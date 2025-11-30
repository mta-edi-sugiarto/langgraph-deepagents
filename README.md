# LangGraph AgentServer

This project provides a modular and configurable framework for creating and managing different types of conversational agents using LangGraph and FastAPI.

## Features

- **Configurable Agent Creation**: Easily switch between different agent implementations (e.g., stateful vs. deep agents) via a simple API call.
- **Modular Architecture**: A clean separation of concerns between the API layer, core business logic, and agent implementations.
- **Session Management**: Robust session handling for multi-turn conversations.
- **Dynamic Agent Loading**: New agent types can be added without modifying the core application logic.
- **CLI Debugging**: Test and debug agents directly from the command line.
- **Comprehensive Documentation**: Detailed documentation on the architecture, API, data models, and agent management.

## Getting Started

### Prerequisites

- Python 3.13+
- `uv` installed (`pip install uv`)
- An environment variable `GOOGLE_API_KEY` with a valid Google API key.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd langgraph-agentserver
    ```

2.  **Create a virtual environment and install dependencies**:
    ```bash
    uv venv .venv
    source .venv/bin/activate
    uv sync
    ```

### Running the Application

To run the application, use the `manage.py` script:

```bash
python manage.py
```

This will start the FastAPI server on `http://localhost:8000`.

## Quickstart

Once the application is running, you can create a new agent and chat with it using `curl`:

1.  **Create a stateful agent**:
    ```bash
    curl -X POST http://localhost:8000/agents -H "Content-Type: application/json" -d '{"agent_template": "stateful_agent"}'
    ```
    This will return an `agent_id`.

2.  **Chat with the agent**:
    ```bash
    curl -X POST http://localhost:8000/agents/{agent_id}/chat -H "Content-Type: application/json" -d '{"message": "Hello, agent!"}'
    ```
    Replace `{agent_id}` with the ID you received in the previous step.

## Usage

For a detailed API reference, see the [API Reference](docs/api_reference.md).

## Debugging

For information on how to debug the agents directly from the command line, see the [CLI Debugging Guide](docs/cli_debugging.md).

## Documentation

For more detailed information about the project, see the [documentation](docs/).