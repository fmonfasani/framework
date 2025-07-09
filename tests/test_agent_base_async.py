import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.mcp.agent_base import GenesisAgent
from genesis_engine.mcp.message_types import MCPRequest


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

