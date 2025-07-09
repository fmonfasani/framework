from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.cli.main import app


def test_help_command(capsys):
    app(["help"], standalone_mode=False)
    captured = capsys.readouterr()
    assert "Usage" in captured.out
