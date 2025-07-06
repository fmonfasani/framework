"""
Genesis Engine - Sistema operativo completo para desarrollo y despliegue de aplicaciones full-stack.

Genesis Engine es un framework que combina generación inteligente de código, 
orquestación de agentes IA especializados y despliegue automático para 
crear aplicaciones modernas completas en minutos.
"""

__version__ = "1.0.0"
__author__ = "Genesis Team"
__email__ = "team@genesis.dev"

# Importaciones principales
from genesis_engine.core.orchestrator import GenesisOrchestrator
from genesis_engine.core.project_manager import ProjectManager
from genesis_engine.mcp.protocol import MCPProtocol
from genesis_engine.agents.base_agent import BaseAgent

# Configuración de logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "GenesisOrchestrator",
    "ProjectManager", 
    "MCPProtocol",
    "BaseAgent",
    "__version__",
    "__author__",
    "__email__"
]