from __future__ import annotations
"""Base classes and dataclasses for Genesis agents used by the MCP protocol."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import asyncio
import uuid

from genesis_engine.mcp.message_types import MCPRequest
from genesis_engine.agents.base_agent import BaseAgent

@dataclass
class AgentTask:
    """Representation of a task assigned to an agent."""
    id: str
    name: str
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0

@dataclass
class TaskResult:
    """Result returned by an agent after executing a task."""
    task_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GenesisAgent(BaseAgent):
    """Base class for all Genesis Engine agents."""

    def __init__(self, agent_id: str, name: str, agent_type: str, version: str = "1.0.0"):
        super().__init__(name=name, version=version)
        self.agent_id = agent_id or f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.handlers: Dict[str, Callable] = {}
        self.metadata: Dict[str, Any] = {}

    async def start(self):
        """Initialize the agent."""
        self.status = "running"

    async def stop(self):
        """Stop the agent."""
        self.status = "stopped"

    def add_capability(self, capability: str):
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    def get_capabilities(self) -> list:
        """Retornar capacidades del agente"""
        return list(self.capabilities)
      
    def register_handler(self, action: str, handler: Callable):
        self.handlers[action] = handler

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)


    async def handle_request(self, request: MCPRequest) -> Dict[str, Any]:

        """Dispatch a request to a registered handler."""

        handler = self.handlers.get(request.action)
        if not handler:
            raise ValueError(f"Handler not found for action '{request.action}'")


        if asyncio.iscoroutinefunction(handler):
            return await handler(request.data)

        result = handler(request.data)
        if asyncio.iscoroutine(result):
            # In case the handler returned a coroutine instead of being
            # declared as async, await it using the current loop
            return await result


        return result
