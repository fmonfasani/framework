"""Compatibility shim for tests expecting templates.engine"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'real_engine',
    Path(__file__).resolve().parents[1] / 'genesis_engine' / 'templates' / 'engine.py'
)
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)
TemplateEngine = _real.TemplateEngine
__all__ = ['TemplateEngine']
