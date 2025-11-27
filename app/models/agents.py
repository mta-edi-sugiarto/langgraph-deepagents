from pydantic import BaseModel


class CreateAgentRequest(BaseModel):
    # you could add tenant_id, initial_user_name, etc.
    pass


class CreateAgentResponse(BaseModel):
    agent_id: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    agent_id: str


class ListAgentsResponse(BaseModel):
    agents: list[str]
