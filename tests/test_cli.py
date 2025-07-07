from pathlib import Path
import sys
import types
import importlib.util
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Minimal package structure for compatibility with CLI wrappers
genesis_pkg = sys.modules.setdefault('genesis_engine', types.ModuleType('genesis_engine'))
genesis_pkg.__path__ = [str(ROOT)]
genesis_pkg.__dict__.setdefault('__version__', '0.0')
sys.modules.setdefault('genesis_engine.cli', types.ModuleType('genesis_engine.cli')).__path__ = [str(ROOT / 'cli')]
sys.modules.setdefault('genesis_engine.cli.ui', types.ModuleType('genesis_engine.cli.ui')).__path__ = [str(ROOT / 'genesis_engine' / 'cli' / 'ui')]

spec_console = importlib.util.spec_from_file_location(
    'genesis_engine.cli.ui.console',
    ROOT / 'genesis_engine' / 'cli' / 'ui' / 'console.py'
)
console_mod = importlib.util.module_from_spec(spec_console)
sys.modules['genesis_engine.cli.ui.console'] = console_mod
spec_console.loader.exec_module(console_mod)

import importlib.util

spec = importlib.util.spec_from_file_location(
    'genesis_engine.cli.main',
    ROOT / 'genesis_engine' / 'cli' / 'main.py'
)
_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_main)
app = _main.app

from genesis_engine.cli import commands as cmd_modules


def test_genesis_help():
    runner = CliRunner()
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0
    assert 'Genesis Engine' in result.output


def test_genesis_doctor(monkeypatch):
    runner = CliRunner()

    def dummy_run(*args, **kwargs):
        return types.SimpleNamespace(returncode=0, stdout='tool version 1')

    monkeypatch.setattr(cmd_modules.doctor.subprocess, 'run', dummy_run)
    import requests
    monkeypatch.setattr(requests, 'get', lambda *a, **kw: types.SimpleNamespace(status_code=200))

    result = runner.invoke(app, ['doctor'])
    assert result.exit_code == 0
