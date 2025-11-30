import pytest
from langchain_core.runnables import Runnable

from app.core.session_manager import SessionManager


class MockRunnable(Runnable):
    def invoke(self, *args, **kwargs):
        pass

    def astream(self, *args, **kwargs):
        pass


@pytest.fixture
def manager():
    return SessionManager()


def test_create_session(manager: SessionManager):
    runnable = MockRunnable()
    agent_id = manager.create_session(runnable, "agent")
    assert isinstance(agent_id, str)
    assert manager.get_session(agent_id) is not None


def test_get_session(manager: SessionManager):
    runnable = MockRunnable()
    agent_id = manager.create_session(runnable, "agent")
    session = manager.get_session(agent_id)
    assert session is not None
    assert session.session_id == agent_id


def test_list_sessions(manager: SessionManager):
    runnable = MockRunnable()
    agent_id1 = manager.create_session(runnable, "agent")
    agent_id2 = manager.create_session(runnable, "deepagent")
    sessions = manager.list_sessions()
    assert isinstance(sessions, list)
    assert agent_id1 in sessions
    assert agent_id2 in sessions


def test_delete_session(manager: SessionManager):
    runnable = MockRunnable()
    agent_id = manager.create_session(runnable, "agent")
    assert manager.delete_session(agent_id) is True
    assert manager.get_session(agent_id) is None
    assert manager.delete_session("unknown_id") is False
