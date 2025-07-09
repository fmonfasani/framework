from pathlib import Path
import sys
import types
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.cli.main import app
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
    monkeypatch.setattr(cmd_modules.utils.subprocess, 'run', dummy_run)
    import requests
    monkeypatch.setattr(requests, 'get', lambda *a, **kw: types.SimpleNamespace(status_code=200))

    result = runner.invoke(app, ['doctor'])
    assert result.exit_code == 0
