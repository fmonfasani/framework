from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_help_command(capsys):
    from genesis_engine.cli.main import app

    app(["help"], standalone_mode=False)
    captured = capsys.readouterr()
    assert "Usage" in captured.out
