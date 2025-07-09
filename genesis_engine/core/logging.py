"""
Módulo de logging para Genesis Engine - CORREGIDO

Proporciona funciones centralizadas para configuración de logging
SIN imports circulares
"""

import logging
from typing import Optional

def get_logger(name: str = "genesis_engine") -> logging.Logger:
    """
    Obtener logger configurado para Genesis Engine
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger configurado
    """
    # Configurar logging básico si no está configurado
    if not logging.getLogger().handlers:
        setup_basic_logging()
    
    return logging.getLogger(name)

def setup_basic_logging(level: str = "INFO"):
    """Configurar logging básico"""
    try:
        from rich.logging import RichHandler
        from rich.console import Console
        
        # Usar Rich handler si está disponible
        handler = RichHandler(
            console=Console(),
            show_time=True,
            show_path=False,
            rich_tracebacks=True
        )
        format_str = "%(message)s"
        
    except ImportError:
        # Fallback a handler estándar
        handler = logging.StreamHandler()
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Limpiar handlers existentes para evitar duplicados
    root_logger = logging.getLogger()
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
    
    # Configurar nuevo handler
    log_level = getattr(logging, level.upper(), logging.INFO)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(format_str))
    
    # Configurar logger raíz
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

def setup_logging(level: str = "INFO", enable_rich: bool = True) -> logging.Logger:
    """
    Configurar logging para Genesis Engine con más opciones
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_rich: Habilitar Rich logging si está disponible
    
    Returns:
        Logger configurado
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Limpiar handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configurar handler apropiado
    if enable_rich:
        try:
            from rich.logging import RichHandler
            from rich.console import Console
            
            handler = RichHandler(
                console=Console(),
                show_time=True,
                show_path=False,
                rich_tracebacks=True
            )
            format_str = "%(message)s"
        except ImportError:
            handler = logging.StreamHandler()
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        handler = logging.StreamHandler()
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(format_str))
    
    # Configurar logger raíz
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Configurar logger específico de Genesis
    genesis_logger = logging.getLogger("genesis_engine")
    genesis_logger.setLevel(log_level)
    
    return genesis_logger

# Configurar logging básico al importar el módulo
setup_basic_logging()   