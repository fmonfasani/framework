import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.agents.frontend import FrontendAgent
from genesis_engine.templates.engine import TemplateEngine

async def run_async(coro):
    return await coro


def make_agent():
    agent = FrontendAgent()
    agent.template_engine = TemplateEngine(ROOT / 'genesis_engine' / 'templates')
    return agent


def test_generate_react_frontend(tmp_path):
    agent = make_agent()
    schema = {"project_name": "DemoApp", "description": "Demo"}
    params = {"schema": schema, "framework": "react", "output_path": tmp_path}
    result = asyncio.run(agent._generate_complete_frontend(params))

    expected = {
        tmp_path / "package.json",
        tmp_path / "index.html",
        tmp_path / "src" / "App.tsx",
        tmp_path / "src" / "main.tsx",
    }

    assert set(map(Path, result["generated_files"])) == expected
    assert result["framework"] == "react"
    assert "DemoApp" in (tmp_path / "src" / "App.tsx").read_text()

