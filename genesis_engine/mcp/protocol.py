"""
Protocolo MCP - Multi-agent Communication Protocol

Protocolo robusto para comunicación entre agentes con:
- Validación de mensajes
- Serialización/deserialización segura
- Circuit breakers
- Retry logic
- Rate limiting
- Logging estructurado
- Métricas de performance
"""

import asyncio
import json
import logging
import weakref
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Callable, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, is_dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import hashlib
import uuid
import inspect

from genesis_engine.mcp.message_types import (
    MCPMessage, MCPRequest, MCPResponse, MCPBroadcast, MCPError,
    MessageType, Priority
)
from genesis_engine.core.logging import get_logger

logger = get_logger(__name__)

class ConnectionState(str, Enum):
    """Estados de conexión"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"

class CircuitBreakerState(str, Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class MessageValidationResult:
    """Resultado de validación de mensaje"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class RateLimitBucket:
    """Bucket para rate limiting"""
    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float  # tokens por segundo

@dataclass
class CircuitBreaker:
    """Circuit breaker para proteger contra agentes fallidos"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    half_open_max_requests: int = 3
    half_open_requests: int = 0
    
    def should_allow_request(self) -> bool:
        """Verificar si se debe permitir la solicitud"""
        now = datetime.utcnow()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and \
               now - self.last_failure_time >= timedelta(seconds=self.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_requests = 0
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return self.half_open_requests < self.half_open_max_requests
        return False
    
    def record_success(self):
        """Registrar éxito"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_requests = 0
    
    def record_failure(self):
        """Registrar fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
    
    def record_request(self):
        """Registrar solicitud en estado half-open"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_requests += 1

