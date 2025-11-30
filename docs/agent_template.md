# Managing Agent Templates

This document explains how to manage and edit the agent templates available in the application. Agent templates define the core logic and behavior of the agents you can create and interact with.

## Locating Agent Templates

All agent templates are located in the `src/agents` directory. Each Python file in this directory (e.g., `stateful_agent.py`) represents a single agent template.

## Structure of an Agent Template

Each agent template file is expected to have a specific structure. The key component is the `create_agent_runnable` function.

-   **`create_agent_runnable(google_api_key: str) -> Tuple[Runnable, str]`**: This function is responsible for creating and returning the agent's core logic as a `Runnable` object, along with a string that identifies the session type for this agent.

### Example

```python
# src/agents/stateful_agent.py

from typing import Tuple
from langchain_core.runnables import Runnable
# ... other imports ...

def create_agent_runnable(google_api_key: str) -> Tuple[Runnable, str]:
    # ... agent implementation ...
    agent_runnable = # ... create your agent runnable ...
    return agent_runnable, "stateful_agent_session"
```

## Creating a New Agent Template

To create a new agent template, you need to:

1.  **Create a new Python file** in the `src/agents` directory (e.g., `src/agents/my_new_agent.py`).
2.  **Implement a `create_agent_runnable` function** in this file, following the structure described above.

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

## Editing an Agent Template

To modify the behavior of an agent, you can directly edit the corresponding template file in the `src/agents` directory. For example, you could change the model it uses, alter the prompt, or add new tools.

Changes to an agent template will be reflected in any new agents created using that template.

## Using Agent Templates

To create an agent using a specific template, you pass the template's filename (without the `.py` extension) as the `agent_template` in a `POST /api/v1/agents` request.

### Example

To use the template defined in `src/agents/stateful_agent.py`, you would send the following request:

```json
{
  "agent_template": "stateful_agent"
}
```

To use a newly created template from `src/agents/my_new_agent.py`:

```json
{
  "agent_template": "my_new_agent"
}