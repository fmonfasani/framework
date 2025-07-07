"""
Genesis Deploy Command
"""

import asyncio
from pathlib import Path
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel

from genesis_engine.agents.deploy import DeployAgent
from genesis_engine.mcp.agent_base import AgentTask

console = Console()


def deploy_command(environment: str, force: bool, auto_migrate: bool):
    """Comando de despliegue utilizando :class:`DeployAgent`."""

    console.print(
        Panel.fit(
            f"[bold cyan]🚀 Desplegando en {environment}[/bold cyan]",
            border_style="cyan",
        )
    )

    async def _run_deploy():
        agent = DeployAgent()
        await agent.initialize()

        task = AgentTask(
            id=str(uuid4()),
            name="deploy_project",
            params={
                "project_path": str(Path.cwd()),
                "target": "local",
                "environment": environment,
                "force": force,
                "auto_migrate": auto_migrate,
            },
        )
        return await agent.execute_task(task)

    result = asyncio.run(_run_deploy())

    if result.success:
        console.print("[green]✅ Despliegue completado[/green]")
        for url in result.urls:
            console.print(f"🌐 Disponible en: [cyan]{url}[/cyan]")
    else:
        console.print(f"[red]❌ Error en despliegue: {result.error}[/red]")
