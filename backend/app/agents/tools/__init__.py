"""
AI Agent Tools for IMS.

Tools are organized by category:
- read_tools: Reading/searching data
- write_tools: Creating/updating data
- knowledge_tools: Knowledge base operations
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
    # Governance hiaten tools
    get_decision,
    list_decisions,
    check_decision_required,
    get_risk_framework,
    calculate_in_control,
    get_in_control_dashboard,
    get_policy_principle,
    list_policy_principles,
    trace_control_origin,
    get_act_overdue,
)
from app.agents.tools.write_tools import (
    create_risk,
    update_risk,
    create_measure,
    update_measure,
    link_measure_to_risk,
    create_corrective_action,
    # Governance hiaten tools
    create_decision,
    update_risk_treatment,
)
from app.agents.tools.knowledge_tools import (
    search_knowledge,
    get_methodology,
    classify_risk_quadrant,
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
    # Governance hiaten
    get_decision,
    list_decisions,
    check_decision_required,
    get_risk_framework,
    calculate_in_control,
    get_in_control_dashboard,
    get_policy_principle,
    list_policy_principles,
    trace_control_origin,
    get_act_overdue,
]

ALL_WRITE_TOOLS = [
    create_risk,
    update_risk,
    create_measure,
    update_measure,
    link_measure_to_risk,
    create_corrective_action,
    # Governance hiaten
    create_decision,
    update_risk_treatment,
]

ALL_KNOWLEDGE_TOOLS = [
    search_knowledge,
    get_methodology,
    classify_risk_quadrant,
]

ALL_TOOLS = ALL_READ_TOOLS + ALL_WRITE_TOOLS + ALL_KNOWLEDGE_TOOLS
