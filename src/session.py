# src/session.py
import asyncio
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from agents.stateful_agent import CustomState


class AgentSession:
    def __init__(self, session_id: str, agent_runnable: Runnable):
        self.session_id = session_id
        self.agent_runnable = agent_runnable
        self._state: CustomState = CustomState(
            messages=[],
            user_name=None,
        )
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CustomState:
        return self._state

    async def chat(self, text: str) -> str:
        """Run a single turn and update internal state."""
        async with self._lock:
            base_state = dict(self._state)

            base_state["messages"] = base_state.get("messages", []) + [
                HumanMessage(content=text)
            ]
            new_state: CustomState = await self.agent_runnable.ainvoke(base_state)
            self._state = new_state

            # extract last AI message
            reply = ""
            for msg in reversed(new_state["messages"]):
                if msg.type == "ai" or msg.__class__.__name__.lower().startswith(
                    "aimessage"
                ):
                    reply = msg.content
                    break

            return reply
