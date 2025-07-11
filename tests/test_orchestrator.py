from pathlib import Path

from genesis_engine.core.orchestrator import GenesisOrchestrator


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
