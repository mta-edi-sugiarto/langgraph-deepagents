# API Reference

This document provides a reference for the application's API endpoints.

## Create Agent

- **Endpoint**: `POST /agents`
- **Description**: Creates a new agent instance.
- **Request Body**:
  ```json
  {
    "agent_template": "stateful_agent"
  }
  ```
- **Response**:
  ```json
  {
    "agent_id": "..."
  }
  ```

## List Agents

- **Endpoint**: `GET /agents`
- **Description**: Lists all active agent instances.
- **Response**:
  ```json
  {
    "agents": ["..."]
  }
  ```

## Delete Agent

- **Endpoint**: `DELETE /agents/{agent_id}`
- **Description**: Deletes an agent instance.
- **Response**:
  ```json
  {
    "status": "deleted",
    "agent_id": "..."
  }
  ```

## Chat with Agent

- **Endpoint**: `POST /agents/{agent_id}/chat`
- **Description**: Sends a message to an agent and receives a reply.
- **Request Body**:
  ```json
  {
    "message": "Hello, agent!"
  }
  ```
- **Response**:
  ```json
  {
    "reply": "Hello! How can I help you?",
    "agent_id": "..."
  }