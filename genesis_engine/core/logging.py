# genesis_engine/core/logging.py - CORREGIDO
"""
Sistema de Logging - CORREGIDO para Windows

FIXES:
- Removidos emojis que causaban 'charmap' codec error
- Configuración UTF-8 explícita
- Fallback robusto para Rich logging
- Prefijos ASCII en lugar de emojis
"""

import logging
import sys
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
    """Configurar logging básico - CORREGIDO para Windows"""
    try:
        from rich.logging import RichHandler
        from rich.console import Console
        
        # CORRECCIÓN: Console con encoding UTF-8 explícito
        console = Console(
            file=sys.stdout,
            force_terminal=True,
            legacy_windows=False,
            _environ={"PYTHONIOENCODING": "utf-8"}
        )
        
        # Usar Rich handler si está disponible
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=False,  # NUEVO: Deshabilitar markup para evitar conflictos
            keywords=[]    # NUEVO: Evitar keywords problemáticos
        )
        format_str = "%(message)s"
        
    except ImportError:
        # Fallback a handler estándar con encoding explícito
        handler = logging.StreamHandler(sys.stdout)
        handler.setEncoding('utf-8')  # CORRECCIÓN: Encoding explícito
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Limpiar handlers existentes para evitar duplicados
    root_logger = logging.getLogger()
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
    
    # Configurar nuevo handler
    log_level = getattr(logging, level.upper(), logging.INFO)
    handler.setLevel(log_level)
    
    # CORRECCIÓN: Formatter con encoding safe
    formatter = logging.Formatter(format_str)
    if hasattr(handler, 'setEncoding'):
        handler.setEncoding('utf-8')
    
    handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

def setup_logging(level: str = "INFO", enable_rich: bool = True) -> logging.Logger:
    """
    Configurar logging para Genesis Engine con más opciones - CORREGIDO
    
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
            
            # CORRECCIÓN: Console con configuración Windows-safe
            console = Console(
                file=sys.stdout,
                force_terminal=True,
                legacy_windows=False,
                width=120,  # NUEVO: Ancho fijo
                _environ={"PYTHONIOENCODING": "utf-8"}
            )
            
            handler = RichHandler(
                console=console,
                show_time=True,
                show_path=False,
                rich_tracebacks=True,
                markup=False,      # CORRECCIÓN: Sin markup
                keywords=[],       # CORRECCIÓN: Sin keywords problemáticos
                log_time_format="[%X]"  # CORRECCIÓN: Formato simple
            )
            format_str = "%(message)s"
            
        except ImportError:
            handler = logging.StreamHandler(sys.stdout)
            handler.setEncoding('utf-8')
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setEncoding('utf-8')
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handler.setLevel(log_level)
    
    # CORRECCIÓN: Formatter seguro
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Configurar logger específico de Genesis
    genesis_logger = logging.getLogger("genesis_engine")
    genesis_logger.setLevel(log_level)
    
    return genesis_logger

def safe_log_message(message: str) -> str:
    """
    NUEVA FUNCIÓN: Convertir mensaje a ASCII-safe
    
    Reemplaza emojis por prefijos de texto para evitar encoding issues
    """
    emoji_replacements = {
        '🚀': '[INIT]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '🔄': '[EXEC]',
        '⚠️': '[WARN]',
        '🎯': '[TARGET]',
        '🔧': '[FIX]',
        '📝': '[DOC]',
        '🔍': '[SCAN]',
        '⚡': '[FAST]',
        '🏗️': '[BUILD]',
        '🎨': '[UI]',
        '🐳': '[DOCKER]',
        '☸️': '[K8S]',
        '📊': '[METRICS]',
        '🔥': '[HOT]',
        '💾': '[SAVE]',
        '🛑': '[STOP]',
        '🎼': '[ORCH]',
        '🤖': '[AGENT]',
        '📋': '[LIST]',
        '📄': '[FILE]',
        '🎯': '[GOAL]',
        '🛠️': '[TOOL]',
        '📈': '[GROWTH]',
        '🔐': '[SECURE]',
        '⏰': '[TIME]',
        '💡': '[IDEA]',
        '🌟': '[STAR]',
        '🚨': '[ALERT]',
        '🔬': '[TEST]',
        '📚': '[DOCS]',
        '🎪': '[DEMO]',
        '🏆': '[SUCCESS]',
        '🎊': '[COMPLETE]'
    }
    
    safe_message = message
    for emoji, replacement in emoji_replacements.items():
        safe_message = safe_message.replace(emoji, replacement)
    
    return safe_message

def get_safe_logger(name: str = "genesis_engine") -> logging.Logger:
    """
    NUEVA FUNCIÓN: Obtener logger con mensajes ASCII-safe
    
    Wrapper que automáticamente convierte emojis a prefijos ASCII
    """
    base_logger = get_logger(name)
    
    class SafeLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return safe_log_message(str(msg)), kwargs
    
    return SafeLoggerAdapter(base_logger, {})

# CORRECCIÓN: Configurar logging básico al importar el módulo con manejo de errores
try:
    setup_basic_logging()
except Exception as e:
    # Fallback básico si falla la configuración
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print(f"[WARN] Fallback logging activated due to: {e}")