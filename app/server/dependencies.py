from functools import lru_cache

from langchain_core.runnables import Runnable

from agents.stateful_agent import create_agent_runnable
from app.server.config import Settings


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()


def get_agent_runnable() -> Runnable:
    settings = get_settings()
    return create_agent_runnable(settings.GOOGLE_API_KEY)
