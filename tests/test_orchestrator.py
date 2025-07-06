import sys
from pathlib import Path
import types
import importlib.util

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

# Minimal package structure for imports used in tests
genesis_pkg = types.ModuleType("genesis_engine")
genesis_pkg.__path__ = [str(repo_root)]
sys.modules.setdefault("genesis_engine", genesis_pkg)

# Load MCP protocol with default instance if missing
spec = importlib.util.spec_from_file_location(
    "genesis_engine.mcp.protocol", repo_root / "mcp" / "protocol.py"
)
protocol_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol_mod)
if not hasattr(protocol_mod, "mcp_protocol"):
    protocol_mod.mcp_protocol = protocol_mod.MCPProtocol()
sys.modules["genesis_engine.mcp"] = types.ModuleType("genesis_engine.mcp")
sys.modules["genesis_engine.mcp"].__path__ = [str(repo_root / "mcp")]
sys.modules["genesis_engine.mcp.protocol"] = protocol_mod

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
