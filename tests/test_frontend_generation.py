from pathlib import Path
import sys
import json

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
    result = agent._generate_complete_frontend(params)

    expected = {
        tmp_path / "package.json",
        tmp_path / "index.html",
        tmp_path / "src" / "App.tsx",
        tmp_path / "src" / "main.tsx",
    }

    generated = set(Path(p) for p in result["generated_files"])
    assert expected <= generated

    assert (tmp_path / "tailwind.config.js") in generated
    assert (tmp_path / "styles" / "globals.css") in generated
    assert result["framework"] == "react"
    assert "DemoApp" in (tmp_path / "src" / "App.tsx").read_text()


def test_generate_nextjs_package_json_contains_next(tmp_path):
    agent = make_agent()
    schema = {"project_name": "DemoNext", "description": "Demo"}
    params = {"schema": schema, "framework": "nextjs", "output_path": tmp_path}
    result = agent._generate_complete_frontend(params)

    package_json = tmp_path / "package.json"
    data = json.loads(package_json.read_text())
    assert "next" in data.get("dependencies", {})

