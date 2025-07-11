

from genesis_engine.agents.architect import ArchitectAgent


def test_architect_agent_instantiation():
    agent = ArchitectAgent()
    assert agent.name == "ArchitectAgent"
