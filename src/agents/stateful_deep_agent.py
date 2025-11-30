# src/agents/stateful_deep_agent.py
import asyncio
import os
import uuid
from pprint import pprint
from typing import Tuple

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from dotenv import load_dotenv
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command


class CustomState(AgentState):
    user_name: str | None = None


class CustomStateMiddleware(AgentMiddleware[CustomState]):
    state_schema = CustomState


@tool
def get_user_info(state: CustomState, runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_name = state["user_name"]
    return "User is " + user_name


@tool
def update_user_info(
    name: str,
    state: CustomState,
    runtime: ToolRuntime,
) -> Command:
    """Update the user's name in state. This has to be run when the user is declaring their identity.

    Args:
        name: The user's name, parsed from the conversation.
    """
    state["user_name"] = name
    return Command(
        update={
            "user_name": name,
            "messages": [
                ToolMessage(
                    "Successfully updated user information",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def diagnose_user(state: CustomState, runtime: ToolRuntime) -> str | Command:
    """Look up a diagnosis based on the current user_name in state."""
    user_name = state.get("user_name", None)

    # 1) No name yet → ask the model to call update_user_info
    if user_name is None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        ("You don't know the user's name yet. "),
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    # 2) We have a name → compute diagnosis
    if user_name == "John":
        diagnosis = "healthy"
    else:
        diagnosis = "unidentified"

    return f"Diagnosis for {user_name}: {diagnosis}"


system_prompt = """
You are an assistant which can look up user info and their diagnosis.
"""


def create_agent_runnable(google_api_key: str) -> Tuple[Runnable, str]:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        thinking_budget=0,
        convert_system_message_to_human=True,
        google_api_key=google_api_key,
    )
    agent_runnable = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        tools=[update_user_info, diagnose_user, get_user_info],
        middleware=[CustomStateMiddleware()],
        checkpointer=MemorySaver(),
    )
    return agent_runnable, "deepagent"


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    thread_id = f"agent-cli-{uuid.uuid4().hex[:8]}"
    config: RunnableConfig = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    async def chat_cli(agent_runnable: CompiledStateGraph):
        print("=== Stateful CLI Agent ===")
        print("Type your message, or 'exit' to quit.\n")

        prev_num_messages = 0
        prev_non_message_state: dict = {}
        while True:
            try:
                user_text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

            if not user_text:
                continue
            if user_text.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            base_state = {"messages": [{"role": "user", "content": user_text}]}
            print("\n--- Agent thinking... ---")
            EXCLUDE_KEYS = {"state", "model", "structured_response"}
            # --- Stream this turn step-by-step ---
            async for state in agent_runnable.astream(
                base_state, stream_mode="values", config=config
            ):
                state_dict = dict(state)
                messages = state_dict.get("messages", [])

            # --- 1) Print only NEW messages since last step ---
            new_messages = messages[prev_num_messages:]
            for msg in new_messages:
                if isinstance(msg, HumanMessage):
                    print(f"\n[HUMAN] {msg.content}")
                elif isinstance(msg, ToolMessage):
                    print(f"\n[TOOL {msg.name}] {msg.content}")
                elif isinstance(msg, AIMessage):
                    # For tool-call steps `content` can be "", so only show non-empty
                    if msg.content:
                        print(f"\n[AI] {msg.content}")
                    elif msg.tool_calls:
                        print("\n[AI] Tool call(s):")
                        for i, call in enumerate(msg.tool_calls, start=1):
                            name = (
                                call.get("name")
                                if isinstance(call, dict)
                                else getattr(call, "name", "<unknown>")
                            )
                            raw_args = (
                                call.get("args")
                                if isinstance(call, dict)
                                else getattr(call, "args", {})
                            )

                            clean_args = {
                                k: v
                                for k, v in raw_args.items()
                                if k not in EXCLUDE_KEYS
                            }

                            print(f"Tool Name: {name}")
                            print(f"Tool Args: {clean_args}")
                else:
                    # Other message types if any
                    msg_type = getattr(msg, "type", type(msg).__name__)
                    content = getattr(msg, "content", "")
                    print(f"\n[{msg_type.upper()}] {content}")

            prev_num_messages = len(messages)

            # --- 2) Print non-message state (e.g. user_name, diagnosis, etc.) when it changes ---
            non_message_state = {k: v for k, v in state_dict.items() if k != "messages"}

            if non_message_state != prev_non_message_state:
                print("\n[STATE UPDATE]:")
                pprint(non_message_state)
                prev_non_message_state = non_message_state
            print("--- Turn end ---\n")

    agent = create_agent_runnable(os.getenv("GOOGLE_API_KEY"))
    asyncio.run(chat_cli(agent))

    print("----End----")
