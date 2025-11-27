# src/session.py
import asyncio
from typing import Any

from langchain_core.messages import HumanMessage

from src.agents.stateful_deep_agent import CustomState, agent_runnable


class AgentSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
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
            input_state: dict[str, Any] = {
                "messages": self._state.messages + [HumanMessage(content=text)],
                "user_name": self._state.user_name,
            }

            new_state: CustomState = await agent_runnable.ainvoke(input_state)
            self._state = new_state

            # extract last AI message
            reply = ""
            for msg in reversed(new_state.messages):
                if msg.type == "ai" or msg.__class__.__name__.lower().startswith(
                    "aimessage"
                ):
                    reply = msg.content
                    break

            return reply
