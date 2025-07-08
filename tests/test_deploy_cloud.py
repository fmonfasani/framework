import asyncio
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pkg = sys.modules.setdefault('genesis_engine', types.ModuleType('genesis_engine'))
pkg.__path__ = [str(ROOT), str(ROOT / 'genesis_engine')]
sys.modules.setdefault('genesis_engine.mcp', types.ModuleType('genesis_engine.mcp')).__path__ = [str(ROOT / 'genesis_engine' / 'mcp')]
sys.modules.setdefault('genesis_engine.agents', types.ModuleType('genesis_engine.agents')).__path__ = [str(ROOT / 'genesis_engine' / 'agents')]
sys.modules.setdefault('genesis_engine.core', types.ModuleType('genesis_engine.core')).__path__ = [str(ROOT / 'genesis_engine' / 'core')]
sys.modules.setdefault('yaml', types.ModuleType('yaml'))

spec = importlib.util.spec_from_file_location(
    'genesis_engine.agents.deploy',
    ROOT / 'genesis_engine' / 'agents' / 'deploy.py'
)
deploy_mod = importlib.util.module_from_spec(spec)
sys.modules['genesis_engine.agents.deploy'] = deploy_mod
spec.loader.exec_module(deploy_mod)

DeployAgent = deploy_mod.DeployAgent
DeploymentConfig = deploy_mod.DeploymentConfig
DeploymentTarget = deploy_mod.DeploymentTarget
DeploymentEnvironment = deploy_mod.DeploymentEnvironment


def test_deploy_to_heroku(monkeypatch, tmp_path):
    agent = DeployAgent()
    calls = []

    async def dummy(cmd, *a, **kw):
        calls.append(cmd)
        return {"success": True, "logs": ["ok"], "stdout": "https://demo.herokuapp.com"}

    monkeypatch.setattr(agent, "_run_command", dummy)
    config = DeploymentConfig(target=DeploymentTarget.HEROKU, environment=DeploymentEnvironment.DEVELOPMENT, custom_config={"app_name": "demo"})
    result = asyncio.run(agent._deploy_to_heroku(tmp_path, config))

    assert result.success
    assert result.target == DeploymentTarget.HEROKU
    assert calls


def test_deploy_to_vercel(monkeypatch, tmp_path):
    agent = DeployAgent()
    calls = []

    async def dummy(cmd, *a, **kw):
        calls.append(cmd)
        return {"success": True, "logs": ["ok"], "stdout": "https://demo.vercel.app"}

    monkeypatch.setattr(agent, "_run_command", dummy)
    config = DeploymentConfig(target=DeploymentTarget.VERCEL, environment=DeploymentEnvironment.DEVELOPMENT)
    result = asyncio.run(agent._deploy_to_vercel(tmp_path, config))

    assert result.success
    assert result.target == DeploymentTarget.VERCEL
    assert calls


def test_deploy_to_aws(monkeypatch, tmp_path):
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
    result = asyncio.run(agent._deploy_to_aws(tmp_path, config))

    assert result.success
    assert result.target == DeploymentTarget.AWS
    assert calls
    assert not (tmp_path / "archive.zip").exists()
