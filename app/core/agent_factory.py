import importlib
from typing import Tuple

from langchain_core.runnables import Runnable

from app.server.config import Settings


def agent_factory(agent_template: str, settings: Settings) -> Tuple[Runnable, str]:
    try:
        module_path = f"src.agents.{agent_template}"
        agent_module = importlib.import_module(module_path)
        create_runnable_func = getattr(agent_module, "create_agent_runnable")

        # Assuming create_agent_runnable functions take google_api_key
        return create_runnable_func(settings.GOOGLE_API_KEY)
    except (ImportError, AttributeError) as e:
        raise ValueError(
            f"Could not find create_agent_runnable for template: {agent_template}"
        ) from e
