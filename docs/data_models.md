# Data Models

This document describes the Pydantic models used for API requests and responses.

## `CreateAgentRequest`

- **Description**: The request model for creating a new agent.
- **Fields**:
  - `agent_template` (str): The name of the agent template to use (e.g., `"stateful_agent"`).

## `CreateAgentResponse`

- **Description**: The response model for a successful agent creation request.
- **Fields**:
  - `agent_id` (str): The unique identifier for the newly created agent.

## `ChatRequest`

- **Description**: The request model for sending a message to an agent.
- **Fields**:
  - `message` (str): The message to send to the agent.

## `ChatResponse`

- **Description**: The response model for a chat request.
- **Fields**:
  - `reply` (str): The agent's reply to the message.
  - `agent_id` (str): The ID of the agent that sent the reply.

## `ListAgentsResponse`

- **Description**: The response model for listing all active agents.
- **Fields**:
  - `agents` (List[str]): A list of agent IDs.