import types
from typer.testing import CliRunner
from unittest.mock import Mock, AsyncMock

from genesis_engine.agents.deploy import DeployAgent

import yaml

from genesis_engine.cli.main import app
from genesis_engine.cli import commands as cmd_modules


def test_genesis_deploy(monkeypatch, tmp_path):
    mock_deploy_cls = Mock(spec=DeployAgent)
    mock_agent = mock_deploy_cls.return_value
    mock_agent.initialize = AsyncMock()
    mock_agent.execute_task = AsyncMock(
        return_value=types.SimpleNamespace(
            success=True,
            urls=["http://localhost"],
            error=None,
        )
    )

    monkeypatch.setattr(cmd_modules.deploy, "DeployAgent", mock_deploy_cls)

    # create temporary genesis.json so CLI detects a project
    genesis_file = tmp_path / "genesis.json"
    genesis_file.write_text("{}")
    monkeypatch.chdir(tmp_path)

    deploy_async = AsyncMock(return_value={"success": True, "url": "http://localhost"})
    monkeypatch.setattr("genesis_engine.cli.main._deploy_async", deploy_async)

    runner = CliRunner()
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0
    assert "Despliegue exitoso" in result.output

    deploy_async.assert_awaited_once_with(
        {"environment": "local", "force": False, "auto_migrate": True}
    )


