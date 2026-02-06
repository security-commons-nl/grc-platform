"""
AI Agent Tools for IMS.

Tools are organized by category:
- read_tools: Reading/searching data
- write_tools: Creating/updating data
- knowledge_tools: Knowledge base operations
- utility_tools: Suggestions and collaboration
"""
from app.agents.tools.read_tools import (
    get_risk,
    list_risks,
    search_risks,
    get_measure,
    list_measures,
    get_policy,
    list_policies,
    get_scope,
    list_scopes,
    get_assessment,
    get_incident,
    get_requirement,
)
from app.agents.tools.write_tools import (
    create_risk,
    update_risk,
    create_measure,
    update_measure,
    link_measure_to_risk,
    create_corrective_action,
)
from app.agents.tools.knowledge_tools import (
    search_knowledge,
    get_methodology,
    classify_risk_quadrant,
)
from app.agents.tools.utility_tools import (
    create_suggestion,
    request_agent_collaboration,
)

# All tools for easy import
ALL_READ_TOOLS = [
    get_risk,
    list_risks,
    search_risks,
    get_measure,
    list_measures,
    get_policy,
    list_policies,
    get_scope,
    list_scopes,
    get_assessment,
    get_incident,
    get_requirement,
]

ALL_WRITE_TOOLS = [
    create_risk,
    update_risk,
    create_measure,
    update_measure,
    link_measure_to_risk,
    create_corrective_action,
]

ALL_KNOWLEDGE_TOOLS = [
    search_knowledge,
    get_methodology,
    classify_risk_quadrant,
]

ALL_UTILITY_TOOLS = [
    create_suggestion,
    request_agent_collaboration,
]

ALL_TOOLS = ALL_READ_TOOLS + ALL_WRITE_TOOLS + ALL_KNOWLEDGE_TOOLS + ALL_UTILITY_TOOLS
