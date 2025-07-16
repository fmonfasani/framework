from mcpturbo_core.messages import Message, MessageType


def test_mcp_message_defaults():
    msg = Message(sender="src")
    assert msg.type == MessageType.REQUEST
    assert msg.sender == "src"
    assert msg.data == {}
