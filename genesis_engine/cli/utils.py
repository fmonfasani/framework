"""Helper functions for the Genesis Engine CLI."""

from .commands.utils import show_banner, check_dependencies
import sys
import shutil

__all__ = [
    "show_banner",
    "check_dependencies",
    "get_terminal_size",
    "is_interactive_terminal",
    "get_user_confirmation",
]


def get_terminal_size() -> tuple[int, int]:
    """Obtener tamaño de terminal"""
    try:
        return shutil.get_terminal_size()
    except Exception:
        return (80, 24)


def is_interactive_terminal() -> bool:
    """Verificar si estamos en terminal interactivo"""
    return sys.stdin.isatty() and sys.stdout.isatty()


def get_user_confirmation(message: str, default: bool = False) -> bool:
    """Solicitar confirmación al usuario"""
    if not is_interactive_terminal():
        return default

    suffix = " [Y/n]" if default else " [y/N]"
    response = input(f"{message}{suffix}: ").strip().lower()
    if not response:
        return default
    return response in {"y", "yes", "true", "1"}
