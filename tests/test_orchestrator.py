import asyncio
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, ProjectGenerationRequest


def test_execute_project_generation():
    orchestrator = CoreOrchestrator()
    request = ProjectGenerationRequest(name="demo", template="saas", features=["x"])
    result = asyncio.run(orchestrator.execute_project_generation(request))
    assert result.success
    assert "steps" in result.data
