# src/agents/stateful_deep_agent.py
import asyncio
import os
from pprint import pprint
from typing import Tuple

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command


class CustomState(AgentState):
    user_name: str | None = None


@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_name = runtime.state["user_name"]
    return "User is " + user_name


@tool
def update_user_info(
    name: str,
    runtime: ToolRuntime[CustomState],
) -> Command:
    """Update the user's name in state. This has to be run when the user is declaring their identity.

    Args:
        name: The user's name, parsed from the conversation.
    """
    runtime.state["user_name"] = name
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
def diagnose_user(runtime: ToolRuntime[CustomState]) -> str | Command:
    """Look up a diagnosis based on the current user_name in state."""
    user_name = runtime.state.get("user_name", None)

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
    agent_runnable = create_agent(
        model=model,
        system_prompt=system_prompt,
        tools=[update_user_info, diagnose_user, get_user_info],
        state_schema=CustomState,
    )
    return agent_runnable, "agent"


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    async def chat_cli(agent_runnable):
        print("=== Stateful CLI Agent ===")
        print("Type your message, or 'exit' to quit.\n")

        current_state: CustomState | None = None
        message_offset = 0  # how many messages we have already printed
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

            # --- Build input state for this turn ---
            if current_state is None:
                # first turn: no prior state
                base_state: dict = {
                    "messages": [HumanMessage(content=user_text)],
                }
            else:
                # subsequent turns: start from previous state, append new message
                base_state = dict(current_state)
                msgs = base_state.get("messages", [])
                base_state["messages"] = msgs + [HumanMessage(content=user_text)]

            # For this turn, we want to start printing from the previous total messages
            # so we don't re-print old history.
            # NOTE: base_state already includes the new HumanMessage at the end.
            message_offset = len(base_state.get("messages", [])) - 1

            print("\n--- Agent thinking... ---")

            last_state: CustomState | None = None

            # --- Stream this turn step-by-step ---
            async for state in agent_runnable.astream(base_state, stream_mode="values"):
                state_dict = dict(state)
                messages = state_dict.get("messages", [])

                # 1) Print only NEW messages (since message_offset)
                new_messages = messages[message_offset:]
                for msg in new_messages:
                    if isinstance(msg, HumanMessage):
                        # You already typed it, but we can still show if you like
                        print(f"[HUMAN] {msg.content}")
                    elif isinstance(msg, ToolMessage):
                        print(f"[TOOL {msg.name}] {msg.content}")
                    elif isinstance(msg, AIMessage):
                        if msg.content:
                            print(f"[AI] {msg.content}")
                        else:
                            # tool-call messages often have empty content
                            if msg.tool_calls:
                                print(f"[AI] Tool call(s): {msg.tool_calls}")
                    else:
                        msg_type = getattr(msg, "type", type(msg).__name__)
                        content = getattr(msg, "content", "")
                        print(f"[{msg_type.upper()}] {content}")

                # update offset to the latest known length
                message_offset = len(messages)

                # 2) Print non-message state (user_name, diagnosis, etc.) when it changes
                non_message_state = {
                    k: v for k, v in state_dict.items() if k != "messages"
                }
                if non_message_state != prev_non_message_state:
                    print("\n[UPDATED STATE]:")
                    pprint(non_message_state)
                    prev_non_message_state = non_message_state

                last_state = state

            # --- Persist final state for next turn ---
            if last_state is not None:
                current_state = last_state

            print("--- Turn end ---\n")

    agent, _ = create_agent_runnable(os.getenv("GOOGLE_API_KEY"))
    asyncio.run(chat_cli(agent))
