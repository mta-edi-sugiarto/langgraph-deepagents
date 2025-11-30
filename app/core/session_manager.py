import uuid
from typing import Dict, List

from langchain_core.runnables import Runnable

from src.session import AgentSession, DeepAgentSession


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, AgentSession] = {}

    def create_session(self, agent_runnable: Runnable, agent_type: str) -> str:
        agent_id = str(uuid.uuid4())
        if agent_type == "deepagent":
            session = DeepAgentSession(
                session_id=agent_id, agent_runnable=agent_runnable
            )
        else:
            session = AgentSession(session_id=agent_id, agent_runnable=agent_runnable)
        self._sessions[agent_id] = session
        return agent_id

    def get_session(self, agent_id: str) -> AgentSession | None:
        return self._sessions.get(agent_id)

    def list_sessions(self) -> List[str]:
        return list(self._sessions.keys())

    def delete_session(self, agent_id: str) -> bool:
        if agent_id in self._sessions:
            del self._sessions[agent_id]
            return True
        return False


# Singleton instance
session_manager = SessionManager()
