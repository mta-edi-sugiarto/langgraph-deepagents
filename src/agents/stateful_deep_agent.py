# src/agents/stateful_deep_agent.py
from langchain.agents import AgentState, create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command


class CustomState(AgentState):
    user_name: str | None = None


model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    convert_system_message_to_human=True,
)


@tool
def get_user_info(runtime: ToolRuntime) -> str:
    user_name = runtime.state["user_name"]
    return "User is " + user_name


@tool
def update_user_info(runtime: ToolRuntime[CustomState]) -> Command:
    name = "John Smith"
    return Command(
        update={
            "user_name": name,
            "messages": [
                ToolMessage(
                    "Successfully looked up user information",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def greet(runtime: ToolRuntime[CustomState]) -> str | Command:
    user_name = runtime.state.get("user_name", None)
    if user_name is None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        "Please call the 'update_user_info' tool it will get and update the user's name.",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )
    return f"Hello {user_name}!"


agent_runnable = create_agent(
    model=model,
    tools=[update_user_info, greet],
    state_schema=CustomState,
)
