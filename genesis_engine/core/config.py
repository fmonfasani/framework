"""
Genesis Engine - Configuración Core

Configuraciones globales, constantes y utilidades del sistema.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import logging
from rich.logging import RichHandler

# Versión de Genesis Engine
__version__ = "1.0.0"

# Constantes globales
DEFAULT_CONFIG_FILE = "genesis.config.json"
GENESIS_DIR = ".genesis"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
CACHE_DIR = Path.home() / ".genesis" / "cache"
LOG_DIR = Path.home() / ".genesis" / "logs"

# Configuración de logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

@dataclass
class StackDefaults:
    """Configuraciones por defecto para stacks"""
    
    # Golden Path - SaaS Básico
    GOLDEN_PATH = {
        "backend": "fastapi",
        "frontend": "nextjs", 
        "database": "postgresql",
        "state_management": "redux_toolkit",
        "styling": "tailwind",
        "auth": "jwt",
        "ui_components": "shadcn",
        "typescript": True,
        "docker": True,
        "ci_cd": "github_actions"
    }
    
    # API REST + SPA
    API_FIRST = {
        "backend": "fastapi",
        "frontend": "react",
        "database": "postgresql", 
        "state_management": "zustand",
        "styling": "tailwind",
        "auth": "jwt",
        "typescript": True
    }
    
    # E-commerce/Marketplace
    ECOMMERCE = {
        "backend": "fastapi",
        "frontend": "nextjs",
        "database": "postgresql",
        "state_management": "redux_toolkit", 
        "styling": "tailwind",
        "auth": "jwt",
        "payment": "stripe",
        "typescript": True
    }

class GenesisConfig:
    """
    Gestión de configuración global de Genesis Engine
    """
    
    _instance = None
    _config: Dict[str, Any] = {}
    _verbose: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GenesisConfig, cls).__new__(cls)
            cls._instance._load_default_config()
        return cls._instance
    
    def _load_default_config(self):
        """Cargar configuración por defecto"""
        self._config = {
            "version": __version__,
            "templates_dir": str(TEMPLATES_DIR),
            "cache_dir": str(CACHE_DIR),
            "log_dir": str(LOG_DIR),
            "log_level": "INFO",
            "default_template": "saas-basic",
            "default_stack": "golden-path",
            "auto_install_deps": True,
            "enable_telemetry": False,
            "check_updates": True,
            "parallel_generation": True,
            "max_workers": 4,
            "timeout": 300,
            "retry_attempts": 3,
            "stack_defaults": {
                "golden-path": StackDefaults.GOLDEN_PATH,
                "api-first": StackDefaults.API_FIRST,
                "ecommerce": StackDefaults.ECOMMERCE
            },
            "supported_frameworks": {
                "backend": ["fastapi", "nestjs", "express", "django", "flask"],
                "frontend": ["nextjs", "react", "vue", "nuxt", "svelte"],
                "database": ["postgresql", "mysql", "mongodb", "sqlite"],
                "styling": ["tailwind", "styled_components", "sass", "css_modules"],
                "state_management": ["redux_toolkit", "zustand", "context_api", "pinia", "vuex"]
            },
            "cloud_providers": {
                "aws": {
                    "regions": ["us-east-1", "us-west-2", "eu-west-1"],
                    "services": ["ec2", "ecs", "lambda", "rds"]
                },
                "gcp": {
                    "regions": ["us-central1", "europe-west1"],
                    "services": ["compute", "cloud-run", "cloud-sql"]
                },
                "azure": {
                    "regions": ["eastus", "westus2", "westeurope"],
                    "services": ["app-service", "container-instances"]
                }
            }
        }
    
    @classmethod
    def load_config(cls, config_file: Path):
        """Cargar configuración desde archivo"""
        instance = cls()
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                
                # Merge con configuración por defecto
                instance._config.update(user_config)
                
                # Setup logging
                instance._setup_logging()
                
                logging.info(f"Configuración cargada desde: {config_file}")
            else:
                logging.warning(f"Archivo de configuración no encontrado: {config_file}")
                
        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
    
    @classmethod 
    def save_config(cls, config_file: Path):
        """Guardar configuración actual"""
        instance = cls()
        
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(instance._config, f, indent=2)
                
            logging.info(f"Configuración guardada en: {config_file}")
            
        except Exception as e:
            logging.error(f"Error guardando configuración: {e}")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        instance = cls()
        
        # Soporte para keys anidadas (ej: "stack_defaults.golden-path")
        keys = key.split('.')
        value = instance._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @classmethod
    def set(cls, key: str, value: Any):
        """Establecer valor de configuración"""
        instance = cls()
        
        # Soporte para keys anidadas
        keys = key.split('.')
        config = instance._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @classmethod
    def get_version(cls) -> str:
        """Obtener versión de Genesis Engine"""
        return __version__
    
    @classmethod
    def set_verbose(cls, verbose: bool):
        """Configurar modo verbose"""
        cls._verbose = verbose
        
        # Configurar nivel de logging
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)
    
    @classmethod
    def is_verbose(cls) -> bool:
        """Verificar si está en modo verbose"""
        return cls._verbose
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_level = getattr(logging, self._config.get("log_level", "INFO"))

        # Crear directorio de logs
        log_dir = Path(self._config.get("log_dir", LOG_DIR))
        log_dir.mkdir(parents=True, exist_ok=True)

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        formatter = logging.Formatter(LOG_FORMAT)

        has_console = any(isinstance(h, RichHandler) for h in root_logger.handlers)
        if not has_console:
            console_handler = RichHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        log_path = log_dir / "genesis.log"
        has_file = any(
            isinstance(h, logging.FileHandler) and Path(getattr(h, "baseFilename", "")) == log_path
            for h in root_logger.handlers
        )
        if not has_file:
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    
    @classmethod
    def get_stack_config(cls, stack_name: str) -> Dict[str, Any]:
        """Obtener configuración de stack"""
        return cls.get(f"stack_defaults.{stack_name}", {})
    
    @classmethod
    def is_framework_supported(cls, category: str, framework: str) -> bool:
        """Verificar si un framework está soportado"""
        supported = cls.get(f"supported_frameworks.{category}", [])
        return framework in supported
    
    @classmethod
    def get_supported_frameworks(cls, category: str) -> List[str]:
        """Obtener frameworks soportados por categoría"""
        return cls.get(f"supported_frameworks.{category}", [])
    
    @classmethod
    def setup_directories(cls):
        """Crear directorios necesarios"""
        directories = [
            cls.get("cache_dir"),
            cls.get("log_dir"),
            Path.home() / ".genesis" / "templates",
            Path.home() / ".genesis" / "projects"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_template_path(cls, template_name: str) -> Path:
        """Obtener ruta de template"""
        templates_dir = Path(cls.get("templates_dir"))
        return templates_dir / f"{template_name}.j2"
    
    @classmethod
    def get_cache_path(cls, cache_key: str) -> Path:
        """Obtener ruta de cache"""
        cache_dir = Path(cls.get("cache_dir"))
        return cache_dir / cache_key
    
    @classmethod
    def clean_cache(cls):
        """Limpiar cache"""
        cache_dir = Path(cls.get("cache_dir"))
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            logging.info("Cache limpiado")

# Funciones de utilidad
def get_user_config_file() -> Path:
    """Obtener archivo de configuración del usuario"""
    return Path.home() / ".genesis" / "config.json"

def ensure_genesis_directories():
    """Asegurar que existan los directorios de Genesis"""
    GenesisConfig.setup_directories()

def load_user_config():
    """Cargar configuración del usuario"""
    config_file = get_user_config_file()
    if config_file.exists():
        GenesisConfig.load_config(config_file)

def save_user_config():
    """Guardar configuración del usuario"""
    config_file = get_user_config_file()
    GenesisConfig.save_config(config_file)

# Inicialización automática
def initialize_genesis():
    """Inicializar Genesis Engine"""
    ensure_genesis_directories()
    load_user_config()
    
    # Configurar logging básico
    GenesisConfig()._setup_logging()
    
    logging.info(f"Genesis Engine v{__version__} inicializado")

# Variables de entorno importantes
def get_env_var(name: str, default: Any = None) -> Any:
    """Obtener variable de entorno con fallback a configuración"""
    env_value = os.getenv(name)
    if env_value is not None:
        return env_value
    
    # Mapeo de variables de entorno a configuración
    env_mapping = {
        "GENESIS_LOG_LEVEL": "log_level",
        "GENESIS_CACHE_DIR": "cache_dir",
        "GENESIS_TEMPLATES_DIR": "templates_dir",
        "GENESIS_VERBOSE": "verbose",
        "GENESIS_AUTO_INSTALL": "auto_install_deps"
    }
    
    config_key = env_mapping.get(name)
    if config_key:
        return GenesisConfig.get(config_key, default)
    
    return default

# Constantes de features
class Features:
    """Características disponibles en Genesis Engine"""
    
    # Core features
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    API_DOCUMENTATION = "api_documentation"
    
    # Advanced features
    BILLING = "billing"
    NOTIFICATIONS = "notifications"
    FILE_UPLOAD = "file_upload"
    SEARCH = "search"
    ANALYTICS = "analytics"
    ADMIN_PANEL = "admin_panel"
    
    # AI features
    AI_CHAT = "ai_chat"
    AI_ASSISTANT = "ai_assistant"
    RAG_SYSTEM = "rag_system"
    SEMANTIC_SEARCH = "semantic_search"
    
    # DevOps features
    DOCKER = "docker"
    CI_CD = "ci_cd"
    MONITORING = "monitoring"
    BACKUP = "backup"
    SSL = "ssl"
    
    @classmethod
    def get_all_features(cls) -> List[str]:
        """Obtener todas las características disponibles"""
        return [
            value for name, value in cls.__dict__.items()
            if not name.startswith('_') and isinstance(value, str) and name != 'get_all_features'
        ]
    
    @classmethod
    def get_core_features(cls) -> List[str]:
        """Obtener características core"""
        return [
            cls.AUTHENTICATION,
            cls.AUTHORIZATION, 
            cls.DATABASE,
            cls.API_DOCUMENTATION
        ]
    
    @classmethod
    def get_ai_features(cls) -> List[str]:
        """Obtener características de IA"""
        return [
            cls.AI_CHAT,
            cls.AI_ASSISTANT,
            cls.RAG_SYSTEM,
            cls.SEMANTIC_SEARCH
        ]

# Validadores de configuración
def validate_stack_config(stack_config: Dict[str, str]) -> List[str]:
    """Validar configuración de stack"""
    errors = []
    
    # Verificar frameworks soportados
    for category, framework in stack_config.items():
        if not GenesisConfig.is_framework_supported(category, framework):
            supported = GenesisConfig.get_supported_frameworks(category)
            errors.append(
                f"Framework '{framework}' no soportado para '{category}'. "
                f"Soportados: {', '.join(supported)}"
            )
    
    # Verificar compatibilidad entre frameworks
    frontend = stack_config.get("frontend")
    state_mgmt = stack_config.get("state_management")
    
    if frontend and state_mgmt:
        incompatible = {
            "vue": ["redux_toolkit"],
            "nuxt": ["redux_toolkit"], 
            "react": ["pinia", "vuex"],
            "nextjs": ["pinia", "vuex"],
            "angular": ["redux_toolkit", "zustand", "pinia", "vuex"]
        }
        
        if frontend in incompatible and state_mgmt in incompatible[frontend]:
            errors.append(
                f"'{state_mgmt}' no es compatible con '{frontend}'"
            )
    
    return errors

def validate_project_name(name: str) -> List[str]:
    """Validar nombre de proyecto"""
    errors = []
    
    if not name:
        errors.append("Nombre de proyecto es obligatorio")
        return errors
    
    # Verificar caracteres válidos
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        errors.append(
            "Nombre debe empezar con letra y contener solo letras, números, _ y -"
        )
    
    # Verificar longitud
    if len(name) < 3:
        errors.append("Nombre debe tener al menos 3 caracteres")
    elif len(name) > 50:
        errors.append("Nombre debe tener máximo 50 caracteres")
    
    # Verificar palabras reservadas
    reserved_words = [
        "genesis", "engine", "admin", "api", "app", "www", "mail", "ftp",
        "test", "dev", "prod", "staging", "localhost", "config", "setup"
    ]
    
    if name.lower() in reserved_words:
        errors.append(f"'{name}' es una palabra reservada")
    
    return errors

# Inicializar al importar el módulo
initialize_genesis()