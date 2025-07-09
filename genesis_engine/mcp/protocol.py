"""
Protocolo MCP - Multi-agent Communication Protocol
"""

import asyncio
import json
import logging
import weakref
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Callable, Optional, Any
import inspect
from datetime import datetime, timedelta
from collections import defaultdict

from genesis_engine.mcp.message_types import (
    MCPMessage, MCPRequest, MCPResponse, MCPBroadcast, MCPError,
    MessageType, Priority
)
from enum import Enum

logger = logging.getLogger(__name__)


class MCPConnectionManager:
    """Gestor de conexiones MCP"""

    def __init__(self) -> None:
        self.connections: weakref.WeakSet = weakref.WeakSet()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def add_connection(self, conn: Any) -> None:
        """Registrar una nueva conexión."""
        self.connections.add(conn)

    def broadcast_to_all(self, message: Any) -> None:
        """Enviar un mensaje a todas las conexiones registradas."""
        for conn in list(self.connections):
            try:
                asyncio.create_task(conn.send(message))

            except (ConnectionError, OSError, RuntimeError) as exc:  # pragma: no cover - errores de red
                logging.warning(f"Failed to send to connection {conn}: {exc}")


    async def cleanup(self) -> None:
        """Liberar recursos del gestor de conexiones."""
        self.executor.shutdown(wait=True)


