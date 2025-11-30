from fastapi import APIRouter, Depends, HTTPException

from app.core.session_manager import SessionManager
from app.models.agents import (
    ChatRequest,
    ChatResponse,
    CreateAgentRequest,
    CreateAgentResponse,
    ListAgentsResponse,
)
from app.server.config import Settings
from app.server.dependencies import (
    get_agent_factory,
    get_session_manager,
    get_settings,
)

router = APIRouter()


@router.post("/agents", response_model=CreateAgentResponse)
async def create_agent_endpoint(
    body: CreateAgentRequest,
    settings: Settings = Depends(get_settings),
    factory: callable = Depends(get_agent_factory),
    manager: SessionManager = Depends(get_session_manager),
):
    try:
        agent_runnable, agent_type = factory(body.agent_template, settings)
        agent_id = manager.create_session(agent_runnable, agent_type)
        return CreateAgentResponse(agent_id=agent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents", response_model=ListAgentsResponse)
async def list_agents(manager: SessionManager = Depends(get_session_manager)):
    return ListAgentsResponse(agents=manager.list_sessions())


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str, manager: SessionManager = Depends(get_session_manager)
):
    if not manager.delete_session(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "deleted", "agent_id": agent_id}


@router.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: str,
    body: ChatRequest,
    manager: SessionManager = Depends(get_session_manager),
):
    session = manager.get_session(agent_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    reply = await session.chat(body.message)
    return ChatResponse(reply=reply, agent_id=agent_id)
