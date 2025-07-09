import asyncio
import sys
import types
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Minimal package setup similar to other tests
pkg = sys.modules.setdefault("genesis_engine", types.ModuleType("genesis_engine"))
pkg.__path__ = [str(ROOT), str(ROOT / "genesis_engine")]
sys.modules.setdefault("genesis_engine.mcp", types.ModuleType("genesis_engine.mcp")).__path__ = [str(ROOT / "genesis_engine" / "mcp")]
sys.modules.setdefault("genesis_engine.agents", types.ModuleType("genesis_engine.agents")).__path__ = [str(ROOT / "genesis_engine" / "agents")]
sys.modules.setdefault("genesis_engine.core", types.ModuleType("genesis_engine.core")).__path__ = [str(ROOT / "genesis_engine" / "core")]
sys.modules.setdefault("yaml", types.ModuleType("yaml"))

spec_msg = importlib.util.spec_from_file_location(
    "genesis_engine.mcp.message_types", ROOT / "genesis_engine" / "mcp" / "message_types.py"
)
msg_mod = importlib.util.module_from_spec(spec_msg)
sys.modules["genesis_engine.mcp.message_types"] = msg_mod
spec_msg.loader.exec_module(msg_mod)
MCPRequest = msg_mod.MCPRequest

spec_agent = importlib.util.spec_from_file_location(
    "genesis_engine.mcp.agent_base", ROOT / "genesis_engine" / "mcp" / "agent_base.py"
)
agent_mod = importlib.util.module_from_spec(spec_agent)
sys.modules["genesis_engine.mcp.agent_base"] = agent_mod
spec_agent.loader.exec_module(agent_mod)
GenesisAgent = agent_mod.GenesisAgent


def test_async_handler_runs_in_running_loop():
    agent = GenesisAgent(agent_id="a1", name="Agent", agent_type="test")

    async def handler(data):
        await asyncio.sleep(0)
        return data["x"]

    agent.register_handler("act", handler)
    req = MCPRequest(
        sender_agent="src",
        target_agent=agent.agent_id,
        action="act",
        data={"x": 123},
        timeout=1,
    )

    async def run():
        result = await agent.handle_request(req)
        assert result == 123

    asyncio.run(run())

