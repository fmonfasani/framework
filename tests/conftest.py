from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def genesis_root():
    """Return repository root directory."""
    return Path(__file__).resolve().parents[1]

import yaml
import genesis_engine
