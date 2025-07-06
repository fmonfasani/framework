
"""
Genesis Generate Command
"""

from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_command(component: str, name: str, agent: str, interactive: bool):
    """Comando de generación"""
    console.print(Panel.fit(
        f"[bold cyan]⚡ Generando {component}: {name}[/bold cyan]",
        border_style="cyan"
    ))
    console.print("[yellow]🚧 Función en desarrollo[/yellow]")