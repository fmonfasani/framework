from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.agents.architect import ArchitectAgent


def test_architect_agent_instantiation():
    agent = ArchitectAgent()
    assert agent.name == "ArchitectAgent"
