"""
Configuración central de Genesis Engine

Este módulo maneja toda la configuración del sistema, incluyendo:
- Configuración de logging
- Variables de entorno
- Rutas y directorios
- Configuraciones por defecto
- Validación de entorno de desarrollo
"""

import os
import json
import logging
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
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
    
    # Configuración de templates
    strict_template_validation: bool = True

    # Internal dictionary mirroring public attributes
    _config: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def _sync_config(self):
        """Synchronize internal config dict with current attributes."""
        self._config = {
            key: getattr(self, key)
            for key in self.__dataclass_fields__
            if key != "_config"
        }

    def _setup_logging(
        self,
        level: Optional[str] = None,
        log_file: Optional[Union[str, Path]] = None,
        enable_rich: Optional[bool] = None,
    ) -> logging.Logger:
        """Configure logging using current configuration."""
        if level is None:
            level = self._config.get("log_level", "INFO")
        if enable_rich is None:
            enable_rich = self._config.get("enable_rich_logging", True) and HAS_RICH

        log_level = getattr(logging, str(level).upper(), logging.INFO)

        root_logger = logging.getLogger()

        # Remove previous handlers added by this setup
        for handler in root_logger.handlers[:]:
            if getattr(handler, "_genesis_handler", False):
                root_logger.removeHandler(handler)

        # Console handler
        if enable_rich and HAS_RICH:
            console_handler = RichHandler(
                console=Console(),
                show_time=True,
                show_path=True,
                rich_tracebacks=True,
                markup=True,
            )
            formatter = logging.Formatter("%(message)s")
        else:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(self._config.get("log_format"))

        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        console_handler._genesis_handler = True

        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)

        # File handler
        log_path = Path(log_file) if log_file else Path(self._config.get("log_dir")) / "genesis.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(self._config.get("log_format")))
        file_handler.setLevel(log_level)
        file_handler._genesis_handler = True
        root_logger.addHandler(file_handler)

        genesis_logger = logging.getLogger("genesis_engine")
        genesis_logger.setLevel(log_level)
        genesis_logger.propagate = True

        genesis_logger.info("Genesis Engine logging configurado")

        return genesis_logger
    
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

        # Sync internal config dictionary with current attributes
        self._sync_config()

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value from the global instance."""
        cfg = get_config()
        return getattr(cfg, key, default)

    @classmethod
    def get_supported_frameworks(cls, component: str) -> List[str]:
        """Return supported frameworks for a component from the global config."""
        return get_config()._get_supported_frameworks(component)

    @classmethod
    def set(cls, key: str, value: Any):
        """Set a configuration value on the global instance."""
        cfg = get_config()
        if "." in key:
            attr, subkey = key.split(".", 1)
            if attr == "supported_frameworks":
                mapping = {
                    "backend": "supported_backends",
                    "frontend": "supported_frontends",
                    "database": "supported_databases",
                }
                if subkey in mapping:
                    setattr(cfg, mapping[subkey], value)
                    cfg._sync_config()
                    return
        setattr(cfg, key, value)
        cfg._sync_config()
    
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
    
    def _get_supported_frameworks(self, component: str) -> List[str]:
        """Obtener frameworks soportados para un componente"""
        mapping = {
            "backend": self.supported_backends,
            "frontend": self.supported_frontends,
            "database": self.supported_databases
        }
        return mapping.get(component, [])
    
    def is_framework_supported(self, component: str, framework: str) -> bool:
        """Verificar si un framework está soportado"""
        supported = self._get_supported_frameworks(component)
        return framework.lower() in [f.lower() for f in supported]
    
    def get_default_port(self, service: str) -> int:
        """Obtener puerto por defecto para un servicio"""
        return self.default_ports.get(service, 8080)


class EnvironmentValidator:
    """Validador del entorno de desarrollo."""
    
    @staticmethod
    def check_python_version() -> Tuple[bool, str]:
        """Verificar versión de Python."""
        version = sys.version_info
        required_major, required_minor = 3, 9
        
        if version.major >= required_major and version.minor >= required_minor:
            return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
        else:
            return False, f"Python {version.major}.{version.minor}.{version.micro} (se requiere 3.9+)"
    
    @staticmethod
    def check_node_version() -> Tuple[bool, str]:
        """Verificar versión de Node.js."""
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                # Extraer número de versión
                version_num = version.lstrip('v')
                major = int(version_num.split('.')[0])
                
                if major >= 18:
                    return True, f"Node.js {version} ✓"
                else:
                    return False, f"Node.js {version} (se requiere v18+)"
            else:
                return False, "Node.js no encontrado"
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            return False, "Node.js no encontrado o inaccesible"
    
    @staticmethod
    def check_git() -> Tuple[bool, str]:
        """Verificar instalación de Git."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"{version} ✓"
            else:
                return False, "Git no encontrado"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Git no encontrado o inaccesible"
    
    @staticmethod
    def check_docker() -> Tuple[bool, str]:
        """Verificar instalación de Docker."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"{version} ✓"
            else:
                return False, "Docker no encontrado"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Docker no encontrado o inaccesible"
    
    @staticmethod
    def check_docker_compose() -> Tuple[bool, str]:
        """Verificar instalación de Docker Compose."""
        try:
            # Probar docker compose (nuevo)
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"Docker Compose {version} ✓"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Probar docker-compose (legacy)
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"{version} ✓"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return False, "Docker Compose no encontrado"
    
    @staticmethod
    def check_npm() -> Tuple[bool, str]:
        """Verificar instalación de npm."""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"npm {version} ✓"
            else:
                return False, "npm no encontrado"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "npm no encontrado o inaccesible"
    
    @staticmethod
    def check_yarn() -> Tuple[bool, str]:
        """Verificar instalación de Yarn (opcional)."""
        try:
            result = subprocess.run(
                ["yarn", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"Yarn {version} ✓"
            else:
                return False, "Yarn no encontrado"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Yarn no encontrado (opcional)"
    
    @staticmethod
    def check_postgresql() -> Tuple[bool, str]:
        """Verificar instalación de PostgreSQL (opcional)."""
        try:
            result = subprocess.run(
                ["psql", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"{version} ✓"
            else:
                return False, "PostgreSQL no encontrado (opcional)"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "PostgreSQL no encontrado (opcional)"


def validate_environment() -> Dict[str, Any]:
    """
    FUNCIÓN CORREGIDA: Validar el entorno de desarrollo completo.
    
    Returns:
        Diccionario con resultados de validación
    """
    validator = EnvironmentValidator()
    
    checks = [
        ("Python Version", validator.check_python_version),
        ("Node.js Version", validator.check_node_version),
        ("Git Installation", validator.check_git),
        ("Docker Installation", validator.check_docker),
        ("Docker Compose", validator.check_docker_compose),
        ("npm Installation", validator.check_npm),
        ("Yarn Installation", validator.check_yarn),
        ("PostgreSQL", validator.check_postgresql),
    ]
    
    results = {}
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            results[check_name] = {
                "success": success,
                "message": message
            }
            
            if success:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            results[check_name] = {
                "success": False,
                "message": f"Error durante verificación: {e}"
            }
            failed += 1
    
    # Determinar estado general
    required_checks = ["Python Version", "Node.js Version", "Git Installation"]
    required_passed = all(
        results[check]["success"] for check in required_checks 
        if check in results
    )
    
    return {
        "overall_success": required_passed,
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "required_passed": required_passed,
        "checks": results,
        "summary": f"✅ {passed}/{len(checks)} verificaciones pasaron" if required_passed else f"❌ Faltan dependencias requeridas"
    }


def get_system_info() -> Dict[str, Any]:
    """Obtener información del sistema."""
    return {
        "platform": sys.platform,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": sys.executable,
        "working_directory": str(Path.cwd()),
        "home_directory": str(Path.home()),
        "genesis_config_dir": str(Path.home() / ".genesis"),
    }


def load_config_from_file(config_path: Path) -> Dict[str, Any]:
    """
    Cargar configuración desde archivo.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Diccionario con configuración
    """
    import json
    try:
        import yaml
        HAS_YAML = True
    except ImportError:
        HAS_YAML = False
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml'] and HAS_YAML:
                return yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    except Exception as e:
        raise ValueError(f"Error loading config from {config_path}: {e}")


def create_default_config(config_path: Path) -> GenesisConfig:
    """
    Crear configuración por defecto.
    
    Args:
        config_path: Ruta donde crear el archivo de configuración
        
    Returns:
        Configuración creada
    """
    config = GenesisConfig()
    
    # Crear archivo de configuración ejemplo
    config_data = {
        "templates_dir": str(config.templates_dir),
        "config_dir": str(config.config_dir),
        "cache_dir": str(config.cache_dir),
        "log_dir": str(config.log_dir),
        "log_level": config.log_level,
        "enable_rich_logging": config.enable_rich_logging,
        "default_template": config.default_template,
        "supported_backends": config.supported_backends,
        "supported_frontends": config.supported_frontends,
        "supported_databases": config.supported_databases,
        "default_ports": config.default_ports,
        "timeout": config.timeout,
        "max_retries": config.max_retries,
        "strict_template_validation": config.strict_template_validation
    }
    
    import json
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    logging.info(f"Default config created: {config_path}")
    return config


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
    
    # Delegate to instance method for configuration
    return config._setup_logging(level=level, log_file=log_file, enable_rich=enable_rich)

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
if _config_instance is None:
    _config_instance = load_user_config()
