"""Simplified orchestrator built on MCPturbo primitives.

This module exposes :class:`CoreOrchestrator` with a single public coroutine
:meth:`execute_project_generation` that builds a workflow and delegates to agents
registered in the MCPturbo orchestrator. The orchestrator itself performs no
business logic or code generation; it simply wires up workflow steps and
executes them using MCPturbo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    # Attempt to import real MCPturbo primitives
    from mcpturbo.orchestrator import Orchestrator as MCPOrchestrator
    from mcpturbo.workflow import Workflow, Step
except Exception:  # pragma: no cover - fallback stubs for tests
    class Step:  # type: ignore
        def __init__(self, id: str, agent: str, task: str, params: Dict[str, Any] | None = None):
            self.id = id
            self.agent = agent
            self.task = task
            self.params = params or {}

    class Workflow:  # type: ignore
        def __init__(self, name: str):
            self.name = name
            self.steps: List[Step] = []

        def add_step(self, step: Step) -> None:
            self.steps.append(step)

    class MCPOrchestrator:  # type: ignore
        async def run_workflow(self, workflow: Workflow) -> Dict[str, Any]:
            # This stub simply returns a success result including step information
            return {"success": True, "steps": [s.id for s in workflow.steps]}


@dataclass
class ProjectGenerationRequest:
    """Request information to generate a project."""

    name: str
    template: str
    features: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectGenerationResult:
    """Result returned by :meth:`execute_project_generation`."""

    success: bool
    data: Dict[str, Any] = field(default_factory=dict)


class CoreOrchestrator:
    """Builds workflows and delegates execution to MCPturbo."""

    def __init__(self) -> None:
        self._engine = MCPOrchestrator()

    async def execute_project_generation(self, request: ProjectGenerationRequest) -> ProjectGenerationResult:
        """Create and run a workflow to generate a project."""

        workflow = Workflow(name=request.name)
        step = Step(
            id="generate_project",
            agent="architect_agent",
            task="design_architecture",
            params={
                "template": request.template,
                "features": request.features,
                **request.options,
            },
        )
        workflow.add_step(step)

        result = await self._engine.run_workflow(workflow)
        return ProjectGenerationResult(success=result.get("success", False), data=result)
