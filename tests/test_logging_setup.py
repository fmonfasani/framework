import importlib.util
import logging
import sys


def load_config(genesis_root):
    spec = importlib.util.spec_from_file_location(
        'genesis_engine.core.config',
        genesis_root / 'genesis_engine' / 'core' / 'config.py'
    )
    config = importlib.util.module_from_spec(spec)
    sys.modules['genesis_engine.core.config'] = config
    spec.loader.exec_module(config)
    return config.GenesisConfig


def test_setup_logging_idempotent(genesis_root, tmp_path):
    GenesisConfig = load_config(genesis_root)
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    cfg = GenesisConfig()
    original_log_dir = cfg._config.get('log_dir')
    try:
        root_logger.handlers = []

        cfg._config['log_dir'] = tmp_path
        cfg._setup_logging()
        cfg._setup_logging()

        console_handlers = [h for h in root_logger.handlers if isinstance(h, config.RichHandler)]
        file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]

        assert len(console_handlers) == 1
        assert len(file_handlers) == 1
    finally:
        root_logger.handlers = original_handlers
        cfg._config['log_dir'] = original_log_dir
