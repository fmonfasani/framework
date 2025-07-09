"""
Configuración central de Genesis Engine

Este módulo maneja toda la configuración del sistema, incluyendo:
- Configuración de logging
- Variables de entorno
- Rutas y directorios
- Configuraciones por defecto
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

try:
    from rich.logging import RichHandler
    from rich.console import Console
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class Features(str, Enum):
    """Available optional project features."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BILLING = "billing"
    NOTIFICATIONS = "notifications"
    FILE_UPLOAD = "file_upload"
    SEARCH = "search"
    ANALYTICS = "analytics"
    ADMIN_PANEL = "admin_panel"
    AI_CHAT = "ai_chat"
    MONITORING = "monitoring"

@dataclass
class GenesisConfig:
    """Configuración principal de Genesis Engine"""
    
    # Directorios
    root_dir: Path = field(default_factory=lambda: Path.cwd())
    config_dir: Path = field(default_factory=lambda: Path.home() / ".genesis")
    templates_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    log_dir: Optional[Path] = None
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_rich_logging: bool = True
    
    # Configuración de framework
    default_template: str = "saas-basic"
    supported_backends: List[str] = field(default_factory=lambda: [
        "fastapi", "nestjs", "express", "django", "flask"
    ])
    supported_frontends: List[str] = field(default_factory=lambda: [
        "nextjs", "react", "vue", "nuxt", "svelte"
    ])
    supported_databases: List[str] = field(default_factory=lambda: [
        "postgresql", "mysql", "mongodb", "sqlite"
    ])
    
    # Configuración de servicios
    default_ports: Dict[str, int] = field(default_factory=lambda: {
        "backend": 8000,
        "frontend": 3000,
        "database": 5432
    })
    
    # Configuración de red
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        """Inicialización posterior"""
        # Configurar directorios por defecto
        if self.templates_dir is None:
            self.templates_dir = self.root_dir / "genesis_engine" / "templates"
        
        if self.cache_dir is None:
            self.cache_dir = self.config_dir / "cache"
        
        if self.log_dir is None:
            self.log_dir = self.config_dir / "logs"
        
        # Crear directorios si no existen
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value from the global instance."""
        cfg = get_config()
        return getattr(cfg, key, default)
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> 'GenesisConfig':
        """Cargar configuración desde archivo"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir paths string a Path objects
            for key in ['root_dir', 'config_dir', 'templates_dir', 'cache_dir', 'log_dir']:
                if key in data and data[key]:
                    data[key] = Path(data[key])
            
            return cls(**data)
        
        except Exception as e:
            logging.warning(f"Error cargando configuración desde {config_file}: {e}")
            return cls()
    
    def save_to_file(self, config_file: Union[str, Path]):
        """Guardar configuración a archivo"""
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir a diccionario serializable
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                data[key] = str(value)
            else:
                data[key] = value
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando configuración en {config_file}: {e}")
    
    def get_supported_frameworks(self, component: str) -> List[str]:
        """Obtener frameworks soportados para un componente"""
        mapping = {
            "backend": self.supported_backends,
            "frontend": self.supported_frontends,
            "database": self.supported_databases
        }
        return mapping.get(component, [])
    
    def is_framework_supported(self, component: str, framework: str) -> bool:
        """Verificar si un framework está soportado"""
        supported = self.get_supported_frameworks(component)
        return framework.lower() in [f.lower() for f in supported]
    
    def get_default_port(self, service: str) -> int:
        """Obtener puerto por defecto para un servicio"""
        return self.default_ports.get(service, 8080)

# Instancia global de configuración
_config_instance: Optional[GenesisConfig] = None

def get_config() -> GenesisConfig:
    """Obtener instancia global de configuración"""
    global _config_instance
    
    if _config_instance is None:
        # Intentar cargar desde archivo de configuración
        config_file = Path.home() / ".genesis" / "config.json"
        _config_instance = GenesisConfig.from_file(config_file)
    
    return _config_instance

def set_config(config: GenesisConfig):
    """Establecer instancia global de configuración"""
    global _config_instance
    _config_instance = config

def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Union[str, Path]] = None,
    enable_rich: Optional[bool] = None
) -> logging.Logger:
    """
    Configurar logging para Genesis Engine
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo de log (opcional)
        enable_rich: Habilitar Rich logging (por defecto True si está disponible)
    
    Returns:
        Logger configurado
    """
    config = get_config()
    
    # Usar valores de configuración si no se proporcionan
    if level is None:
        level = config.log_level
    if enable_rich is None:
        enable_rich = config.enable_rich_logging and HAS_RICH
    
    # Configurar nivel de logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Limpiar handlers existentes para evitar duplicados
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configurar formato de logging
    if enable_rich and HAS_RICH:
        # Usar Rich handler para output colorizado
        console_handler = RichHandler(
            console=Console(),
            show_time=True,
            show_path=True,
            rich_tracebacks=True,
            markup=True
        )
        console_handler.setLevel(log_level)
        
        # Formato más simple para Rich
        formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(formatter)
    else:
        # Handler estándar
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        formatter = logging.Formatter(config.log_format)
        console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Configurar file handler si se especifica
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        file_formatter = logging.Formatter(config.log_format)
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
    else:
        # Usar archivo de log por defecto
        default_log_file = config.log_dir / "genesis.log"
        
        file_handler = logging.FileHandler(default_log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        file_formatter = logging.Formatter(config.log_format)
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
    
    # Configurar logger específico para Genesis
    genesis_logger = logging.getLogger("genesis_engine")
    genesis_logger.setLevel(log_level)
    
    # Evitar propagación duplicada al root logger
    genesis_logger.propagate = True
    
    # Log de inicialización
    genesis_logger.info("Genesis Engine logging configurado")
    genesis_logger.debug(f"Nivel de logging: {level}")
    genesis_logger.debug(f"Rich logging: {enable_rich}")
    if log_file:
        genesis_logger.debug(f"Archivo de log: {log_file}")
    
    return genesis_logger

def get_logger(name: str = "genesis_engine") -> logging.Logger:
    """
    Obtener logger configurado para Genesis Engine
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger configurado
    """
    # Asegurar que el logging esté configurado
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logging.getLogger(name)

def configure_environment():
    """Configurar variables de entorno para Genesis Engine"""
    config = get_config()
    
    # Establecer variables de entorno útiles
    os.environ.setdefault("GENESIS_CONFIG_DIR", str(config.config_dir))
    os.environ.setdefault("GENESIS_TEMPLATES_DIR", str(config.templates_dir))
    os.environ.setdefault("GENESIS_CACHE_DIR", str(config.cache_dir))
    os.environ.setdefault("GENESIS_LOG_DIR", str(config.log_dir))
    
    # Configurar Python path si es necesario
    root_dir = str(config.root_dir)
    if root_dir not in os.environ.get("PYTHONPATH", ""):
        current_path = os.environ.get("PYTHONPATH", "")
        if current_path:
            os.environ["PYTHONPATH"] = f"{root_dir}{os.pathsep}{current_path}"
        else:
            os.environ["PYTHONPATH"] = root_dir

def load_user_config(config_file: Optional[Union[str, Path]] = None) -> GenesisConfig:
    """
    Cargar configuración de usuario
    
    Args:
        config_file: Archivo de configuración específico (opcional)
    
    Returns:
        Configuración cargada
    """
    if config_file is None:
        config_file = Path.home() / ".genesis" / "config.json"
    
    config = GenesisConfig.from_file(config_file)
    set_config(config)
    configure_environment()

    return config

def initialize(
    config_file: Optional[Union[str, Path]] = None,
    level: Optional[str] = None,
    log_file: Optional[Union[str, Path]] = None,
    enable_rich: Optional[bool] = None,
) -> GenesisConfig:
    """Inicializar configuración global y logging.

    Esta función carga la configuración de usuario y establece el entorno y
    el sistema de logging de Genesis Engine.

    Args:
        config_file: Ruta alternativa al archivo de configuración de usuario.
        level: Nivel de logging a utilizar.
        log_file: Archivo de log a emplear.
        enable_rich: Habilitar salida enriquecida mediante Rich.

    Returns:
        Instancia de :class:`GenesisConfig` cargada.
    """

    config = load_user_config(config_file)
    setup_logging(level=level, log_file=log_file, enable_rich=enable_rich)
    configure_environment()
    return config

def save_user_config(config: Optional[GenesisConfig] = None, config_file: Optional[Union[str, Path]] = None):
    """
    Guardar configuración de usuario
    
    Args:
        config: Configuración a guardar (usa la global si no se especifica)
        config_file: Archivo de destino (usa el por defecto si no se especifica)
    """
    if config is None:
        config = get_config()
    
    if config_file is None:
        config_file = Path.home() / ".genesis" / "config.json"
    
    config.save_to_file(config_file)

def initialize(
    config_file: Optional[Union[str, Path]] = None,
    log_file: Optional[Union[str, Path]] = None,
    level: Optional[str] = None,
    enable_rich: Optional[bool] = None,
) -> GenesisConfig:
    """Inicializar configuración y logging de Genesis Engine."""

    # Cargar configuración de usuario
    config = load_user_config(config_file)

    # Configurar logging y variables de entorno
    setup_logging(level=level, log_file=log_file, enable_rich=enable_rich)
    configure_environment()

    return config

# Configuración por defecto al importar el módulo
if _config_instance is None:    _config_instance = load_user_config()
