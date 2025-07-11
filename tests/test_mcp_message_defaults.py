from genesis_engine.mcp.message_types import MCPMessage, MessageType


def test_mcp_message_defaults():
    msg = MCPMessage(sender="src", recipient="dest", action="ping")
    assert msg.type == MessageType.REQUEST
    assert msg.sender_agent == ""
    assert msg.sender == "src"
    assert msg.recipient == "dest"
    assert msg.action == "ping"
    assert msg.data == {}
