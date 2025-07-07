
"""
Genesis Generate Command
"""

import asyncio
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel

from genesis_engine.agents.backend import BackendAgent
from genesis_engine.agents.devops import DevOpsAgent
from genesis_engine.agents.frontend import FrontendAgent
from genesis_engine.mcp.agent_base import AgentTask

console = Console()


def _select_agent(component: str, explicit: str | None) -> tuple[type, str]:
    """Return agent class and task name based on component."""
    mapping = {
        "model": (BackendAgent, "generate_models"),
        "endpoint": (BackendAgent, "generate_api"),
        "page": (FrontendAgent, "generate_frontend"),
        "component": (FrontendAgent, "generate_frontend"),
        "k8s": (DevOpsAgent, "generate_k8s"),
    }

    if explicit:
        agent_map = {
            "backend": BackendAgent,
            "frontend": FrontendAgent,
            "devops": DevOpsAgent,
        }
        cls = agent_map.get(explicit)
        if not cls:
            raise ValueError(f"Agente desconocido: {explicit}")
        task = mapping.get(component, (None, f"generate_{component}"))[1]
        return cls, task

    if component not in mapping:
        raise ValueError(f"Componente desconocido: {component}")
    return mapping[component]


def generate_command(component: str, name: str, agent: str | None, interactive: bool):
    """Comando de generación de componentes."""

    console.print(
        Panel.fit(
            f"[bold cyan]⚡ Generando {component}: {name}[/bold cyan]",
            border_style="cyan",
        )
    )

    try:
        agent_cls, task_name = _select_agent(component, agent)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        return

    async def _run_generate():
        inst = agent_cls()
        await inst.initialize()
        task = AgentTask(
            id=str(uuid4()),
            name=task_name,
            params={"name": name, "interactive": interactive},
        )
        return await inst.execute_task(task)

    result = asyncio.run(_run_generate())

    if isinstance(result, dict) and result.get("generated_files"):
        console.print("[green]✅ Generación completada[/green]")
        for f in result["generated_files"]:
            console.print(f"📄 {f}")
    else:
        console.print("[yellow]⚠️ Generación finalizó sin archivos" )
