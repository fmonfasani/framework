from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Callable, Union
from abc import abstractmethod

from mcpturbo_agents import BaseAgent, AgentConfig, AgentType
from genesis_engine.tasking import AgentTask, TaskResult, TaskStatus

logger = logging.getLogger(__name__)

class GenesisAgent(BaseAgent):
    """Compatibility layer over mcpturbo BaseAgent."""

    def __init__(self, agent_id: str, name: str, agent_type: str = "generic"):
        config = AgentConfig(agent_id=agent_id, name=name, agent_type=AgentType.LOCAL)
        super().__init__(config)
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.version = "1.0.0"
        self.metadata: Dict[str, Any] = {}
        self._register_core_handlers()

    def _register_core_handlers(self) -> None:
        self.register_handler("task.execute", self._handle_task_execute)
        self.register_handler("ping", self._handle_ping)
        self.register_handler("status", self._handle_status)
        self.register_handler("capabilities", self._handle_capabilities)
        self.register_handler("health", self._handle_health)

    async def handle_request(self, request) -> Dict[str, Any]:
        try:
            action = getattr(request, "action", None)
            if not action:
                raise ValueError("Request sin action especificada")
            if action not in self.handlers:
                raise ValueError(f"Handler not found for action '{action}'")
            handler = self.handlers[action]
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request)
            else:
                result = handler(request)
            return result
        except Exception as e:  # pragma: no cover - defensive
            logger.error("Error manejando request %s: %s", action, e)
            return {"success": False, "error": str(e), "agent_id": self.agent_id}

    async def _handle_task_execute(self, request) -> Dict[str, Any]:
        try:
            data = getattr(request, "data", {})
            task = AgentTask(
                id=data.get("task_id", str(uuid.uuid4())),
                name=data.get("name", "unknown_task"),
                description=data.get("description", ""),
                params=data.get("params", {}),
                priority=data.get("priority", 2),
            )
            task.start()
            start_time = datetime.utcnow()
            result = await self.execute_task(task)
            end_time = datetime.utcnow()
            exec_time = (end_time - start_time).total_seconds()
            if isinstance(result, TaskResult):
                task_result = result
                task_result.execution_time = exec_time
            else:
                task_result = TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result,
                    execution_time=exec_time,
                )
            if task_result.success:
                task.complete()
            else:
                task.fail()
            return task_result.to_dict()
        except Exception as e:  # pragma: no cover - defensive
            logger.error("Error ejecutando task.execute: %s", e)
            return {"task_id": data.get("task_id", "unknown"), "success": False, "error": str(e), "execution_time": None}

    async def _handle_ping(self, request) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "timestamp": datetime.utcnow().isoformat(),
            "pong": True,
        }

    async def _handle_status(self, request) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "version": self.version,
            "handlers": list(self.handlers.keys()),
        }

    async def _handle_capabilities(self, request) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "handlers": list(self.handlers.keys()),
        }

    async def _handle_health(self, request) -> Dict[str, Any]:
        return {
            "success": True,
            "agent_id": self.agent_id,
            "healthy": self.status == "running",
            "status": self.status,
            "uptime": getattr(self, "_start_time", None),
        }

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Union[TaskResult, Any]:
        pass
