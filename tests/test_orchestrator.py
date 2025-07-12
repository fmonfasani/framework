import sys
import asyncio
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from genesis_engine.core.orchestrator import GenesisOrchestrator
from genesis_engine.agents.devops import DevOpsAgent


class DummyArchitect:
    async def execute_task(self, task):
        return {"pattern": "layered"}


def test_process_request_success(monkeypatch):
    orchestrator = GenesisOrchestrator()
    monkeypatch.setattr(
        orchestrator, "agents", {"architect": DummyArchitect()}, raising=False
    )
    result = orchestrator.process_request(
        {
            "type": "design_architecture",
            "agent": "architect",
            "data": {"requirements": {}, "pattern": "layered", "type": "web_app"},
        }
    )
    assert result["success"] is True
    assert "pattern" in result["result"]


def test_process_request_unknown_agent():
    orchestrator = GenesisOrchestrator()
    result = orchestrator.process_request({"agent": "unknown", "type": "noop"})
    assert result["success"] is False

class DummyOrchestratorForInit:
    def __init__(self):
        self.requests = []
    def process_request(self, req):
        self.requests.append(req)
        return {"success": True, "result": {}}

class DummyTemplateEngine:
    def generate_project(self, template_name, output_dir, context):
        return []

def test_init_command_calls_design_architecture(monkeypatch, tmp_path):
    from genesis_engine.cli.commands import init as init_module
    orch = DummyOrchestratorForInit()
    tmpl = DummyTemplateEngine()
    monkeypatch.setattr(init_module.real_module, "GenesisOrchestrator", lambda: orch)
    monkeypatch.setattr(init_module.real_module, "TemplateEngine", lambda: tmpl)
    init_module.init_command("demo", no_interactive=True, output_dir=str(tmp_path))
    assert any(req.get("type") == "design_architecture" for req in orch.requests)


def test_validate_generated_project_without_stack(tmp_path):
    """Project validation should pass even when stack info is missing."""
    agent = DevOpsAgent()
    config = agent._extract_devops_config({})
    schema = {"project_name": "demo", "stack": {"frontend": "nextjs"}}
    backend_app = tmp_path / "backend" / "app"
    backend_app.mkdir(parents=True)
    (backend_app / "main.py").write_text("print('hi')")
    (tmp_path / "backend" / "requirements.txt").write_text("fastapi")
    frontend_app = tmp_path / "frontend" / "app"
    frontend_app.mkdir(parents=True)
    (frontend_app / "page.tsx").write_text("page")
    (tmp_path / "frontend" / "package.json").write_text("{}")
    asyncio.run(
        agent._generate_docker_compose_improved(
            tmp_path, schema, config, {}
        )
    )
    orchestrator = GenesisOrchestrator()
    orchestrator._validate_generated_project(tmp_path)
