import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from app.agents.core.base_agent import BaseAgent
from app.agents.tools.utility_tools import create_suggestion
from app.core.context import get_current_tenant_id

# Define a dummy tool
@tool
def dummy_tool(arg: str) -> str:
    """A dummy tool for testing."""
    return f"Processed: {arg}"

# Define a concrete implementation of BaseAgent for testing
class TestAgent(BaseAgent):
    def __init__(self, name="test", domain="test", tools=None):
        self.name = name
        self.domain = domain
        self.system_prompt = self.get_system_prompt()
        self.tools = tools or self.get_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.runnable = MagicMock()

    def get_system_prompt(self) -> str:
        return "You are a test agent."

    def get_tools(self) -> list:
        return [dummy_tool]

@pytest.mark.asyncio
async def test_agent_tool_execution_loop_multi_turn():
    """
    Test that the agent executes tools in a loop (multi-turn).
    """
    mock_runnable = AsyncMock()

    # 1. Request Tool 1
    msg1 = AIMessage(
        content="",
        tool_calls=[{"name": "dummy_tool", "args": {"arg": "1"}, "id": "call_1"}]
    )

    # 2. Request Tool 2 (after Tool 1 result)
    msg2 = AIMessage(
        content="",
        tool_calls=[{"name": "dummy_tool", "args": {"arg": "2"}, "id": "call_2"}]
    )

    # 3. Final response
    msg3 = AIMessage(content="Final")

    mock_runnable.ainvoke.side_effect = [msg1, msg2, msg3]

    with patch("app.services.ai_gateway.ai_gateway.get_runnable", return_value=mock_runnable):
        agent = TestAgent()
        agent.runnable = mock_runnable

        response = await agent.chat("Go")

        assert response == "Final"
        assert mock_runnable.ainvoke.call_count == 3

        # Verify the history grew correctly.
        # Since the list is mutated in place, we check the final state passed to the last call.
        final_history = mock_runnable.ainvoke.call_args_list[-1][0][0]

        # Should contain:
        # 0. System
        # 1. Human ("Go")
        # 2. AI (tool_call 1)
        # 3. Tool (result 1)
        # 4. AI (tool_call 2)
        # 5. Tool (result 2)
        assert len(final_history) == 6
        assert final_history[1].content == "Go"
        assert final_history[3].content == "Processed: 1"
        assert final_history[5].content == "Processed: 2"

@pytest.mark.asyncio
async def test_tenant_context_injection():
    """
    Test that tenant_id is correctly injected into the context and accessible by tools.
    """
    # Create a tool that checks the context
    @tool
    def check_context_tool() -> str:
        """Check the tenant context."""
        tid = get_current_tenant_id()
        return f"TenantID: {tid}"

    mock_runnable = AsyncMock()
    msg1 = AIMessage(
        content="",
        tool_calls=[{"name": "check_context_tool", "args": {}, "id": "call_ctx"}]
    )
    msg2 = AIMessage(content="Done")
    mock_runnable.ainvoke.side_effect = [msg1, msg2]

    agent = TestAgent(tools=[check_context_tool])
    agent.runnable = mock_runnable

    # Chat with context
    context = {"tenant_id": 999}
    await agent.chat("Check context", context=context)

    # Verify the tool result contained the tenant ID
    # Inspect the final history passed to the last call
    final_history = mock_runnable.ainvoke.call_args_list[-1][0][0]

    # Structure: Sys, Human, AI(call), Tool(res)
    assert len(final_history) == 4
    tool_msg = final_history[3]
    assert isinstance(tool_msg, ToolMessage)
    assert tool_msg.content == "TenantID: 999"

@pytest.mark.asyncio
async def test_create_suggestion_security():
    """
    Test that create_suggestion fails if no tenant context is present.
    """
    # We call the tool directly to verify its internal logic
    # Note: create_suggestion is async

    # Without context
    result = await create_suggestion.ainvoke({
        "suggestion_type": "test",
        "target_entity_type": "test",
        "reasoning": "test",
        "suggested_value": "test"
    })
    assert "Error: No active tenant context" in result
