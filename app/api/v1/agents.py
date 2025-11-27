import uuid

from fastapi import APIRouter, HTTPException

from app.models.agents import (
    ChatRequest,
    ChatResponse,
    CreateAgentRequest,
    CreateAgentResponse,
    ListAgentsResponse,
)
from src.session import AgentSession

router = APIRouter()

AGENTS: dict[str, AgentSession] = {}


@router.post("/agents", response_model=CreateAgentResponse)
async def create_agent_endpoint(body: CreateAgentRequest):
    agent_id = str(uuid.uuid4())
    AGENTS[agent_id] = AgentSession(session_id=agent_id)
    return CreateAgentResponse(agent_id=agent_id)


@router.get("/agents", response_model=ListAgentsResponse)
async def list_agents():
    return ListAgentsResponse(agents=list(AGENTS.keys()))


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    del AGENTS[agent_id]
    return {"status": "deleted", "agent_id": agent_id}


@router.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, body: ChatRequest):
    session = AGENTS.get(agent_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    reply = await session.chat(body.message)
    return ChatResponse(reply=reply, agent_id=agent_id)
