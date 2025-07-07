from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.core.config import GenesisConfig
from genesis_engine.utils.validation import ConfigValidator, ValidationLevel


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
