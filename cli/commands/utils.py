"""
Utilidades para CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from genesis_engine import __version__

console = Console()

def show_banner():
    """Mostrar banner de Genesis Engine"""
    banner_text = Text()
    banner_text.append("🚀 ", style="bold cyan")
    banner_text.append("GENESIS ENGINE", style="bold white")
    banner_text.append(f" v{__version__}", style="bold green")
    banner_text.append("\n")
    banner_text.append("Sistema operativo para desarrollo full-stack moderno", style="italic cyan")
    
    console.print(Panel.fit(
        banner_text,
        border_style="cyan",
        padding=(1, 2)
    ))

def check_dependencies():
    """Verificar dependencias básicas"""
    # TODO: Implementar verificación de dependencias
    pass