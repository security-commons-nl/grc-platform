from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.core.orchestrator import orchestrator

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    agent_name: Optional[str] = "risk_agent"  # Default to risk agent for now

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[list] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Chat with a specific AI agent.
    If no agent_name is provided in context, defaults to 'risk_agent'.
    """
    # Ensure agent_name is in context
    context = request.context or {}
    if request.agent_name:
        context["agent_name"] = request.agent_name
        
    try:
        response_text = await orchestrator.route_request(request.message, context)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
