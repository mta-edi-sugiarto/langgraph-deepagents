# main.py
import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# from src.session import AgentSession

app = FastAPI(title="Self-hosted Stateful Agents")

# In-memory registry: {agent_id: AgentSession}
# AGENTS: Dict[str, AgentSession] = {}
