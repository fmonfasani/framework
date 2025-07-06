"""
Protocolo MCP - Multi-agent Communication Protocol
"""

import asyncio
import json
import logging
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import threading
from queue import Queue, Empty

from genesis_engine.mcp.message_types import (
    MCPMessage, MCPRequest, MCPResponse, MCPBroadcast, MCPError,
    MessageType, Priority
)
from enum import Enum

logger = logging.getLogger(__name__)


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
        self.message_queue: Queue = Queue()
        self.response_handlers: Dict[str, Callable] = {}
        self.broadcast_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
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
    
    def start(self):
        """Iniciar el protocolo MCP"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._message_worker, daemon=True)
        self.worker_thread.start()
        logger.info("Protocolo MCP iniciado")
    
    def stop(self):
        """Detener el protocolo MCP"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Protocolo MCP detenido")
    
    def send_request(
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
        
        return self._send_and_wait_response(request)
    
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
        
        self.message_queue.put(response)
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
        
        self.message_queue.put(broadcast)
        self.stats["messages_sent"] += 1
    
    def subscribe_to_broadcasts(
        self,
        event: str,
        handler: Callable[[MCPBroadcast], None]
    ):
        """Suscribirse a eventos broadcast"""
        self.broadcast_handlers[event].append(handler)
    
    def _send_and_wait_response(self, request: MCPRequest) -> MCPResponse:
        """Enviar solicitud y esperar respuesta"""
        response_event = threading.Event()
        response_data = {}
        
        def response_handler(response: MCPResponse):
            response_data['response'] = response
            response_event.set()
        
        # Registrar handler para la respuesta
        self.response_handlers[request.id] = response_handler
        
        try:
            # Enviar solicitud
            self.message_queue.put(request)
            self.stats["messages_sent"] += 1
            
            # Esperar respuesta
            if response_event.wait(timeout=request.timeout):
                return response_data['response']
            else:
                # Timeout
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
    
    def _message_worker(self):
        """Worker thread para procesar mensajes"""
        while self.running:
            try:
                # Obtener mensaje de la cola
                message = self.message_queue.get(timeout=1)
                self.stats["messages_received"] += 1
                
                # Procesar según tipo de mensaje
                if isinstance(message, MCPRequest):
                    self._handle_request(message)
                elif isinstance(message, MCPResponse):
                    self._handle_response(message)
                elif isinstance(message, MCPBroadcast):
                    self._handle_broadcast(message)
                elif isinstance(message, MCPError):
                    self._handle_error(message)
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                self.stats["errors"] += 1
    
    def _handle_request(self, request: MCPRequest):
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
            self.message_queue.put(error_response)
            return
        
        try:
            # Ejecutar acción en el agente
            start_time = datetime.now()
            result = target_agent.handle_request(request)
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
            self.message_queue.put(response)
            
        except Exception as e:
            # Error al ejecutar
            logger.error(f"Error ejecutando {request.action} en {request.target_agent}: {e}")
            error_response = MCPResponse(
                sender_agent=request.target_agent,
                target_agent=request.sender_agent,
                correlation_id=request.id,
                success=False,
                error_message=str(e),
                data={}
            )
            self.message_queue.put(error_response)
    
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
            except Exception as e:
                logger.error(f"Error en handler de broadcast: {e}")
    
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
