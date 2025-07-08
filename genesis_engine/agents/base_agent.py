"""
Agente base para todos los agentes especializados
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from genesis_engine.mcp.message_types import MCPRequest, MCPResponse

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Clase base para todos los agentes especializados.
    
    Todos los agentes heredan de esta clase y implementan
    la comunicación vía protocolo MCP.
    """
    
    # Debe ser definido por cada agente
    agent_type: str = "base"
    
    def __init__(self, name: str = None, version: str = "1.0.0"):
        self.agent_id = f"{self.agent_type}_{uuid.uuid4().hex[:8]}"
        self.name = name or f"{self.agent_type.title()}Agent"
        self.version = version
        self.created_at = datetime.now()
        self.status = "initialized"
        self.capabilities: List[str] = []
        self.mcp_protocol = None
        self.logger = logging.getLogger(f"genesis.agents.{self.agent_type}")
    
    def set_mcp_protocol(self, protocol):
        """Configurar protocolo MCP"""
        self.mcp_protocol = protocol
        self.status = "ready"
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retornar lista de capacidades del agente"""
        pass
    
    @abstractmethod
    async def handle_request(self, request: MCPRequest) -> Dict[str, Any]:
        """
        Manejar solicitud entrante vía MCP

        Args:
            request: Solicitud MCP

        Returns:
            Dict con resultado de la operación
        """
        pass
    
    async def send_request(
        self,
        target_agent: str,
        action: str,
        data: Dict[str, Any],
        timeout: int = 30
    ) -> MCPResponse:
        """Enviar solicitud a otro agente"""
        if not self.mcp_protocol:
            raise RuntimeError("Protocolo MCP no configurado")

        return await self.mcp_protocol.send_request(
            sender_id=self.agent_id,
            target_id=target_agent,
            action=action,
            data=data,
            timeout=timeout
        )
    
    def broadcast_event(
        self,
        event: str,
        data: Dict[str, Any],
        scope: str = "all"
    ):
        """Enviar evento broadcast"""
        if not self.mcp_protocol:
            raise RuntimeError("Protocolo MCP no configurado")
        
        self.mcp_protocol.broadcast(
            sender_id=self.agent_id,
            event=event,
            data=data,
            scope=scope
        )
    
    def log_action(self, action: str, data: Dict[str, Any] = None):
        """Registrar acción en logs"""
        self.logger.info(f"Acción: {action}", extra={"data": data})
    
    def get_info(self) -> Dict[str, Any]:
        """Obtener información del agente"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat()
        }