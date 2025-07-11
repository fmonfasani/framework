import types
import pytest

from genesis_engine.cli.commands import utils


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
