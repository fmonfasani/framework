"""
Tipos de mensajes para el protocolo MCP (Multi-agent Communication Protocol).
"""

from typing import Any, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Tipos de mensajes MCP"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"
    NOTIFICATION = "notification"


class Priority(int, Enum):
    """Prioridades de mensajes"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MCPMessage:
    """Mensaje base del protocolo MCP - ESTRUCTURA CORREGIDA"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.REQUEST
    sender: str = ""
    sender_agent: str = ""
    recipient: str = ""
    action: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "sender_agent": self.sender_agent,
            "recipient": self.recipient,
            "action": self.action,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }

@dataclass
class MCPResponse:
    """Respuesta del protocolo MCP"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.RESPONSE
    success: bool = True
    result: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

    sender_agent: str = ""
    target_agent: str = ""
    correlation_id: str = ""
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    data: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "success": self.success,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
            "sender_agent": self.sender_agent,
            "target_agent": self.target_agent,
            "correlation_id": self.correlation_id,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "data": self.data,
            "priority": self.priority,
        }

class MCPRequest(BaseModel):
    """Solicitud MCP"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = Field(default=MessageType.REQUEST)
    sender_agent: str = Field(description="Agente que envía")
    target_agent: str = Field(description="Agente destinatario")
    action: str = Field(description="Acción a ejecutar")
    data: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=30)
    priority: Priority = Field(default=Priority.NORMAL)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPBroadcast(BaseModel):
    """Mensaje de broadcast para múltiples agentes."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único del broadcast")
    type: MessageType = Field(default=MessageType.BROADCAST)
    sender: str = Field(description="ID del agente remitente")
    sender_agent: str = Field(description="Nombre del agente remitente")
    event: str = Field(description="Evento a broadcast")
    data: Dict[str, Any] = Field(default_factory=dict, description="Datos del mensaje")
    recipients: Optional[list[str]] = Field(default=None, description="Lista de destinatarios")
    scope: str = Field(default="all", description="Alcance del broadcast")
    priority: Priority = Field(default=Priority.NORMAL)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPError(BaseModel):
    """Mensaje de error MCP."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único del error")
    type: MessageType = Field(default=MessageType.ERROR)
    original_id: Optional[str] = Field(description="ID del mensaje que causó el error")
    sender: str = Field(description="ID del agente que reporta el error")
    sender_agent: str = Field(description="Nombre del agente que reporta el error")
    error_code: str = Field(description="Código de error")
    error_message: str = Field(description="Mensaje de error")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detalles adicionales")
    priority: Priority = Field(default=Priority.NORMAL)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }