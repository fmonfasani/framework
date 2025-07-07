"""Compatibility wrapper for genesis_engine.mcp.agent_registry"""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location(
    '_real_agent_registry',
    Path(__file__).resolve().parent / 'genesis_engine' / 'mcp' / 'agent_registry.py'
)
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)
AgentRegistry = _real.AgentRegistry
__all__ = ['AgentRegistry']
