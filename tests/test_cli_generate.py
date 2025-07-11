from pathlib import Path
import types
from typer.testing import CliRunner

import yaml

from genesis_engine.cli.main import app
from genesis_engine.cli import commands as cmd_modules


def test_genesis_generate(monkeypatch, tmp_path):
    class DummyBackendAgent:
        async def initialize(self):
            pass

        async def execute_task(self, task):
            return {"generated_files": ["models/user.py"]}

    monkeypatch.setattr(cmd_modules.generate, 'BackendAgent', DummyBackendAgent)

    # create temporary genesis.json so CLI detects a project
    genesis_file = tmp_path / "genesis.json"
    genesis_file.write_text("{}")
    monkeypatch.chdir(tmp_path)

    async def dummy_async(config):
        return {"success": True, "files": ["models/user.py"]}

    monkeypatch.setattr("genesis_engine.cli.main._generate_async", dummy_async)

    runner = CliRunner()
    result = runner.invoke(app, ['generate', 'model', 'User'])
    assert result.exit_code == 0
    assert "generado exitosamente" in result.output

