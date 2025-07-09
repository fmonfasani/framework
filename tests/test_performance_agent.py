from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.agents.performance import PerformanceAgent


def make_agent():
    return PerformanceAgent()


@pytest.mark.asyncio
async def test_security_audit_detects_issues(tmp_path):
    file = tmp_path / "main.py"
    file.write_text("password = '123'\nprint(eval('1+1'))\n")
    agent = make_agent()
    result = await agent._perform_security_audit({"project_path": tmp_path})
    assert result["issues"]
    assert result["files_modified"] == [str(file)]
    report = Path(result["report_file"])
    assert report.exists()
    assert "# TODO" in file.read_text()


@pytest.mark.asyncio
async def test_optimize_database_queries(tmp_path):
    file = tmp_path / "db.py"
    file.write_text("db.execute('SELECT * FROM users')\nfor u in User.objects.all():\n    pass\n")
    agent = make_agent()
    result = await agent._optimize_database_queries({"project_path": tmp_path})
    assert result["optimizations"]
    assert result["files_modified"] == [str(file)]
    assert "# TODO" in file.read_text()


@pytest.mark.asyncio
async def test_setup_caching_creates_config(tmp_path):
    agent = make_agent()
    result = await agent._setup_caching_strategy({"project_path": tmp_path})
    config = tmp_path / "cache_config.json"
    assert result["optimizations"]
    assert result["files_modified"] == [str(config)]
    assert config.exists()


@pytest.mark.asyncio
async def test_setup_monitoring_creates_config(tmp_path):
    agent = make_agent()
    result = await agent._setup_performance_monitoring({"project_path": tmp_path})
    config = tmp_path / ".genesis" / "monitoring.json"
    assert result["optimizations"]
    assert result["files_modified"] == [str(config)]
    assert config.exists()
