"""Compatibility wrapper for genesis_engine.mcp.agent_base"""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location(
    '_real_agent_base',
    Path(__file__).resolve().parent / 'genesis_engine' / 'mcp' / 'agent_base.py'
)
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)
AgentTask = _real.AgentTask
TaskResult = _real.TaskResult
GenesisAgent = _real.GenesisAgent
__all__ = ['AgentTask', 'TaskResult', 'GenesisAgent']
