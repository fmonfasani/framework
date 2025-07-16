import sys
import types
import importlib.util
import logging
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub core.config before importing TemplateEngine
spec = importlib.util.spec_from_file_location(
    'genesis_engine.core.config', ROOT / 'genesis_engine' / 'core' / 'config.py'
)
config_mod = importlib.util.module_from_spec(spec)
sys.modules['genesis_engine.core.config'] = config_mod
spec.loader.exec_module(config_mod)
config_mod.GenesisConfig.get = classmethod(lambda cls, key, default=None: default)

# Stub core.logging to avoid circular import
logging_mod = types.ModuleType('genesis_engine.core.logging')
logging_mod.get_logger = lambda name, level=None: logging.getLogger(name)
sys.modules['genesis_engine.core.logging'] = logging_mod

from genesis_engine.agents.ai_ready import AIReadyAgent
import genesis_engine.agents.ai_ready as ai_mod
ai_mod.asyncio = __import__('asyncio')
from genesis_engine.tasking import AgentTask


@pytest.mark.asyncio
async def test_ai_ready_agent_main_handlers(tmp_path):
    agent = AIReadyAgent()
    # Provide missing set_metadata method
    agent.metadata = {}
    agent.set_metadata = lambda k, v: agent.metadata.__setitem__(k, v)

    await agent.initialize()
    assert agent.metadata.get("specialization") == "ai_integration"

    cfg = agent._extract_ai_config({})
    task = AgentTask(name="setup_embeddings", params={"project_path": tmp_path, "config": cfg})
    result = await agent.execute_task(task)

    expected_file = tmp_path / "backend" / "app" / "ai" / "embedding_service.py"
    assert expected_file.exists()
    assert result == [str(expected_file)]
