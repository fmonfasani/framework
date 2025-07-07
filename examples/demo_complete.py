"""Minimal demonstration of the Genesis Engine CLI."""

import os
import tempfile
from pathlib import Path
from typer.testing import CliRunner

# Import the Typer application powering the ``genesis`` command
from genesis_engine.cli.main import app


def main() -> None:
    """Initialize a demo project and run a follow-up command."""

    runner = CliRunner()
    # Use a temporary directory so the demo can be executed repeatedly
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # --------------------------------------------------------------
        # 1) Initialize a project with default options
        # --------------------------------------------------------------
        result_init = runner.invoke(
            app,
            ["init", "demo_app", "--no-interactive"],
        )
        print(result_init.stdout)
        # Expected output (truncated):
        #   🚀 Genesis Engine - Inicializando Proyecto
        #   ✅ ¡Proyecto 'demo_app' creado exitosamente!

        # Enter the new project directory and run ``genesis doctor``
        os.chdir(Path("demo_app"))
        result_doctor = runner.invoke(app, ["doctor"])
        print(result_doctor.stdout)
        # Expected output includes a table with environment checks


if __name__ == "__main__":
    main()