@dataclass
class RetryConfig:
    """Configuración de retry"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_errors: Set[str] = field(default_factory=lambda: {
        "timeout", "connection_error", "temporary_failure"
    })

@dataclass
class ConnectionInfo:
    """Información de conexión"""
    agent_id: str
    connection_id: str
    state: ConnectionState
    last_seen: datetime
    message_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0

class MCPMessageValidator:
    """Validador de mensajes MCP"""
    
    @staticmethod
    def validate_message(message: MCPMessage) -> MessageValidationResult:
        """Validar mensaje MCP"""
        errors = []
        warnings = []
        
        # Validar campos requeridos
        if not hasattr(message, 'id') or not message.id:
            errors.append("Campo 'id' requerido")
        
        if not hasattr(message, 'type') or not message.type:
            errors.append("Campo 'type' requerido")
        
        if not hasattr(message, 'timestamp') or not message.timestamp:
            errors.append("Campo 'timestamp' requerido")
        
        # Validar formato de ID
        if hasattr(message, 'id') and message.id:
            try:
                uuid.UUID(message.id)
            except ValueError:
                errors.append("Formato de ID inválido")
        
        # Validar timestamp
        if hasattr(message, 'timestamp') and message.timestamp:
            try:
                if isinstance(message.timestamp, str):
                    datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
                elif not isinstance(message.timestamp, datetime):
                    errors.append("Timestamp debe ser datetime o string ISO")
            except ValueError:
                errors.append("Formato de timestamp inválido")
        
        # Validar prioridad
        if hasattr(message, 'priority') and message.priority:
            if not isinstance(message.priority, Priority):
                errors.append("Prioridad inválida")
        
        # Validación específica por tipo
        if isinstance(message, MCPRequest):
            if not message.sender_agent:
                errors.append("Campo 'sender_agent' requerido en request")
            if not message.target_agent:
                errors.append("Campo 'target_agent' requerido en request")
            if not message.action:
                errors.append("Campo 'action' requerido en request")
        
        elif isinstance(message, MCPResponse):
            if not message.sender_agent:
                errors.append("Campo 'sender_agent' requerido en response")
            if not message.target_agent:
                errors.append("Campo 'target_agent' requerido en response")
            if not message.correlation_id:
                errors.append("Campo 'correlation_id' requerido en response")
        
        elif isinstance(message, MCPBroadcast):
            if not message.sender_agent:
                errors.append("Campo 'sender_agent' requerido en broadcast")
            if not message.event:
                errors.append("Campo 'event' requerido en broadcast")
        
        # Validar tamaño del payload
        if hasattr(message, 'data') and message.data:
            try:
                serialized = json.dumps(message.data)
                if len(serialized) > 1024 * 1024:  # 1MB
                    warnings.append("Payload muy grande (>1MB)")
            except (TypeError, ValueError):
                errors.append("Payload no serializable")
        
        return MessageValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

class MCPMessageSerializer:
    """Serializador de mensajes MCP"""
    
    @staticmethod
    def serialize(message: MCPMessage) -> bytes:
        """Serializar mensaje a bytes"""
        try:
            # Convertir a diccionario
            data = {
                "id": message.id,
                "type": message.type.value if hasattr(message.type, 'value') else str(message.type),
                "timestamp": message.timestamp.isoformat() if isinstance(message.timestamp, datetime) else message.timestamp,
                "priority": message.priority.value if hasattr(message.priority, 'value') else str(message.priority)
            }
            
            # Agregar campos específicos
            if isinstance(message, MCPRequest):
                data.update({
                    "sender_agent": message.sender_agent,
                    "target_agent": message.target_agent,
                    "action": message.action,
                    "data": message.data,
                    "timeout": message.timeout
                })
            elif isinstance(message, MCPResponse):
                data.update({
                    "sender_agent": message.sender_agent,
                    "target_agent": message.target_agent,
                    "correlation_id": message.correlation_id,
                    "success": message.success,
                    "result": message.result,
                    "error_message": message.error_message,
                    "execution_time": message.execution_time,
                    "data": message.data
                })
            elif isinstance(message, MCPBroadcast):
                data.update({
                    "sender_agent": message.sender_agent,
                    "event": message.event,
                    "data": message.data,
                    "scope": message.scope
                })
            elif isinstance(message, MCPError):
                data.update({
                    "error_code": message.error_code,
                    "error_message": message.error_message,
                    "details": message.details
                })
            
            # Serializar a JSON y luego a bytes
            json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            return json_str.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error serializando mensaje: {e}")
            raise ValueError(f"Error en serialización: {e}")
    
    @staticmethod
    def deserialize(data: bytes) -> MCPMessage:
        """Deserializar bytes a mensaje"""
        try:
            # Decodificar y parsear JSON
            json_str = data.decode('utf-8')
            obj = json.loads(json_str)
            
            # Convertir timestamp
            if 'timestamp' in obj:
                if isinstance(obj['timestamp'], str):
                    obj['timestamp'] = datetime.fromisoformat(obj['timestamp'].replace('Z', '+00:00'))
            
            # Convertir prioridad
            if 'priority' in obj:
                if isinstance(obj['priority'], str):
                    obj['priority'] = Priority(obj['priority'])
            
            # Crear mensaje según tipo
            msg_type = obj.get('type')
            
            if msg_type == 'request':
                return MCPRequest(
                    id=obj['id'],
                    sender_agent=obj['sender_agent'],
                    target_agent=obj['target_agent'],
                    action=obj['action'],
                    data=obj.get('data', {}),
                    timeout=obj.get('timeout', 30),
                    priority=obj.get('priority', Priority.NORMAL),
                    timestamp=obj.get('timestamp')
                )
            elif msg_type == 'response':
                return MCPResponse(
                    id=obj['id'],
                    sender_agent=obj['sender_agent'],
                    target_agent=obj['target_agent'],
                    correlation_id=obj['correlation_id'],
                    success=obj.get('success', False),
                    result=obj.get('result'),
                    error_message=obj.get('error_message'),
                    execution_time=obj.get('execution_time'),
                    data=obj.get('data', {}),
                    priority=obj.get('priority', Priority.NORMAL),
                    timestamp=obj.get('timestamp')
                )
            elif msg_type == 'broadcast':
                return MCPBroadcast(
                    id=obj['id'],
                    sender_agent=obj['sender_agent'],
                    event=obj['event'],
                    data=obj.get('data', {}),
                    scope=obj.get('scope', 'all'),
                    priority=obj.get('priority', Priority.NORMAL),
                    timestamp=obj.get('timestamp')
                )
            elif msg_type == 'error':
                return MCPError(
                    id=obj['id'],
                    error_code=obj['error_code'],
                    error_message=obj['error_message'],
                    details=obj.get('details', {}),
                    priority=obj.get('priority', Priority.NORMAL),
                    timestamp=obj.get('timestamp')
                )
            else:
                raise ValueError(f"Tipo de mensaje desconocido: {msg_type}")
                
        except Exception as e:
            logger.error(f"Error deserializando mensaje: {e}")
            raise ValueError(f"Error en deserialización: {e}")

class MCPConnectionManager:
    """Gestor de conexiones MCP mejorado"""

    def __init__(self, max_connections: int = 100):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.connection_refs: weakref.WeakSet = weakref.WeakSet()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.max_connections = max_connections
        self.lock = asyncio.Lock()
        self.logger = get_logger(f"{__name__}.connection_manager")

    async def register_connection(self, agent_id: str, connection: Any) -> str:
        """Registrar una nueva conexión"""
        async with self.lock:
            if len(self.connections) >= self.max_connections:
                raise ValueError(f"Máximo de conexiones alcanzado: {self.max_connections}")
            
            connection_id = str(uuid.uuid4())
            
            self.connections[connection_id] = ConnectionInfo(
                agent_id=agent_id,
                connection_id=connection_id,
                state=ConnectionState.CONNECTED,
                last_seen=datetime.utcnow()
            )
            
            self.connection_refs.add(connection)
            
            self.logger.info(f"Conexión registrada: {agent_id} -> {connection_id}")
            return connection_id

    async def unregister_connection(self, connection_id: str):
        """Desregistrar conexión"""
        async with self.lock:
            if connection_id in self.connections:
                agent_id = self.connections[connection_id].agent_id
                del self.connections[connection_id]
                self.logger.info(f"Conexión desregistrada: {agent_id} -> {connection_id}")

    async def update_connection_stats(self, connection_id: str, response_time: float):
        """Actualizar estadísticas de conexión"""
        async with self.lock:
            if connection_id in self.connections:
                conn = self.connections[connection_id]
                conn.message_count += 1
                conn.last_seen = datetime.utcnow()
                
                # Calcular promedio móvil
                if conn.avg_response_time == 0:
                    conn.avg_response_time = response_time
                else:
                    conn.avg_response_time = (conn.avg_response_time * 0.9) + (response_time * 0.1)

    async def broadcast_to_all(self, message: MCPMessage, exclude_agent: Optional[str] = None):
        """Enviar un mensaje a todas las conexiones registradas"""
        serialized = MCPMessageSerializer.serialize(message)
        
        for conn_info in list(self.connections.values()):
            if exclude_agent and conn_info.agent_id == exclude_agent:
                continue
                
            try:
                # Buscar conexión activa
                for conn in list(self.connection_refs):
                    if hasattr(conn, 'agent_id') and conn.agent_id == conn_info.agent_id:
                        asyncio.create_task(self._safe_send(conn, serialized))
                        break
                        
            except Exception as e:
                self.logger.warning(f"Error enviando broadcast a {conn_info.agent_id}: {e}")
                await self._handle_connection_error(conn_info.connection_id)

    async def _safe_send(self, connection: Any, message: bytes):
        """Enviar mensaje de forma segura"""
        try:
            if hasattr(connection, 'send'):
                await connection.send(message)
            else:
                self.logger.warning(f"Conexión sin método send: {connection}")
        except Exception as e:
            self.logger.error(f"Error enviando mensaje: {e}")

    async def _handle_connection_error(self, connection_id: str):
        """Manejar error de conexión"""
        async with self.lock:
            if connection_id in self.connections:
                conn = self.connections[connection_id]
                conn.error_count += 1
                conn.state = ConnectionState.FAILED
                
                # Desconectar si hay demasiados errores
                if conn.error_count > 5:
                    await self.unregister_connection(connection_id)

    async def get_connection_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de conexiones"""
        async with self.lock:
            return {
                "total_connections": len(self.connections),
                "by_agent": {
                    conn.agent_id: {
                        "state": conn.state.value,
                        "message_count": conn.message_count,
                        "error_count": conn.error_count,
                        "avg_response_time": conn.avg_response_time,
                        "last_seen": conn.last_seen.isoformat()
                    }
                    for conn in self.connections.values()
                },
                "max_connections": self.max_connections
            }

    async def cleanup(self):
        """Liberar recursos del gestor de conexiones"""
        async with self.lock:
            self.connections.clear()
            self.executor.shutdown(wait=True)

