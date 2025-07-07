class MCPProtocol:
    """Minimal MCP protocol stub for tests."""
    def __init__(self):
        self.running = False
        self.handlers = {}
    def start(self):
        self.running = True
    def register_handler(self, event, handler):
        self.handlers[event] = handler

mcp_protocol = MCPProtocol()
