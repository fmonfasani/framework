from pathlib import Path
import sys
import types
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Minimal genesis_engine package stub
pkg = sys.modules.setdefault('genesis_engine', types.ModuleType('genesis_engine'))
pkg.__path__ = [str(ROOT / 'genesis_engine')]

# Load required submodules directly
spec_logging = importlib.util.spec_from_file_location(
    'genesis_engine.core.logging',
    ROOT / 'genesis_engine' / 'core' / 'logging.py'
)
logging_mod = importlib.util.module_from_spec(spec_logging)
sys.modules['genesis_engine.core.logging'] = logging_mod
spec_logging.loader.exec_module(logging_mod)

spec_validation = importlib.util.spec_from_file_location(
    'genesis_engine.utils.validation',
    ROOT / 'genesis_engine' / 'utils' / 'validation.py'
)
validation_mod = importlib.util.module_from_spec(spec_validation)
sys.modules['genesis_engine.utils.validation'] = validation_mod
spec_validation.loader.exec_module(validation_mod)

EnvironmentValidator = validation_mod.EnvironmentValidator


def test_multiple_package_managers(monkeypatch):
    def dummy_run(cmd, *a, **kw):
        tool = cmd[0]
        return types.SimpleNamespace(returncode=0, stdout=f'{tool}-1.0')

    monkeypatch.setattr(validation_mod.subprocess, 'run', dummy_run)

    validator = EnvironmentValidator()
    validator._check_development_tools()

    found = [r.name for r in validator.results]
    assert 'NPM Package Manager' in found
    assert 'YARN Package Manager' in found
    assert 'PNPM Package Manager' in found

