import sys

from genesis_engine.cli.main import app


def test_help_command(capsys):
    from genesis_engine.cli.main import app


    app(["help"], standalone_mode=False)
    captured = capsys.readouterr()
    assert "Usage" in captured.out
