from pathlib import Path
import sys
import types
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from genesis_engine.cli.main import app
from genesis_engine.cli import commands as cmd_modules


def test_genesis_generate(monkeypatch):
    class DummyBackendAgent:
        async def initialize(self):
            pass

        async def execute_task(self, task):
            return {"generated_files": ["models/user.py"]}

    monkeypatch.setattr(cmd_modules.generate, 'BackendAgent', DummyBackendAgent)

    runner = CliRunner()
    result = runner.invoke(app, ['generate', 'model', 'User'])
    assert result.exit_code == 0
    assert 'Generación completada' in result.output

