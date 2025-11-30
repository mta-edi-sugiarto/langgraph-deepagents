# Architecture

This document provides a high-level overview of the application's architecture.

## Core Concepts

The application is designed with a clear separation of concerns, dividing the codebase into three main areas:

- **API Layer (`app/api`)**: Handles incoming HTTP requests and responses.
- **Core Logic (`app/core`)**: Contains the business logic for creating and managing agents.
- **Agent Implementations (`src/agents`)**: Provides the specific implementations for different types of agents.

## Directory Structure

```
.
├── app
│   ├── api
│   │   └── v1
│   │       └── agents.py       # API endpoints for agents
│   ├── core
│   │   ├── agent_factory.py  # Creates agent runnables
│   │   └── session_manager.py# Manages agent sessions
│   ├── models
│   │   └── agents.py       # Pydantic models for API
│   ├── server
│   │   ├── config.py       # Application settings
│   │   └── dependencies.py # FastAPI dependencies
│   └── main.py             # FastAPI application entrypoint
├── docs
│   ├── architecture.md
│   ├── api_reference.md
│   ├── data_models.md
│   └── agent_management.md
│   └── cli_debugging.md
├── src
│   ├── agents
│   │   ├── stateful_agent.py
│   │   └── stateful_deep_agent.py
│   └── session.py            # Agent session classes
└── manage.py                 # Script for running the application
```

## Key Components

### Agent Factory (`app/core/agent_factory.py`)

The agent factory is responsible for creating agent runnables based on a template string provided by the client. It dynamically imports the `create_agent_runnable` function from the appropriate module in `src/agents`, making it easy to add new agent types without modifying the core application logic.

### Session Manager (`app/core/session_manager.py`)

The session manager handles the lifecycle of agent sessions, including creation, storage, retrieval, and deletion. It uses the session type string returned by the agent factory to instantiate the correct session class (`AgentSession` or `DeepAgentSession`).

### API Endpoints (`app/api/v1/agents.py`)

The API layer is responsible for exposing the application's functionality via a RESTful API. It uses the agent factory and session manager, provided as FastAPI dependencies, to handle agent-related requests.