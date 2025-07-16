from __future__ import annotations

import asyncio
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from mcpturbo_agents import GenesisAgent, AgentConfig, AgentType

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 2
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def start(self) -> None:
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self) -> None:
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self) -> None:
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()

@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }

class SimpleAgent(GenesisAgent):
    """Simple agent used for testing."""

    def __init__(self, agent_id: str, name: str, agent_type: str = "simple"):
        config = AgentConfig(agent_id=agent_id, name=name, agent_type=AgentType.LOCAL)
        super().__init__(config)
        self.add_capability(
            AgentConfig(agent_id=agent_id, name=name, agent_type=AgentType.LOCAL)
        )

    async def execute_task(self, task: AgentTask) -> TaskResult:
        await asyncio.sleep(0.1)
        return TaskResult(
            task_id=task.id,
            success=True,
            result={
                "message": f"Tarea {task.name} completada por {self.config.name}",
                "task_name": task.name,
                "agent": self.config.name,
                "params": task.params,
            },
        )

def create_simple_agent(agent_id: str, name: str | None = None) -> SimpleAgent:
    if name is None:
        name = agent_id.replace("_", " ").title()
    return SimpleAgent(agent_id, name)

def validate_agent_implementation(agent: GenesisAgent) -> bool:
    required_handlers = ["task.execute", "ping", "status"]
    for handler in required_handlers:
        if handler not in getattr(agent, "handlers", {}):
            logger.error("Agente %s falta handler: %s", getattr(agent, "name", ""), handler)
            return False
    if not hasattr(agent, "execute_task"):
        logger.error("Agente %s falta método execute_task", getattr(agent, "name", ""))
        return False
    return True
