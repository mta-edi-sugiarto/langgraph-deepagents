from langchain.agents import AgentState, create_agent
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command
from pydantic import BaseModel


class CustomState(AgentState):
    user_name: str


model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    convert_system_message_to_human=True,
)


@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_name = runtime.state["user_name"]
    return "User is " + user_name


@tool
def update_user_info(
    runtime: ToolRuntime[CustomState],
) -> Command:
    """Look up and update user info."""
    name = "John Smith"
    return Command(
        update={
            "user_name": name,
            # update the message history
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
    """Use this to greet the user once you found their info."""
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


agent = create_agent(
    model=model,
    tools=[update_user_info, greet],
    state_schema=CustomState,
)
