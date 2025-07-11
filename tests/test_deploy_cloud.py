from pathlib import Path
import pytest

import genesis_engine.agents.deploy as deploy_mod
from genesis_engine.agents.deploy import (
    DeployAgent,
    DeploymentConfig,
    DeploymentTarget,
    DeploymentEnvironment,
)


@pytest.mark.asyncio
async def test_deploy_to_heroku(monkeypatch, tmp_path):
    agent = DeployAgent()
    calls = []

    async def dummy(cmd, *a, **kw):
        calls.append(cmd)
        return {"success": True, "logs": ["ok"], "stdout": "https://demo.herokuapp.com"}

    monkeypatch.setattr(agent, "_run_command", dummy)
    config = DeploymentConfig(target=DeploymentTarget.HEROKU, environment=DeploymentEnvironment.DEVELOPMENT, custom_config={"app_name": "demo"})
    result = await agent._deploy_to_heroku(tmp_path, config)

    assert result.success
    assert result.target == DeploymentTarget.HEROKU
    assert calls


@pytest.mark.asyncio
async def test_deploy_to_vercel(monkeypatch, tmp_path):
    agent = DeployAgent()
    calls = []

    async def dummy(cmd, *a, **kw):
        calls.append(cmd)
        return {"success": True, "logs": ["ok"], "stdout": "https://demo.vercel.app"}

    monkeypatch.setattr(agent, "_run_command", dummy)
    config = DeploymentConfig(target=DeploymentTarget.VERCEL, environment=DeploymentEnvironment.DEVELOPMENT)
    result = await agent._deploy_to_vercel(tmp_path, config)

    assert result.success
    assert result.target == DeploymentTarget.VERCEL
    assert calls


@pytest.mark.asyncio
async def test_deploy_to_aws(monkeypatch, tmp_path):
    agent = DeployAgent()
    (tmp_path / "file.txt").write_text("data")
    calls = []

    async def dummy(cmd, *a, **kw):
        calls.append(cmd)
        return {"success": True, "logs": ["ok"]}

    def fake_make_archive(base, fmt, root_dir):
        archive = Path(root_dir) / "archive.zip"
        archive.write_text("zip")
        return str(archive)

    monkeypatch.setattr(agent, "_run_command", dummy)
    monkeypatch.setattr(deploy_mod.shutil, "make_archive", fake_make_archive)

    config = DeploymentConfig(target=DeploymentTarget.AWS, environment=DeploymentEnvironment.DEVELOPMENT, custom_config={"app_name": "demo", "bucket": "bkt"})
    result = await agent._deploy_to_aws(tmp_path, config)

    assert result.success
    assert result.target == DeploymentTarget.AWS
    assert calls
    assert not (tmp_path / "archive.zip").exists()
