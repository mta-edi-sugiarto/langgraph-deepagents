import pytest

from app.core.agent_factory import agent_factory
from app.server.config import Settings


def test_agent_factory_stateful_agent():
    settings = Settings(GOOGLE_API_KEY="test")
    runnable, agent_type = agent_factory("stateful_agent", settings)
    assert agent_type == "agent"
    assert hasattr(runnable, "astream")


def test_agent_factory_stateful_deep_agent():
    settings = Settings(GOOGLE_API_KEY="test")
    runnable, agent_type = agent_factory("stateful_deep_agent", settings)
    assert agent_type == "deepagent"
    assert hasattr(runnable, "astream")


def test_agent_factory_unknown_agent():
    settings = Settings(GOOGLE_API_KEY="test")
    with pytest.raises(ValueError):
        agent_factory("unknown_agent", settings)
