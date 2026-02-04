from typing import List
from langchain_core.tools import BaseTool, tool
from app.agents.core.base_agent import BaseAgent
from app.core.db import get_session
from app.services.knowledge_service import knowledge_service

# Define tools
@tool
def classify_risk(impact: str, vulnerability: str) -> str:
    """
    Determine the risk quadrant based on Impact and Vulnerability.
    Both inputs should be 'HIGH' or 'LOW'.
    Returns: MITIGATE, MONITOR, ASSURANCE, or ACCEPT.
    """
    impact = impact.upper()
    vulnerability = vulnerability.upper()
    
    if impact == "HIGH" and vulnerability == "HIGH":
        return "MITIGATE"
    elif impact == "LOW" and vulnerability == "HIGH":
        return "MONITOR"
    elif impact == "HIGH" and vulnerability == "LOW":
        return "ASSURANCE"
    elif impact == "LOW" and vulnerability == "LOW":
        return "ACCEPT"
    else:
        return "UNKNOWN - Inputs must be HIGH or LOW"

@tool
async def search_knowledge_tool(query: str) -> str:
    """
    Search the internal knowledge base for methodologies, frameworks, and best practices.
    Use this when you need Information about 'In Control', 'MAPGOOD', 'BIO', or other defined standards.
    """
    results_text = []
    async for session in get_session():
        items = await knowledge_service.search_knowledge(session, query)
        for item in items:
            results_text.append(f"Source: {item.title}\nContent: {item.content}\n---")
        break # Only use one session iteration
    
    if not results_text:
        return "No relevant knowledge found."
    
    return "\n".join(results_text)

class RiskAgent(BaseAgent):
    """
    Agent responsible for risk management advice and classification.
    """
    
    def __init__(self):
        super().__init__(
            name="risk_agent",
            domain="isms"
        )

    def get_system_prompt(self) -> str:
        return """
Je bent een Risk Management Expert binnen een Nederlandse gemeente.

## Jouw expertise
- "In Control" model (kwadranten: Mitigeren, Zekerheid, Monitoren, Accepteren)
- MAPGOOD dreigingscategorieën
- Impact en kwetsbaarheid bepaling

## Jouw taak
Help de gebruiker bij het classificeren en behandelen van risico's.
Gebruik de tool `classify_risk` als de gebruiker expliciet vraagt om het kwadrant te bepalen op basis van impact en kwetsbaarheid.
Gebruik de tool `search_knowledge_tool` als je specifieke definities of methodieken moet opzoeken (zoals MAPGOOD of In Control details) die je niet zeker weet.

## Het In Control Model
| Impact/Kwetsbaarheid | Hoog Impact | Laag Impact |
|----------------------|-------------|-------------|
| Hoge Kwetsbaarheid   | MITIGEREN   | MONITOREN   |
| Lage Kwetsbaarheid   | ZEKERHEID   | ACCEPTEREN  |

Reageer professioneel, concreet en in het Nederlands.
"""

    def get_tools(self) -> List[BaseTool]:
        return [classify_risk, search_knowledge_tool]
