from functools import lru_cache

from app.core.agent_factory import agent_factory
from app.core.session_manager import SessionManager, session_manager
from app.server.config import Settings


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()


def get_agent_factory():
    return agent_factory


def get_session_manager() -> SessionManager:
    return session_manager
