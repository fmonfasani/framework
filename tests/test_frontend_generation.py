from pathlib import Path

from genesis_engine.agents.frontend import FrontendAgent
from genesis_engine.templates.engine import TemplateEngine

async def run_async(coro):
    return await coro


def make_agent(genesis_root):
    agent = FrontendAgent()
    agent.template_engine = TemplateEngine(genesis_root / 'genesis_engine' / 'templates')
    return agent


def test_generate_react_frontend(genesis_root, tmp_path):
    agent = make_agent(genesis_root)
    schema = {"project_name": "DemoApp", "description": "Demo"}
    params = {"schema": schema, "framework": "react", "output_path": tmp_path}
    result = agent._generate_complete_frontend(params)

    expected = {
        tmp_path / "package.json",
        tmp_path / "index.html",
        tmp_path / "src" / "App.tsx",
        tmp_path / "src" / "main.tsx",
    }

    assert set(map(Path, result["generated_files"])) == expected
    assert result["framework"] == "react"
    assert "DemoApp" in (tmp_path / "src" / "App.tsx").read_text()

