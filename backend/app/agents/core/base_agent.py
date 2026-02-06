from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool

from app.services.ai_gateway import ai_gateway
from app.core.context import tenant_context

class BaseAgent(ABC):
    """
    Abstract base class for all IMS AI Agents.
    Uses AI Gateway for multi-provider support (Mistral/Scaleway/Ollama).
    """
    
    def __init__(self, name: str, domain: str, model: str = None):
        self.name = name
        self.domain = domain
        # Model selection is now handled by the gateway primarily, 
        # but we keep the field for logging/context if needed.
        self.model = model 
        
        self.system_prompt = self.get_system_prompt()
        self.tools = self.get_tools()
        
        # Create a mapping for easy tool execution
        self.tool_map = {tool.name: tool for tool in self.tools}

        # Get configured runnable from gateway
        self.runnable = ai_gateway.get_runnable(self.tools)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Return list of tools available to this agent."""
        pass
        
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Send a message to the agent and get a response.
        Context can be used to inject dynamic information into the prompt if needed.
        History is a list of {"role": "user"|"assistant", "content": "..."}

        Handles the tool execution loop:
        1. Invoke LLM
        2. Check for tool calls
        3. Execute tools
        4. Re-invoke LLM with results
        Repeats until no tool calls or max iterations reached.
        """
        # Set tenant context for this execution
        token = None
        if context and "tenant_id" in context:
            token = tenant_context.set(context["tenant_id"])

        try:
            messages = [SystemMessage(content=self.system_prompt)]

            # Add history if provided
            if history:
                for msg in history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))

            # Add current message
            messages.append(HumanMessage(content=message))

            # Execution loop
            max_iterations = 5
            iterations = 0

            # First call to LLM
            response = await self.runnable.ainvoke(messages)

            while iterations < max_iterations:
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    iterations += 1

                    # We have tool calls!
                    # Add the assistant's intent to use tool to history
                    messages.append(response)

                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        tool_call_id = tool_call["id"]

                        tool = self.tool_map.get(tool_name)

                        if tool:
                            try:
                                # Execute tool
                                # We use ainvoke which handles async execution for LangChain tools
                                tool_result = await tool.ainvoke(tool_args)

                                messages.append(ToolMessage(
                                    tool_call_id=tool_call_id,
                                    content=str(tool_result),
                                    name=tool_name
                                ))
                            except Exception as e:
                                messages.append(ToolMessage(
                                    tool_call_id=tool_call_id,
                                    content=f"Error executing tool {tool_name}: {str(e)}",
                                    name=tool_name
                                ))
                        else:
                             messages.append(ToolMessage(
                                tool_call_id=tool_call_id,
                                content=f"Error: Tool {tool_name} not found.",
                                name=tool_name
                            ))

                    # Re-invoke LLM with tool results
                    response = await self.runnable.ainvoke(messages)
                else:
                    # No more tool calls, we are done
                    break

            return response.content if response.content else "No response generated."

        finally:
            if token:
                tenant_context.reset(token)
