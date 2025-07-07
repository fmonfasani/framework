import logging
from typing import Optional

DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LEVEL = logging.INFO


def configure_logging(level: int = DEFAULT_LEVEL, fmt: str = DEFAULT_FORMAT) -> None:
    """Configure the root logger once with a standard stream handler."""
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt))
        root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Return a logger configured with the global settings."""
    configure_logging(level or DEFAULT_LEVEL)
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger
