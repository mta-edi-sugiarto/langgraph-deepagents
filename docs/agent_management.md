# Agent Management

This document explains how to create and add new agent types to the application.

## Creating a New Agent

To create a new agent, you need to:

1.  **Create a new Python file** in the `src/agents` directory (e.g., `src/agents/my_new_agent.py`).
2.  **Implement a `create_agent_runnable` function** in this file. This function should:
    - Accept a `google_api_key` string as an argument.
    - Return a tuple containing the agent's runnable and a unique session type string (e.g., `"my_new_agent_session"`).

### Example

```python
# src/agents/my_new_agent.py

from typing import Tuple
from langchain_core.runnables import Runnable
# ... other imports ...

def create_agent_runnable(google_api_key: str) -> Tuple[Runnable, str]:
    # ... your agent implementation ...
    agent_runnable = # ... create your agent runnable ...
    return agent_runnable, "my_new_agent_session"
```

## Adding a New Session Type

If your new agent requires a custom session class, you can add it to `src/session.py`. The session manager in `app/core/session_manager.py` will then need to be updated to handle the new session type.

### Example

```python
# src/session.py

class MyNewAgentSession(AgentSession):
    # ... your custom session implementation ...

# app/core/session_manager.py

class SessionManager:
    def create_session(self, agent_runnable: Runnable, agent_type: str) -> str:
        agent_id = str(uuid.uuid4())
        if agent_type == "deepagent":
            session = DeepAgentSession(session_id=agent_id, agent_runnable=agent_runnable)
        elif agent_type == "my_new_agent_session":
            session = MyNewAgentSession(session_id=agent_id, agent_runnable=agent_runnable)
        else:
            session = AgentSession(session_id=agent_id, agent_runnable=agent_runnable)
        self._sessions[agent_id] = session
        return agent_id
```

## Using the New Agent

Once you have created the new agent and (optionally) its session type, you can use it by passing the agent's filename (without the `.py` extension) as the `agent_template` in a `POST /agents` request.

### Example

```json
{
  "agent_template": "my_new_agent"
}