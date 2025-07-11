from pathlib import Path

from genesis_engine.utils.validation import EnvironmentValidator
import genesis_engine.utils.validation as validation_mod
import types


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

