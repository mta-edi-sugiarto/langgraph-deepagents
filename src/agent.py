import os

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Local, non-API-key tools ---------------------------------

NOTES_DB: dict[str, str] = {}


def save_note(title: str, content: str) -> str:
    """
    Save a short note under the given title.
     This tool does NOT call any external API.
    """
    NOTES_DB[title] = content
    return f"Saved note with title: {title}"


def get_note(title: str) -> str:
    """
    Retrieve a saved note by title.
    """
    if title in NOTES_DB:
        return NOTES_DB[title]
    return f"No note found with title: {title!r}"


# --- System instructions --------------------------------------

research_instructions = """
You are an expert personal research and note-taking assistant.

You can:
- Explain concepts clearly.
- Save important notes using the `save_note` tool.
- Retrieve past notes using the `get_note` tool.

When it makes sense, use the tools instead of asking the user
to remember things manually.
"""

# --- Gemini model via LangChain -------------------------------

# Requires GOOGLE_API_KEY in the environment
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # choose your Gemini model
    temperature=0,
    convert_system_message_to_human=True,
)

# --- Deep Agent (LangGraph graph under the hood) --------------

agent = create_deep_agent(
    tools=[save_note, get_note],
    system_prompt=research_instructions,
    model=model,
)