class AgentStatus(str, Enum):
    """Estados posibles de un agente."""
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class MCPProtocol:
    """
    Protocolo de comunicación entre agentes (MCP)
    
    Maneja el intercambio de mensajes entre agentes especializados,
    incluyendo routing, timeouts, retry logic y broadcasting.
    """
    
    def __init__(self):
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.response_handlers: Dict[str, Callable] = {}
        self.broadcast_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "timeouts": 0
        }
    
    def register_agent(self, agent: 'BaseAgent'):
        """Registrar un agente en el protocolo"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Agente registrado: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Desregistrar un agente"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agente desregistrado: {agent_id}")
    
    async def start(self):
        """Iniciar el protocolo MCP"""
        if self.running:
            return

        self.running = True
        self.worker_task = asyncio.create_task(self._message_worker())
        logger.info("Protocolo MCP iniciado")

    async def stop(self):
        """Detener el protocolo MCP"""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Protocolo MCP detenido")
    
    async def send_request(
        self,
        sender_id: str,
        target_id: str,
        action: str,
        data: Dict[str, Any],
        timeout: int = 30,
        priority: Priority = Priority.NORMAL
    ) -> MCPResponse:
        """
        Enviar una solicitud a un agente específico
        
        Args:
            sender_id: ID del agente que envía
            target_id: ID del agente destino
            action: Acción a ejecutar
            data: Datos de la solicitud
            timeout: Timeout en segundos
            priority: Prioridad del mensaje
            
        Returns:
            MCPResponse: Respuesta del agente
        """
        request = MCPRequest(
            sender_agent=sender_id,
            target_agent=target_id,
            action=action,
            data=data,
            timeout=timeout,
            priority=priority
        )
        
        return await self._send_and_wait_response(request)
    
    def send_response(
        self,
        request: MCPRequest,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        """Enviar respuesta a una solicitud"""
        response = MCPResponse(
            sender_agent=request.target_agent,
            target_agent=request.sender_agent,
            correlation_id=request.id,
            success=success,
            result=result,
            error_message=error_message,
            execution_time=execution_time,
            data={}
        )
        
        self.message_queue.put_nowait(response)
        self.stats["messages_sent"] += 1
    
    def broadcast(
        self,
        sender_id: str,
        event: str,
        data: Dict[str, Any],
        scope: str = "all",
        priority: Priority = Priority.NORMAL
    ):
        """
        Enviar mensaje broadcast a múltiples agentes
        
        Args:
            sender_id: ID del agente que envía
            event: Tipo de evento
            data: Datos del evento
            scope: Alcance del broadcast (all, backend, frontend, etc.)
            priority: Prioridad del mensaje
        """
        broadcast = MCPBroadcast(
            sender_agent=sender_id,
            event=event,
            data=data,
            scope=scope,
            priority=priority
        )
        
        self.message_queue.put_nowait(broadcast)
        self.stats["messages_sent"] += 1
    
    def subscribe_to_broadcasts(
        self,
        event: str,
        handler: Callable[[MCPBroadcast], None]
    ):
        """Suscribirse a eventos broadcast"""
        self.broadcast_handlers[event].append(handler)
    
    async def _send_and_wait_response(self, request: MCPRequest) -> MCPResponse:
        """Enviar solicitud y esperar respuesta"""
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()

        def response_handler(response: MCPResponse):
            if not future.done():
                future.set_result(response)

        # Registrar handler para la respuesta
        self.response_handlers[request.id] = response_handler

        try:
            # Enviar solicitud
            self.message_queue.put_nowait(request)
            self.stats["messages_sent"] += 1

            try:
                return await asyncio.wait_for(future, timeout=request.timeout)
            except asyncio.TimeoutError:
                self.stats["timeouts"] += 1
                return MCPResponse(
                    sender_agent="mcp_protocol",
                    target_agent=request.sender_agent,
                    correlation_id=request.id,
                    success=False,
                    error_message=f"Timeout después de {request.timeout}s",
                    data={}
                )

        finally:
            # Limpiar handler
            self.response_handlers.pop(request.id, None)
    
    async def _message_worker(self):
        """Tarea asíncrona para procesar mensajes"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1)
                self.stats["messages_received"] += 1

                if isinstance(message, MCPRequest):
                    await self._handle_request(message)
                elif isinstance(message, MCPResponse):
                    self._handle_response(message)
                elif isinstance(message, MCPBroadcast):
                    self._handle_broadcast(message)
                elif isinstance(message, MCPError):
                    self._handle_error(message)

            except asyncio.TimeoutError:
                continue

            except (ValueError, RuntimeError, KeyError, OSError) as e:
                logger.error(f"Error procesando mensaje {message}: {e}")

                self.stats["errors"] += 1
    
    async def _handle_request(self, request: MCPRequest):
        """Manejar solicitud entrante"""
        target_agent = self.agents.get(request.target_agent)
        if not target_agent:
            # Agente no encontrado
            error_response = MCPResponse(
                sender_agent="mcp_protocol",
                target_agent=request.sender_agent,
                correlation_id=request.id,
                success=False,
                error_message=f"Agente {request.target_agent} no encontrado",
                data={}
            )
            self.message_queue.put_nowait(error_response)
            return
        
        try:
            # Ejecutar acción en el agente
            start_time = datetime.now()

            result = target_agent.handle_request(request)
            if inspect.isawaitable(result):
                result = await result

            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Enviar respuesta exitosa
            response = MCPResponse(
                sender_agent=request.target_agent,
                target_agent=request.sender_agent,
                correlation_id=request.id,
                success=True,
                result=result,
                execution_time=execution_time,
                data={}
            )
            self.message_queue.put_nowait(response)
            

        except (AttributeError, ValueError, RuntimeError, KeyError, OSError) as e:

            # Error al ejecutar
            logger.error(
                f"Error ejecutando {request.action} en {request.target_agent}: {e}"
            )
            error_response = MCPResponse(
                sender_agent=request.target_agent,
                target_agent=request.sender_agent,
                correlation_id=request.id,
                success=False,
                error_message=str(e),
                data={}
            )
            self.message_queue.put_nowait(error_response)
    
    def _handle_response(self, response: MCPResponse):
        """Manejar respuesta entrante"""
        handler = self.response_handlers.get(response.correlation_id)
        if handler:
            handler(response)
    
    def _handle_broadcast(self, broadcast: MCPBroadcast):
        """Manejar mensaje broadcast"""
        handlers = self.broadcast_handlers.get(broadcast.event, [])
        for handler in handlers:
            try:
                handler(broadcast)

            except (RuntimeError, ValueError, KeyError) as e:
                logger.error(
                    f"Error en handler de broadcast {broadcast.event}: {e}"
                )

    
    def _handle_error(self, error: MCPError):
        """Manejar mensaje de error"""
        logger.error(f"Error MCP: {error.error_code} - {error.error_message}")
        self.stats["errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del protocolo"""
        return {
            **self.stats,
            "agents_registered": len(self.agents),
            "queue_size": self.message_queue.qsize(),
            "running": self.running
        }
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un agente"""
        agent = self.agents.get(agent_id)
        if agent:
            return {
                "id": agent.agent_id,
                "name": agent.name,
                "version": agent.version,
                "capabilities": agent.capabilities,
                "status": agent.status
            }
        return None


# Instancia global del protocolo utilizada por el orquestador
mcp_protocol = MCPProtocol()
