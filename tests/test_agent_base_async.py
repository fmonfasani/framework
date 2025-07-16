import asyncio
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.tasking import create_simple_agent
from mcpturbo_core.messages import Request


@pytest.mark.asyncio
async def test_async_handler_runs_in_running_loop():
    agent = create_simple_agent("a1", "Agent")

    async def handler(request):
        await asyncio.sleep(0)
        return request.data["x"]

    agent.register_handler("act", handler)
    req = Request(
        sender="src",
        target=agent.agent_id,
        action="act",
        data={"x": 123},
        timeout=1,
    )

    result = await agent.handle_request(req)
    assert result == 123

