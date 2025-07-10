from pathlib import Path
import sys
import types
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from genesis_engine.cli.main import app
from genesis_engine.cli import commands as cmd_modules


def test_genesis_deploy(monkeypatch, tmp_path):
    class DummyDeployAgent:
        async def initialize(self):
            pass

        async def execute_task(self, task):
            return types.SimpleNamespace(
                success=True,
                urls=["http://localhost"],
                error=None,
            )

    monkeypatch.setattr(cmd_modules.deploy, "DeployAgent", DummyDeployAgent)

    # create temporary genesis.json so CLI detects a project
    genesis_file = tmp_path / "genesis.json"
    genesis_file.write_text("{}")
    monkeypatch.chdir(tmp_path)

    async def dummy_async(config):
        return {"success": True, "url": "http://localhost"}

    monkeypatch.setattr("genesis_engine.cli.main._deploy_async", dummy_async)

    runner = CliRunner()
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0
    assert "Despliegue exitoso" in result.output


