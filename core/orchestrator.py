"""Simplified orchestrator for tests."""
import asyncio
from types import SimpleNamespace

class GenesisOrchestrator:
    def __init__(self):
        self.agents = {}

    def process_request(self, request):
        agent_key = request.get("agent")
        action = request.get("type")
        data = request.get("data", {})
        if agent_key not in self.agents:
            return {"success": False, "error": f"Unknown agent '{agent_key}'"}
        task = SimpleNamespace(name=action, params=data)
        try:
            result = asyncio.run(self.agents[agent_key].execute_task(task))
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
