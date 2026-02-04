from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from app.core.config import settings

class BaseAgent(ABC):
    """
    Abstract base class for all IMS AI Agents.
    Wraps LangChain ChatOllama for consistency.
    """
    
    def __init__(self, name: str, domain: str, model: str = None):
        self.name = name
        self.domain = domain
        self.model = model or settings.AI_MODEL_NAME or "mistral"
        self.llm = ChatOllama(
            base_url=settings.AI_API_BASE,
            model=self.model,
            temperature=0.2,
        )
        self.system_prompt = self.get_system_prompt()
        self.tools = self.get_tools()
        
        # Bind tools if available
        if self.tools:
            self.runnable = self.llm.bind_tools(self.tools)
        else:
            self.runnable = self.llm

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Return list of tools available to this agent."""
        pass
        
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the agent and get a response.
        Context can be used to inject dynamic information into the prompt if needed.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=message)
        ]
        
        # In a real implementation, we would handle tool calling loops here.
        # For now, we just invoke the LLM.
        response = await self.runnable.ainvoke(messages)
        return response.content
