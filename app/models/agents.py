from pydantic import BaseModel


class CreateAgentRequest(BaseModel):
    agent_template: str


class CreateAgentResponse(BaseModel):
    agent_id: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    agent_id: str


class ListAgentsResponse(BaseModel):
    agents: list[str]
