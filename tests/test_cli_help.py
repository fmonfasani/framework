from pathlib import Path
import sys
import types
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def test_help_command(capsys):
    # Prepare minimal genesis_engine package for imports
    pkg = types.ModuleType('genesis_engine')
    pkg.__path__ = [str(ROOT)]
    pkg.__version__ = '0.0.0'
    sys.modules['genesis_engine'] = pkg

    spec = importlib.util.spec_from_file_location(
        'genesis_engine.cli.main', ROOT / 'genesis_engine' / 'cli' / 'main.py'
    )
    cli_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli_main)

    cli_main.app(["help"], standalone_mode=False)
    captured = capsys.readouterr()
    assert "Usage" in captured.out

    del sys.modules['genesis_engine']
