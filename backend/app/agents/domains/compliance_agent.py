from typing import List
from langchain_core.tools import BaseTool, tool
from app.agents.core.base_agent import BaseAgent
from app.core.db import get_session
from app.services.knowledge_service import knowledge_service

@tool
async def search_standard_tool(query: str) -> str:
    """
    Search for information about compliance standards (BIO, ISO 27001, NEN 7510).
    """
    # In the future, this will query the Standard/Requirement tables.
    # For now, it falls back to the knowledge base.
    return await search_knowledge_tool(query)

@tool
async def search_knowledge_tool(query: str) -> str:
    """
    Search the internal knowledge base for methodologies, frameworks, and best practices.
    """
    results_text = []
    async for session in get_session():
        items = await knowledge_service.search_knowledge(session, query)
        for item in items:
            results_text.append(f"Source: {item.title}\nContent: {item.content}\n---")
        break
    
    if not results_text:
        return "No relevant knowledge found."
    
    return "\n".join(results_text)

class ComplianceAgent(BaseAgent):
    """
    Agent responsible for compliance, frameworks (BIO, ISO), and standards.
    """
    
    def __init__(self):
        super().__init__(
            name="compliance_agent",
            domain="isms"
        )

    def get_system_prompt(self) -> str:
        return """
Je bent een Compliance Expert gespecialiseerd in informatiebeveiliging en privacy.

## Jouw expertise
- BIO (Baseline Informatiebeveiliging Overheid)
- ISO 27001
- NEN 7510
- AVG / GDPR

## Jouw taak
Help de gebruiker bij het begrijpen en toepassen van deze standaarden.
Als de gebruiker een vraag heeft over een specifieke maatregel of norm, zoek deze dan op.

## Toon
- Formeel en accuraat
- Verwijs waar mogelijk naar artikelnummers of hoofdstukken
"""

    def get_tools(self) -> List[BaseTool]:
        return [search_standard_tool, search_knowledge_tool]
