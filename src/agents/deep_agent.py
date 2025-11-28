import os
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from dotenv import load_dotenv
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain.tools import ToolRuntime
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import NotRequired  # or from typing import NotRequired (3.11+)

load_dotenv()

# ---------- 0) Custom state schema ----------


class CounterState(AgentState):
    # Optional counter field managed by our tools
    counter: NotRequired[int]


class CounterStateMiddleware(AgentMiddleware[CounterState]):
    # This is the key: tell LangGraph that this is the state schema
    state_schema = CounterState


# ---------- 1) LLM ----------

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # or your preferred strong model
    temperature=0,
    convert_system_message_to_human=True,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


# ---------- 2) Tools that read/write state via runtime.state ----------


@tool
def increment_counter(state: CounterState, runtime: ToolRuntime) -> str:
    """
    Increment a persistent counter stored in the agent state.
    """
    before = state.get("counter", 0)
    current = before + 1
    state["counter"] = current
    print(f"[DEBUG increment_counter] before={before}, after={current}")
    return f"The counter is now: {current}"


@tool
def read_counter(state: CounterState, runtime: ToolRuntime) -> str:
    """
    Read the current value of the counter.
    """
    current = state.get("counter")
    print(f"[DEBUG read_counter] current={current}")
    if current is None:
        return "The counter has not been initialized yet."
    return f"The counter is currently: {current}"


# ---------- 3) Agent factory with StateBackend + custom state + checkpointer ----------


def build_agent():
    def backend_factory(rt):
        # This backend is for the filesystem tools.
        # It stores files in LangGraph state (ephemeral per thread).
        return StateBackend(rt)

    checkpointer = MemorySaver()

    return create_deep_agent(
        model=model,
        tools=[increment_counter, read_counter],
        backend=backend_factory,
        checkpointer=checkpointer,
        middleware=[CounterStateMiddleware()],  # 🔑 attach our state schema
        system_prompt=(
            "You manage a numeric counter using ONLY the available tools.\n"
            "- When the user asks you to increment the counter, you MUST call "
            "`increment_counter` exactly once and then report the tool's result.\n"
            "- When the user asks for the current counter value, you MUST call "
            "`read_counter` and report the tool's result.\n"
            "- You MUST NOT guess or simulate the counter value."
        ),
    )


if __name__ == "__main__":
    agent = build_agent()

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "counter-demo-1",
        }
    }

    prompts = [
        "My Name is Edi. Increment the counter",
        "Increment the counter again",
        "What is the current counter?",
        "What is my Name?",
    ]

    for p in prompts:
        print(f"\n=== USER: {p!r} ===")
        result = agent.invoke(
            {"messages": [{"role": "user", "content": p}]},
            config=config,
        )

        # Inspect messages
        for m in result["messages"]:
            print(type(m), "→", getattr(m, "content", None))

        last = result["messages"][-1]
        print("\nAGENT:", last.content)
        print("-" * 60)
