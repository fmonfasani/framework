"""
Genesis Deploy Command
"""

from rich.console import Console
from rich.panel import Panel

console = Console()

def deploy_command(environment: str, force: bool, auto_migrate: bool):
    """Comando de despliegue"""
    console.print(Panel.fit(
        f"[bold cyan]🚀 Desplegando en {environment}[/bold cyan]",
        border_style="cyan"
    ))
    console.print("[yellow]🚧 Función en desarrollo[/yellow]")
