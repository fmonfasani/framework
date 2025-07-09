from pathlib import Path
import sys
import types
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from genesis_engine.cli.main import app
from genesis_engine.cli import commands as cmd_modules


def test_genesis_deploy(monkeypatch):
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

    runner = CliRunner()
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0
    assert "Despliegue completado" in result.output


