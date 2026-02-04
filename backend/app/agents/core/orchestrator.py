from app.agents.core.base_agent import BaseAgent
from app.agents.domains.risk_agent import RiskAgent
from app.agents.domains.compliance_agent import ComplianceAgent

class AgentOrchestrator:
    """
    Routes interactions to the appropriate agent based on context.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.register_agent(RiskAgent())
        self.register_agent(ComplianceAgent())

    def register_agent(self, agent: BaseAgent):
        """Register an initialized agent."""
        self.agents[agent.name] = agent

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        return self.agents.get(agent_name)

    async def route_request(self, message: str, context: Dict[str, Any]) -> str:
        """
        Determine which agent should handle the request.
        For now, we expect 'agent_name' in context, or default to a general agent (not yet impl).
        """
        agent_name = context.get("agent_name")
        if not agent_name:
            return "Error: No agent specified in context."
            
        agent = self.get_agent(agent_name)
        if not agent:
            return f"Error: Agent '{agent_name}' not found."
            
        return await agent.chat(message, context)

# Global instance
orchestrator = AgentOrchestrator()
