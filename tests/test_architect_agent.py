import sys
import types
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Create minimal genesis_engine package stub
genesis_pkg = types.ModuleType("genesis_engine")
genesis_pkg.__path__ = [str(ROOT)]
sys.modules.setdefault("genesis_engine", genesis_pkg)

# Stub BaseAgent
base_agent_stub = types.ModuleType("genesis_engine.agents.base_agent")
class BaseAgent:
    def __init__(self, name=None, version="1.0.0"):
        self.name = name
        self.version = version
        self.capabilities = []
        self.metadata = {}
    def add_capability(self, c):
        self.capabilities.append(c)
    def register_handler(self, action, handler):
        pass
    def set_metadata(self, k, v):
        self.metadata[k] = v
base_agent_stub.BaseAgent = BaseAgent
sys.modules.setdefault("genesis_engine.agents", types.ModuleType("genesis_engine.agents"))
sys.modules["genesis_engine.agents"].__path__ = [str(ROOT)]
sys.modules.setdefault("genesis_engine.agents.base_agent", base_agent_stub)

# Minimal BackendAgent stub required for orchestrator import
backend_stub = types.ModuleType("genesis_engine.agents.backend")
class BackendAgent: ...
backend_stub.BackendAgent = BackendAgent
sys.modules.setdefault("genesis_engine.agents.backend", backend_stub)

# Stub MCP agent_base
agent_base_stub = types.ModuleType("genesis_engine.mcp.agent_base")
@dataclass
class AgentTask:
    id: str
    name: str
    description: str = ""
    params: dict = field(default_factory=dict)
    priority: int = 0
@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: dict | None = None
    error: str | None = None
class GenesisAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, agent_type: str, version: str = "1.0.0"):
        super().__init__(name=name, version=version)
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.handlers = {}
    def add_capability(self, cap):
        super().add_capability(cap)
    def register_handler(self, act, handler):
        self.handlers[act] = handler
    def set_metadata(self, k, v):
        super().set_metadata(k, v)
agent_base_stub.AgentTask = AgentTask
agent_base_stub.TaskResult = TaskResult
agent_base_stub.GenesisAgent = GenesisAgent
sys.modules.setdefault("genesis_engine.mcp", types.ModuleType("genesis_engine.mcp"))
sys.modules["genesis_engine.mcp"].__path__ = [str(ROOT)]
sys.modules.setdefault("genesis_engine.mcp.agent_base", agent_base_stub)

# Load config module required by ArchitectAgent
core_pkg = types.ModuleType("genesis_engine.core")
core_pkg.__path__ = [str(ROOT / "genesis_engine" / "core")]
sys.modules.setdefault("genesis_engine.core", core_pkg)
import importlib.util
config_spec = importlib.util.spec_from_file_location(
    "genesis_engine.core.config",
    ROOT / "genesis_engine" / "core" / "config.py",
)
config_mod = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_mod)
sys.modules["genesis_engine.core.config"] = config_mod

# Expose CLI console module used by orchestrator
cli_pkg = types.ModuleType("genesis_engine.cli")
cli_pkg.__path__ = [str(ROOT / "cli")]
sys.modules.setdefault("genesis_engine.cli", cli_pkg)
cli_ui_pkg = types.ModuleType("genesis_engine.cli.ui")
cli_ui_pkg.__path__ = [str(ROOT / "cli" / "ui")]
sys.modules.setdefault("genesis_engine.cli.ui", cli_ui_pkg)
console_spec = importlib.util.spec_from_file_location(
    "genesis_engine.cli.ui.console",
    ROOT / "genesis_engine" / "cli" / "ui" / "console.py",
)
console_mod = importlib.util.module_from_spec(console_spec)
console_spec.loader.exec_module(console_mod)
sys.modules["genesis_engine.cli.ui.console"] = console_mod

# Import the real ArchitectAgent implementation
spec = Path(ROOT / "genesis_engine" / "agents" / "architect.py")
module_name = "_architect_module"
import importlib.util
spec_loader = importlib.util.spec_from_file_location(module_name, spec)
arch_mod = importlib.util.module_from_spec(spec_loader)
spec_loader.loader.exec_module(arch_mod)
sys.modules["genesis_engine.agents.architect"] = arch_mod
ArchitectAgent = arch_mod.ArchitectAgent


def test_architect_agent_instantiation():
    agent = ArchitectAgent()
    assert agent.name == "ArchitectAgent"
