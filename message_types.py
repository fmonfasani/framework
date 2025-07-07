"""Compatibility wrapper for genesis_engine.mcp.message_types"""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location(
    '_real_message_types',
    Path(__file__).resolve().parent / 'genesis_engine' / 'mcp' / 'message_types.py'
)
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)
MCPRequest = _real.MCPRequest
__all__ = ['MCPRequest']
