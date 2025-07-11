import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.agents import devops as devops_mod
from genesis_engine.agents.devops import (
    DevOpsAgent,
    DevOpsConfig,
    CIProvider,
    ContainerOrchestrator,
)


class DummyTemplateEngine:
    async def render_template(self, name, context):
        return "content"


def _default_config():
    return DevOpsConfig(
        ci_provider=CIProvider.GITHUB_ACTIONS,
        orchestrator=ContainerOrchestrator.DOCKER_COMPOSE,
        cloud_provider=None,
        monitoring_enabled=True,
        logging_enabled=True,
        ssl_enabled=True,
        backup_enabled=True,
        auto_scaling=False,
    )


def test_generate_docker_config(monkeypatch, tmp_path):
    monkeypatch.setattr(devops_mod, "TemplateEngine", DummyTemplateEngine)
    agent = DevOpsAgent()

    async def dummy_python(path, name):
        return str(path / "Dockerfile")

    async def dummy_node(path, name):
        return str(path / "Dockerfile")

    async def dummy_nextjs(path):
        return str(path / "Dockerfile")

    async def dummy_compose(out_path, schema, config, dockerfile_status):
        return str(out_path / "docker-compose.yml")

    async def dummy_ignore(out_path, stack):
        return [
            str(out_path / "backend/.dockerignore"),
            str(out_path / "frontend/.dockerignore"),
        ]

    monkeypatch.setattr(agent, "_generate_python_dockerfile", dummy_python)
    monkeypatch.setattr(agent, "_generate_node_dockerfile", dummy_node)
    monkeypatch.setattr(agent, "_generate_nextjs_dockerfile", dummy_nextjs)
    monkeypatch.setattr(agent, "_generate_docker_compose", dummy_compose)
    monkeypatch.setattr(agent, "_generate_dockerignore_files", dummy_ignore)

    schema = {"stack": {"backend": "fastapi", "frontend": "nextjs"}}
    params = {"schema": schema, "config": _default_config(), "output_path": tmp_path}

    files = asyncio.run(agent._generate_docker_config(params))
    expected = {
        str(tmp_path / "docker-compose.yml"),
        str(tmp_path / "backend/.dockerignore"),
        str(tmp_path / "frontend/.dockerignore"),
    }
    assert set(files) == expected


def test_setup_cicd_pipeline(monkeypatch, tmp_path):
    monkeypatch.setattr(devops_mod, "TemplateEngine", DummyTemplateEngine)
    agent = DevOpsAgent()

    async def dummy_ci(dir_path, schema):
        return str(dir_path / "ci.yml")

    async def dummy_cd(dir_path, schema, config):
        return str(dir_path / "cd.yml")

    async def dummy_pr(dir_path, schema):
        return str(dir_path / "pr.yml")

    monkeypatch.setattr(agent, "_generate_github_ci_workflow", dummy_ci)
    monkeypatch.setattr(agent, "_generate_github_cd_workflow", dummy_cd)
    monkeypatch.setattr(agent, "_generate_github_pr_workflow", dummy_pr)

    params = {"schema": {}, "config": _default_config(), "output_path": tmp_path}
    files = asyncio.run(agent._setup_cicd_pipeline(params))
    expected = {
        str(tmp_path / ".github/workflows/ci.yml"),
        str(tmp_path / ".github/workflows/cd.yml"),
        str(tmp_path / ".github/workflows/pr.yml"),
    }
    assert set(files) == expected
