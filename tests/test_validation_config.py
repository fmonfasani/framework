from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import importlib.util
import types

# Build minimal genesis_engine package stubs
genesis_pkg = sys.modules.setdefault('genesis_engine', types.ModuleType('genesis_engine'))
genesis_pkg.__path__ = [str(ROOT), str(ROOT / 'genesis_engine')]
core_pkg = sys.modules.setdefault('genesis_engine.core', types.ModuleType('genesis_engine.core'))
core_pkg.__path__ = [str(ROOT / 'genesis_engine' / 'core')]
utils_pkg = sys.modules.setdefault('genesis_engine.utils', types.ModuleType('genesis_engine.utils'))
utils_pkg.__path__ = [str(ROOT / 'genesis_engine' / 'utils')]

spec_cfg = importlib.util.spec_from_file_location(
    'genesis_engine.core.config',
    ROOT / 'genesis_engine' / 'core' / 'config.py'
)
cfg_mod = importlib.util.module_from_spec(spec_cfg)
sys.modules['genesis_engine.core.config'] = cfg_mod
spec_cfg.loader.exec_module(cfg_mod)

spec_val = importlib.util.spec_from_file_location(
    'genesis_engine.utils.validation',
    ROOT / 'genesis_engine' / 'utils' / 'validation.py'
)
val_mod = importlib.util.module_from_spec(spec_val)
sys.modules['genesis_engine.utils.validation'] = val_mod
spec_val.loader.exec_module(val_mod)

GenesisConfig = cfg_mod.GenesisConfig
ConfigValidator = val_mod.ConfigValidator
ValidationLevel = val_mod.ValidationLevel


def test_stack_validation_reflects_genesis_config():
    validator = ConfigValidator()
    test_config = {"name": "demo", "template": "saas-basic", "stack": {"backend": "laravel"}}

    # Without modifying config, validation should fail for unknown framework
    results = validator.validate_project_config(test_config)
    assert any(r.name == "Stack: backend" and r.level == ValidationLevel.ERROR for r in results)

    original = GenesisConfig.get_supported_frameworks("backend")
    try:
        # Add new framework and validate again
        GenesisConfig.set("supported_frameworks.backend", original + ["laravel"])
        results = validator.validate_project_config(test_config)
        assert any(r.name == "Stack: backend" and r.level == ValidationLevel.SUCCESS for r in results)
    finally:
        GenesisConfig.set("supported_frameworks.backend", original)
