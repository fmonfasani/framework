import pytest
from genesis_engine.mcp.protocol import MCPProtocol

@pytest.mark.asyncio
async def test_protocol_tasks_cleanup():
    protocol = MCPProtocol()
    await protocol.start()
    await protocol.stop()
    assert protocol.worker_task.done()
    assert protocol.metrics_task.done()
    assert protocol.circuit_task.done()
