"""
Genesis Engine - Sistema operativo completo para desarrollo y despliegue de aplicaciones full-stack.

Genesis Engine es un framework que combina generación inteligente de código, 
orquestación de agentes IA especializados y despliegue automático para 
crear aplicaciones modernas completas en minutos.
"""

__version__ = "1.0.0"
__author__ = "Genesis Team"
__email__ = "team@genesis.dev"

# Configuración de logging
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Importaciones principales con manejo de errores
try:
    from genesis_engine.core.orchestrator import GenesisOrchestrator
    from genesis_engine.core.project_manager import ProjectManager
    from genesis_engine.mcp.protocol import MCPProtocol
    from genesis_engine.mcp.agent_base import GenesisAgent
except ImportError as e:  # pragma: no cover - graceful fallback if deps fail
    logger.error(f"Failed to import core dependencies: {e}", exc_info=True)
    GenesisOrchestrator = None
    ProjectManager = None
    MCPProtocol = None
    GenesisAgent = None

__all__ = [
    "GenesisOrchestrator",
    "ProjectManager", 
    "MCPProtocol",
    "GenesisAgent",
    "__version__",
    "__author__",
    "__email__"
]