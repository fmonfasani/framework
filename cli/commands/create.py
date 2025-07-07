import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location('real', Path(__file__).resolve().parents[2] / 'genesis_engine' / 'cli' / 'commands' / 'create.py')
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)
real_module = _real
for name in dir(_real):
    if not name.startswith('_'):
        globals()[name] = getattr(_real, name)
