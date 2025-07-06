"""
Tipos de mensajes para el protocolo MCP
"""

from enum import Enum
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class MessageType(str, Enum):
    """Tipos de mensajes MCP"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    SHUTDOWN = "shutdown"

class Priority(str, Enum):
    """Prioridades de mensajes"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class MCPMessage(BaseModel):
    """Mensaje base del protocolo MCP"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    sender_agent: str
    target_agent: Optional[str] = None  # None para broadcasts
    priority: Priority = Priority.NORMAL
    data: Dict[str, Any]
    correlation_id: Optional[str] = None  # Para relacionar request/response
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MCPRequest(MCPMessage):
    """Mensaje de solicitud"""
    type: MessageType = MessageType.REQUEST
    action: str
    timeout: Optional[int] = 30  # segundos
    retry_count: int = 0

class MCPResponse(MCPMessage):
    """Mensaje de respuesta"""
    type: MessageType = MessageType.RESPONSE
    success: bool
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

class MCPBroadcast(MCPMessage):
    """Mensaje de difusión"""
    type: MessageType = MessageType.BROADCAST
    event: str
    scope: str = "all"  # all, backend, frontend, devops, etc.

class MCPError(MCPMessage):
    """Mensaje de error"""
    type: MessageType = MessageType.ERROR
    error_code: str
    error_message: str
    stack_trace: Optional[str] = None   