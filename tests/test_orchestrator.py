import sys
from pathlib import Path
import types
import importlib.util

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

# Minimal package structure for imports used in tests
genesis_pkg = types.ModuleType("genesis_engine")
genesis_pkg.__path__ = [str(repo_root), str(repo_root / 'genesis_engine')]
sys.modules.setdefault("genesis_engine", genesis_pkg)

# Load MCP protocol with default instance if missing
spec = importlib.util.spec_from_file_location(
    "genesis_engine.mcp.protocol", repo_root / "genesis_engine" / "mcp" / "protocol.py"
)
protocol_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol_mod)
if not hasattr(protocol_mod, "mcp_protocol"):
    protocol_mod.mcp_protocol = protocol_mod.MCPProtocol()
sys.modules["genesis_engine.mcp"] = types.ModuleType("genesis_engine.mcp")
sys.modules["genesis_engine.mcp"].__path__ = [str(repo_root / "genesis_engine" / "mcp")]
sys.modules["genesis_engine.mcp.protocol"] = protocol_mod

sys.modules.setdefault("genesis_engine.cli", types.ModuleType("genesis_engine.cli")).__path__ = [str(repo_root / "genesis_engine" / "cli")]
sys.modules.setdefault("genesis_engine.cli.ui", types.ModuleType("genesis_engine.cli.ui")).__path__ = [str(repo_root / "genesis_engine" / "cli" / "ui")]
sys.modules.setdefault("genesis_engine.cli.commands", types.ModuleType("genesis_engine.cli.commands")).__path__ = [str(repo_root / "genesis_engine" / "cli" / "commands")]
sys.modules.setdefault("genesis_engine.core", types.ModuleType("genesis_engine.core")).__path__ = [str(repo_root / 'genesis_engine' / 'core')]
sys.modules.setdefault("genesis_engine.agents", types.ModuleType("genesis_engine.agents")).__path__ = [str(repo_root / 'genesis_engine' / 'agents')]
sys.modules.setdefault('yaml', types.ModuleType('yaml'))
spec_console = importlib.util.spec_from_file_location(
    "genesis_engine.cli.ui.console", repo_root / "genesis_engine" / "cli" / "ui" / "console.py"
)
console_mod = importlib.util.module_from_spec(spec_console)
spec_console.loader.exec_module(console_mod)
sys.modules["genesis_engine.cli.ui.console"] = console_mod

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
