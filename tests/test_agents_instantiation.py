from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.agents.architect import ArchitectAgent
from genesis_engine.agents.backend import BackendAgent
from genesis_engine.agents.devops import DevOpsAgent
from genesis_engine.agents.deploy import DeployAgent
from genesis_engine.agents.frontend import FrontendAgent
from genesis_engine.agents.performance import PerformanceAgent
from genesis_engine.agents.ai_ready import AIReadyAgent


def test_agents_can_instantiate():
    """All main agent classes should initialize without errors."""
    ArchitectAgent()
    BackendAgent()
    DevOpsAgent()
    DeployAgent()
    FrontendAgent()
    PerformanceAgent()
    AIReadyAgent()
