"""
Utility Tools for AI Agents.

These tools provide generic capabilities for agents:
1. Creating suggestions for user review (instead of direct writes)
2. Collaborating with other agents
3. Sending notifications
"""
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from sqlmodel import select
from app.core.db import get_session
from app.models.core_models import AISuggestion
from app.core.context import get_current_tenant_id
import json

@tool
async def create_suggestion(
    suggestion_type: str,
    target_entity_type: str,
    reasoning: str,
    suggested_value: Any,
    target_entity_id: Optional[int] = None,
    field_name: Optional[str] = None,
    current_value: Any = None,
    confidence: float = 0.8,
    context_summary: Optional[str] = None,
    conversation_id: Optional[int] = None,
) -> str:
    """
    Create a suggestion for the user to review.
    Use this tool when you want to modify data (create, update, delete)
    but require user confirmation.

    Parameters:
    - suggestion_type: "field_update", "create_entity", "workflow_transition", "classification"
    - target_entity_type: "Risk", "Measure", "Policy", etc.
    - target_entity_id: ID of entity (if update/delete)
    - field_name: Field to update (if update)
    - suggested_value: The new value (or full object for create)
    - current_value: The old value (for comparison)
    - reasoning: Why you are suggesting this
    - confidence: 0.0 to 1.0
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return "Error: No active tenant context found. Cannot create suggestion."

    async for session in get_session():
        # Serialize values to JSON if they aren't strings
        if not isinstance(suggested_value, str):
            suggested_value = json.dumps(suggested_value, default=str)

        if current_value is not None and not isinstance(current_value, str):
            current_value = json.dumps(current_value, default=str)

        suggestion = AISuggestion(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            suggestion_type=suggestion_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            field_name=field_name,
            suggested_value=suggested_value,
            current_value=current_value,
            reasoning=reasoning,
            confidence=confidence,
            context_summary=context_summary,
            status="pending"
        )

        session.add(suggestion)
        await session.commit()
        await session.refresh(suggestion)

        return f"Suggestion created successfully (ID: {suggestion.id}). The user will be prompted to review it."


@tool
async def request_agent_collaboration(
    target_agent: str,
    question: str,
    context_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Request help from another specialized agent.

    Use this when:
    - A Risk Agent needs compliance info (ask Compliance Agent)
    - A Policy Agent needs technical details (ask Measure Agent)

    Parameters:
    - target_agent: Name of agent (e.g., "compliance_agent", "measure_agent")
    - question: The specific question to ask
    - context_data: Relevant context to pass along
    """
    from app.agents.core.orchestrator import orchestrator

    agent = orchestrator.get_agent(target_agent)
    if not agent:
        return f"Error: Agent '{target_agent}' not found."

    # In a real implementation, we would start a sub-conversation
    # For now, we simulate a direct call

    # We pass the question as a message to the other agent
    try:
        response = await agent.chat(
            message=question,
            context=context_data or {}
        )
        return f"Response from {target_agent}:\n{response}"
    except Exception as e:
        return f"Error communicating with {target_agent}: {str(e)}"
