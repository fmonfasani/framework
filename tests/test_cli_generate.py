from pathlib import Path
import types
from typer.testing import CliRunner
from unittest.mock import Mock, AsyncMock

from genesis_engine.agents.backend import BackendAgent

import yaml

from genesis_engine.cli.main import app
from genesis_engine.cli import commands as cmd_modules


def test_genesis_generate(monkeypatch, tmp_path):
    mock_backend_cls = Mock(spec=BackendAgent)
    mock_backend = mock_backend_cls.return_value
    mock_backend.initialize = AsyncMock()
    mock_backend.execute_task = AsyncMock(return_value={"generated_files": ["models/user.py"]})

    monkeypatch.setattr(cmd_modules.generate, 'BackendAgent', mock_backend_cls)

    # create temporary genesis.json so CLI detects a project
    genesis_file = tmp_path / "genesis.json"
    genesis_file.write_text("{}")
    monkeypatch.chdir(tmp_path)

    generate_async = AsyncMock(return_value={"success": True, "files": ["models/user.py"]})
    monkeypatch.setattr("genesis_engine.cli.main._generate_async", generate_async)

    runner = CliRunner()
    result = runner.invoke(app, ['generate', 'model', 'User'])
    assert result.exit_code == 0
    assert "generado exitosamente" in result.output

    generate_async.assert_awaited_once_with(
        {
            "component": "model",
            "name": "User",
            "agent": None,
            "interactive": True,
        }
    )

