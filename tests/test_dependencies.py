import importlib.util
import types
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    'genesis_engine.cli.commands.utils',
    ROOT / 'genesis_engine' / 'cli' / 'commands' / 'utils.py'
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


def test_check_dependencies_success(monkeypatch):
    def dummy_run(*args, **kwargs):
        return types.SimpleNamespace(returncode=0, stdout='v1')

    monkeypatch.setattr(utils.subprocess, 'run', dummy_run)
    monkeypatch.setattr(utils.sys, 'version_info', (3, 9, 0))
    assert utils.check_dependencies() is True


def test_check_dependencies_failure(monkeypatch):
    def failing_run(cmd, *a, **kw):
        if cmd[0] == 'docker':
            raise FileNotFoundError
        return types.SimpleNamespace(returncode=0, stdout='v1')

    monkeypatch.setattr(utils.subprocess, 'run', failing_run)
    monkeypatch.setattr(utils.sys, 'version_info', (3, 9, 0))

    with pytest.raises(RuntimeError):
        utils.check_dependencies()
