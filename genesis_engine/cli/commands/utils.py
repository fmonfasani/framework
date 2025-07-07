"""
Utilidades para CLI
"""

import sys
import subprocess

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

def check_dependencies() -> bool:
    """Verificar dependencias básicas.

    Returns ``True`` si todas las dependencias están disponibles. Lanza un
    ``RuntimeError`` si alguna está ausente o si la versión de Python es
    inferior a 3.8.
    """

    missing = []

    if sys.version_info < (3, 8):
        missing.append("Python >= 3.8")

    def _check(cmd, name):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    if not _check(["node", "--version"], "Node.js"):
        missing.append("Node.js")
    if not _check(["git", "--version"], "Git"):
        missing.append("Git")
    if not _check(["docker", "--version"], "Docker"):
        missing.append("Docker")

    if missing:
        raise RuntimeError(
            "Dependencias faltantes: " + ", ".join(missing)
        )

    return True
