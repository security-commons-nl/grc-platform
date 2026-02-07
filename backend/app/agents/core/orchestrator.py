from typing import Dict, Any, Optional, List
from app.agents.core.base_agent import BaseAgent
from app.agents.domains import ALL_AGENTS


class AgentOrchestrator:
    """
    Routes interactions to the appropriate agent based on context.

    Supports:
    - Agent selection by name
    - Context-based agent detection
    - Agent listing for UI
    """

    # Mapping of page contexts to recommended agents
    CONTEXT_AGENT_MAP = {
        "risk": "risk",
        "risks": "risk",
        "decision": "risk",
        "decisions": "risk",
        "besluit": "risk",
        "besluitlog": "risk",
        "risk-framework": "risk",
        "risicokader": "risk",
        "behandelstrategie": "risk",
        "treatment": "risk",
        "in-control": "risk",
        "in_control": "risk",
        "measure": "measure",
        "measures": "measure",
        "policy": "policy",
        "policies": "policy",
        "policy-principles": "policy",
        "uitgangspunten": "policy",
        "beleid-trace": "policy",
        "principle": "policy",
        "scope": "scope",
        "scopes": "scope",
        "asset": "scope",
        "assets": "scope",
        "assessment": "assessment",
        "assessments": "assessment",
        "audit": "assessment",
        "incident": "incident",
        "incidents": "incident",
        "privacy": "privacy",
        "dpia": "privacy",
        "continuity": "bcm",
        "bcm": "bcm",
        "supplier": "supplier",
        "suppliers": "supplier",
        "improvement": "improvement",
        "corrective": "improvement",
        "act-overdue": "improvement",
        "feedbackloop": "improvement",
        "workflow": "workflow",
        "planning": "planning",
        "report": "report",
        "dashboard": "report",
        "objective": "objectives",
        "kpi": "objectives",
        "maturity": "maturity",
        "admin": "admin",
        "compliance": "compliance",
        "soa": "compliance",
    }

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self._register_all_agents()

    def _register_all_agents(self):
        """Register all available agents."""
        for name, agent_class in ALL_AGENTS.items():
            try:
                self.agents[name] = agent_class()
            except Exception as e:
                print(f"Warning: Failed to initialize {name} agent: {e}")

    def register_agent(self, agent: BaseAgent):
        """Register an initialized agent."""
        self.agents[agent.name] = agent

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        return self.agents.get(agent_name)

    def list_agents(self) -> List[Dict[str, str]]:
        """List all available agents with their info."""
        return [
            {
                "name": agent.name,
                "domain": agent.domain,
                "description": agent.get_system_prompt()[:200] + "..."
            }
            for agent in self.agents.values()
        ]

    def detect_agent_from_context(self, page: str = None, entity_type: str = None) -> str:
        """
        Detect the best agent based on page/entity context.

        Returns agent name or 'risk' as default.
        """
        # Check page context
        if page:
            page_lower = page.lower()
            for key, agent_name in self.CONTEXT_AGENT_MAP.items():
                if key in page_lower:
                    return agent_name

        # Check entity type
        if entity_type:
            entity_lower = entity_type.lower()
            if entity_lower in self.CONTEXT_AGENT_MAP:
                return self.CONTEXT_AGENT_MAP[entity_lower]

        # Default to risk agent
        return "risk"

    async def route_request(self, message: str, context: Dict[str, Any], history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Determine which agent should handle the request.

        Context can include:
        - agent_name: Explicit agent selection
        - page: Current page for auto-detection
        - entity_type: Current entity type for auto-detection
        """
        # Get agent name from context or detect from page
        agent_name = context.get("agent_name")
        if not agent_name:
            agent_name = self.detect_agent_from_context(
                page=context.get("page"),
                entity_type=context.get("entity_type")
            )

        agent = self.get_agent(agent_name)
        if not agent:
            # Fallback to risk agent
            agent = self.get_agent("risk")
            if not agent:
                return "Error: No agents available."

        return await agent.chat(message, context, history)


# Global instance
orchestrator = AgentOrchestrator()
