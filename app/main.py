# main.py
import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.api.v1.agents import router as agents_router

# from src.session import AgentSession

app = FastAPI(title="Self-hosted Stateful Agents")
app.include_router(agents_router, prefix="/api/v1")

# In-memory registry: {agent_id: AgentSession}
# AGENTS: Dict[str, AgentSession] = {}
