# CLI Debugging

This document explains how to run the agents directly from the command line for debugging purposes. This is useful for testing and observing the agent's behavior in isolation.

## Running the Stateful Agent

To run the stateful agent, execute the following command from the project root:

```bash
python -m src.agents.stateful_agent
```

This will start an interactive chat session in your terminal. You can send messages to the agent and see its responses, including step-by-step streaming of its thought process and state changes.

## Running the Stateful Deep Agent

To run the stateful deep agent, execute the following command from the project root:

```bash
python -m src.agents.stateful_deep_agent
```

This will also start an interactive chat session. The deep agent's output will include detailed information about tool calls and state updates, which is useful for debugging complex interactions.

## Streaming Output

Both command-line interfaces are designed to stream the agent's output step-by-step. This allows you to see:

- **Human messages**: The input you provide to the agent.
- **AI messages**: The agent's responses, including intermediate thoughts and tool calls.
- **Tool messages**: The output of any tools the agent uses.
- **State updates**: Changes to the agent's internal state.

This detailed, real-time feedback is invaluable for understanding how the agent processes information and makes decisions.