class MCPProtocol:
    """
    Protocolo de comunicación entre agentes (MCP) mejorado
    
    Características:
    - Validación de mensajes
    - Circuit breakers
    - Rate limiting
    - Retry logic
    - Métricas de performance
    - Logging estructurado
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.response_handlers: Dict[str, Callable] = {}
        self.broadcast_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        self.circuit_task: Optional[asyncio.Task] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None       

        # Componentes mejorados
        self.validator = MCPMessageValidator()
        self.serializer = MCPMessageSerializer()
        self.connection_manager = MCPConnectionManager()
        
        # Circuit breakers por agente
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Rate limiting
        self.rate_limit_buckets: Dict[str, RateLimitBucket] = {}
        self.default_rate_limit = 100  # requests por segundo
        
        # Retry configurations
        self.retry_configs: Dict[str, RetryConfig] = {}
        
        # Métricas
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_validated": 0,
            "validation_errors": 0,
            "errors": 0,
            "timeouts": 0,
            "circuit_breaker_trips": 0,
            "rate_limit_hits": 0,
            "retries": 0,
            "avg_response_time": 0.0,
            "peak_queue_size": 0
        }
        
        # Historial de métricas
        self.metrics_history: deque = deque(maxlen=1000)
        
        # Logger
        self.logger = get_logger(f"{__name__}.protocol")
    
    def register_agent(self, agent: 'BaseAgent'):
        """Registrar un agente en el protocolo"""
        self.agents[agent.agent_id] = agent
        
        # Configurar circuit breaker
        self.circuit_breakers[agent.agent_id] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        
        # Configurar rate limiting
        self.rate_limit_buckets[agent.agent_id] = RateLimitBucket(
            capacity=self.default_rate_limit,
            tokens=self.default_rate_limit,
            last_refill=time.time(),
            refill_rate=self.default_rate_limit
        )
        
        # Configurar retry
        self.retry_configs[agent.agent_id] = RetryConfig()
        
        self.logger.info(f"Agente registrado: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Desregistrar un agente"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.circuit_breakers.pop(agent_id, None)
            self.rate_limit_buckets.pop(agent_id, None)
            self.retry_configs.pop(agent_id, None)
            self.logger.info(f"Agente desregistrado: {agent_id}")
    
    def register_handler(self, event: str, handler: Callable):
        """Registrar handler para eventos"""
        self.broadcast_handlers[event].append(handler)
        self.logger.debug(f"Handler registrado para evento: {event}")
    
    def unregister_handler(self, event: str, handler: Callable):
        """Desregistrar handler"""
        if event in self.broadcast_handlers:
            try:
                self.broadcast_handlers[event].remove(handler)
            except ValueError:
                pass
    
    async def start(self):
        """Iniciar el protocolo MCP"""
        if self.running:
            return

        self.running = True
        self.event_loop = asyncio.get_event_loop()
        self.logger.info("MCP Protocol iniciado")
        self.worker_task = asyncio.create_task(self._message_worker())

        # Iniciar tareas de mantenimiento y almacenarlas
        self.metrics_task = asyncio.create_task(self._metrics_collector())
        self.circuit_task = asyncio.create_task(self._circuit_breaker_monitor())
        
        self.logger.info("Protocolo MCP iniciado")

    async def stop(self):
        """Detener el protocolo MCP"""

        if not self.running:
            return
        self.running = False
        
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

        for task in (self.metrics_task, self.circuit_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        await self.connection_manager.cleanup()
        self.logger.info("Protocolo MCP detenido")
    
    def _check_rate_limit(self, agent_id: str) -> bool:
        """Verificar rate limit para un agente"""
        if agent_id not in self.rate_limit_buckets:
            return True
        
        bucket = self.rate_limit_buckets[agent_id]
        now = time.time()
        
        # Rellenar bucket
        time_passed = now - bucket.last_refill
        bucket.tokens = min(
            bucket.capacity,
            bucket.tokens + (time_passed * bucket.refill_rate)
        )
        bucket.last_refill = now
        
        # Verificar si hay tokens disponibles
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        
        self.stats["rate_limit_hits"] += 1
        return False
    
    # MÉTODO CORREGIDO: Compatibilidad con tests
    async def send_request(
        self,
        sender: str,
        recipient: str,
        action: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        priority: Priority = Priority.NORMAL,
        retry_config: Optional[RetryConfig] = None
    ) -> MCPResponse:
        """
        Método de compatibilidad para tests.
        Enviar una solicitud a un agente específico.
        
        Args:
            sender: ID del agente remitente
            recipient: ID del agente destinatario
            action: Acción a ejecutar
            data: Datos opcionales
            timeout: Timeout en segundos
            priority: Prioridad del mensaje
            retry_config: Configuración de retry
            
        Returns:
            Respuesta del agente
        """
        return await self.send_request_advanced(
            sender_id=sender,
            target_id=recipient,
            action=action,
            data=data or {},
            timeout=timeout,
            priority=priority,
            retry_config=retry_config
        )
    
    async def send_request_advanced(
        self,
        sender_id: str,
        target_id: str,
        action: str,
        data: Dict[str, Any],
        timeout: int = 30,
        priority: Priority = Priority.NORMAL,
        retry_config: Optional[RetryConfig] = None
    ) -> MCPResponse:
        """
        Enviar una solicitud a un agente específico con retry logic
        """
        # Usar configuración de retry del agente o la proporcionada
        if retry_config is None:
            retry_config = self.retry_configs.get(sender_id, RetryConfig())
        
        last_error = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                # Crear request
                request = MCPRequest(
                    sender_agent=sender_id,
                    target_agent=target_id,
                    action=action,
                    data=data,
                    timeout=timeout,
                    priority=priority
                )
                
                # Intentar envío
                response = await self._send_request_attempt(request)
                
                # Verificar si es un error reintentable
                if not response.success and attempt < retry_config.max_attempts - 1:
                    error_type = self._classify_error(response.error_message)
                    if error_type in retry_config.retryable_errors:
                        self.stats["retries"] += 1
                        
                        # Calcular delay con exponential backoff
                        delay = min(
                            retry_config.initial_delay * (retry_config.exponential_base ** attempt),
                            retry_config.max_delay
                        )
                        
                        if retry_config.jitter:
                            import random
                            delay *= (0.5 + random.random() * 0.5)
                        
                        self.logger.warning(
                            f"Reintentando request {request.id} (intento {attempt + 1}/{retry_config.max_attempts})"
                        )
                        await asyncio.sleep(delay)
                        continue
                
                return response
                
            except Exception as e:
                last_error = e
                if attempt < retry_config.max_attempts - 1:
                    self.stats["retries"] += 1
                    delay = min(
                        retry_config.initial_delay * (retry_config.exponential_base ** attempt),
                        retry_config.max_delay
                    )
                    await asyncio.sleep(delay)
                    continue
                
        # Si llegamos aquí, todos los intentos fallaron
        return MCPResponse(
            sender_agent="mcp_protocol",
            target_agent=sender_id,
            correlation_id=str(uuid.uuid4()),
            success=False,
            error_message=f"Falló después de {retry_config.max_attempts} intentos. Último error: {last_error}",
            data={}
        )
    
    def _classify_error(self, error_message: Optional[str]) -> str:
        """Clasificar tipo de error para retry logic"""
        if not error_message:
            return "unknown"
        
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            return "timeout"
        elif "connection" in error_lower:
            return "connection_error"
        elif "temporary" in error_lower or "try again" in error_lower:
            return "temporary_failure"
        elif "circuit breaker" in error_lower:
            return "circuit_breaker"
        elif "rate limit" in error_lower:
            return "rate_limit"
        else:
            return "unknown"
    
    async def _send_request_attempt(self, request: MCPRequest) -> MCPResponse:
        """Enviar un intento de request"""
        start_time = time.time()
        
        try:
            # Validar mensaje
            validation_result = self.validator.validate_message(request)
            self.stats["messages_validated"] += 1
            
            if not validation_result.is_valid:
                self.stats["validation_errors"] += 1
                self.logger.error(f"Mensaje inválido: {validation_result.errors}")
                return MCPResponse(
                    sender_agent="mcp_protocol",
                    target_agent=request.sender_agent,
                    correlation_id=request.id,
                    success=False,
                    error_message=f"Mensaje inválido: {', '.join(validation_result.errors)}",
                    data={}
                )
            
            # Verificar rate limit
            if not self._check_rate_limit(request.sender_agent):
                return MCPResponse(
                    sender_agent="mcp_protocol",
                    target_agent=request.sender_agent,
                    correlation_id=request.id,
                    success=False,
                    error_message="Rate limit excedido",
                    data={}
                )
            
            # Verificar circuit breaker
            if request.target_agent in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[request.target_agent]
                if not circuit_breaker.should_allow_request():
                    self.stats["circuit_breaker_trips"] += 1
                    return MCPResponse(
                        sender_agent="mcp_protocol",
                        target_agent=request.sender_agent,
                        correlation_id=request.id,
                        success=False,
                        error_message=f"Circuit breaker abierto para {request.target_agent}",
                        data={}
                    )
                circuit_breaker.record_request()
            
            # Enviar request
            response = await self._send_and_wait_response(request)
            
            # Actualizar circuit breaker
            if request.target_agent in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[request.target_agent]
                if response.success:
                    circuit_breaker.record_success()
                else:
                    circuit_breaker.record_failure()
            
            # Actualizar métricas
            response_time = time.time() - start_time
            self._update_response_time_metric(response_time)
            
            return response
            
        except Exception as e:
            # Registrar fallo en circuit breaker
            if request.target_agent in self.circuit_breakers:
                self.circuit_breakers[request.target_agent].record_failure()
            
            self.logger.error(f"Error enviando request: {e}")
            return MCPResponse(
                sender_agent="mcp_protocol",
                target_agent=request.sender_agent,
                correlation_id=request.id,
                success=False,
                error_message=str(e),
                data={}
            )
    
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
        
        # Validar respuesta
        validation_result = self.validator.validate_message(response)
        if not validation_result.is_valid:
            self.logger.error(f"Respuesta inválida: {validation_result.errors}")
            return
        
        try:
            self.message_queue.put_nowait(response)
            self.stats["messages_sent"] += 1
        except asyncio.QueueFull:
            self.logger.error("Cola de mensajes llena")
    
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
        """
        broadcast = MCPBroadcast(
            sender_agent=sender_id,
            event=event,
            data=data,
            scope=scope,
            priority=priority
        )
        
        # Validar broadcast
        validation_result = self.validator.validate_message(broadcast)
        if not validation_result.is_valid:
            self.logger.error(f"Broadcast inválido: {validation_result.errors}")
            return
        
        try:
            self.message_queue.put_nowait(broadcast)
            self.stats["messages_sent"] += 1
        except asyncio.QueueFull:
            self.logger.error("Cola de mensajes llena")
    
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
                # Actualizar métrica de tamaño de cola
                queue_size = self.message_queue.qsize()
                self.stats["peak_queue_size"] = max(self.stats["peak_queue_size"], queue_size)
                
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1)
                self.stats["messages_received"] += 1

                # Procesar mensaje según tipo
                if isinstance(message, MCPRequest):
                    await self._handle_request(message)
                elif isinstance(message, MCPResponse):
                    self._handle_response(message)
                elif isinstance(message, MCPBroadcast):
                    await self._handle_broadcast(message)
                elif isinstance(message, MCPError):
                    self._handle_error(message)
                else:
                    self.logger.warning(f"Tipo de mensaje desconocido: {type(message)}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error procesando mensaje: {e}")
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
            start_time = time.time()

            result = target_agent.handle_request(request)
            if inspect.isawaitable(result):
                result = await result

            # Convertir dataclasses o modelos Pydantic a diccionarios
            if is_dataclass(result):
                result = asdict(result)
            elif hasattr(result, "model_dump"):
                try:
                    result = result.model_dump()
                except Exception:
                    pass

            execution_time = time.time() - start_time
            
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
            

        except Exception as e:
            # Error al ejecutar
            self.logger.error(f"Error ejecutando {request.action} en {request.target_agent}: {e}")
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
    
    async def _handle_broadcast(self, broadcast: MCPBroadcast):
        """Manejar mensaje broadcast"""
        handlers = self.broadcast_handlers.get(broadcast.event, [])
        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(broadcast)
                else:
                    handler(broadcast)
            except Exception as e:
                self.logger.error(f"Error en handler de broadcast {broadcast.event}: {e}")

        # Reenviar a connection manager
        await self.connection_manager.broadcast_to_all(broadcast, exclude_agent=broadcast.sender_agent)
    
    def _handle_error(self, error: MCPError):
        """Manejar mensaje de error"""
        self.logger.error(f"Error MCP: {error.error_code} - {error.error_message}")
        self.stats["errors"] += 1
    
    def _update_response_time_metric(self, response_time: float):
        """Actualizar métrica de tiempo de respuesta"""
        if self.stats["avg_response_time"] == 0:
            self.stats["avg_response_time"] = response_time
        else:
            # Promedio móvil
            self.stats["avg_response_time"] = (self.stats["avg_response_time"] * 0.9) + (response_time * 0.1)
    
    async def _metrics_collector(self):
        """Recolector de métricas en background"""
        while self.running:
            try:
                # Capturar snapshot de métricas
                snapshot = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "stats": dict(self.stats),
                    "queue_size": self.message_queue.qsize(),
                    "agents_count": len(self.agents),
                    "circuit_breakers": {
                        agent_id: {
                            "state": cb.state.value,
                            "failure_count": cb.failure_count
                        }
                        for agent_id, cb in self.circuit_breakers.items()
                    }
                }
                
                self.metrics_history.append(snapshot)
                
                # Resetear métricas incrementales
                self.stats["peak_queue_size"] = 0
                
                await asyncio.sleep(10)  # Recolectar cada 10 segundos
                
            except Exception as e:
                self.logger.error(f"Error en recolector de métricas: {e}")
                await asyncio.sleep(30)
    
    async def _circuit_breaker_monitor(self):
        """Monitor de circuit breakers"""
        while self.running:
            try:
                for agent_id, cb in self.circuit_breakers.items():
                    if cb.state == CircuitBreakerState.OPEN:
                        self.logger.warning(f"Circuit breaker abierto para {agent_id}")
                    elif cb.state == CircuitBreakerState.HALF_OPEN:
                        self.logger.info(f"Circuit breaker en half-open para {agent_id}")
                
                await asyncio.sleep(30)  # Monitorear cada 30 segundos
                
            except Exception as e:
                self.logger.error(f"Error en monitor de circuit breakers: {e}")
                await asyncio.sleep(60)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del protocolo"""
        return {
            **self.stats,
            "agents_registered": len(self.agents),
            "queue_size": self.message_queue.qsize(),
            "queue_max_size": self.message_queue.maxsize,
            "running": self.running,
            "circuit_breakers": {
                agent_id: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None
                }
                for agent_id, cb in self.circuit_breakers.items()
            },
            "rate_limits": {
                agent_id: {
                    "tokens": bucket.tokens,
                    "capacity": bucket.capacity,
                    "refill_rate": bucket.refill_rate
                }
                for agent_id, bucket in self.rate_limit_buckets.items()
            }
        }
    
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de métricas"""
        return list(self.metrics_history)
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un agente"""
        agent = self.agents.get(agent_id)
        if agent:
            return {
                "id": agent.agent_id,
                "name": agent.name,
                "version": getattr(agent, 'version', '1.0.0'),
                "capabilities": getattr(agent, 'capabilities', []),
                "status": getattr(agent, 'status', 'unknown'),
                "circuit_breaker": {
                    "state": self.circuit_breakers.get(agent_id, CircuitBreaker()).state.value,
                    "failure_count": self.circuit_breakers.get(agent_id, CircuitBreaker()).failure_count
                },
                "rate_limit": {
                    "tokens": self.rate_limit_buckets.get(agent_id, RateLimitBucket(0, 0, 0, 0)).tokens,
                    "capacity": self.rate_limit_buckets.get(agent_id, RateLimitBucket(0, 0, 0, 0)).capacity
                }
            }
        return None

# Instancia global del protocolo utilizada por el orquestador
mcp_protocol = MCPProtocol()