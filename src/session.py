# src/session.py
import asyncio
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import Runnable

from src.agents.stateful_agent import CustomState


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


class DeepAgentSession(AgentSession):
    """
    Session wrapper for DeepAgents / LangGraph-based agents.

    - We do NOT manage the full CustomState here.
    - We only send the *new* user message and a stable thread_id.
    - LangGraph + its checkpointer hold the true agent state.
    """

    def __init__(
        self,
        session_id: str,
        agent_runnable: Runnable,
        thread_id: Optional[str] = None,
    ):
        # Keep session_id & agent_runnable from base, but don't rely on base _state layout
        super().__init__(session_id, agent_runnable)

        # For DeepAgents, this thread_id is what binds all turns together
        self.thread_id = thread_id or session_id

        # We'll repurpose _state to store the last returned messages for inspection/UI.
        # Not a "real" CustomState anymore, but still useful.
        self._state: Dict[str, Any] = {"messages": []}

    @property
    def messages(self) -> List[BaseMessage]:
        """Convenience: access the last known messages list."""
        return self._state.get("messages", [])

    async def chat(self, text: str) -> str:
        """
        Run a single turn for a deep agent.

        Only sends the new user message; the underlying LangGraph graph
        reconstructs full state from the checkpointer using thread_id.
        """
        async with self._lock:
            # 1) Build input: ONLY the new user message
            input_payload = {
                "messages": [
                    HumanMessage(content=text),
                ]
            }

            config = {
                "configurable": {
                    "thread_id": self.thread_id,
                }
            }

            # 2) Invoke the deep agent graph
            result: Dict[str, Any] = await self.agent_runnable.ainvoke(
                input_payload,
                config=config,
            )

            # deepagents create_deep_agent returns a dict with "messages"
            messages: List[BaseMessage] = result.get("messages", [])
            self._state["messages"] = messages

            # 3) Extract last AI message (like in AgentSession)
            reply = ""
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) or (
                    getattr(msg, "type", "") == "ai"
                    or msg.__class__.__name__.lower().startswith("aimessage")
                ):
                    reply = msg.content
                    break

            return reply
