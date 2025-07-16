import pytest
from mcpturbo_core import MCPProtocol

@pytest.mark.asyncio
async def test_protocol_tasks_cleanup():
    protocol = MCPProtocol()
    await protocol.start()
    assert protocol.running
    await protocol.stop()
    assert not protocol.running
