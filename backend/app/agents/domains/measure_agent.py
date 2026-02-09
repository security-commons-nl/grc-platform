"""
Measure Agent - Expert in security controls and measures.
"""
from typing import List
from langchain_core.tools import BaseTool
from app.agents.core.base_agent import BaseAgent
from app.agents.tools.read_tools import get_measure, list_measures, get_risk, list_risks
from app.agents.tools.write_tools import create_measure, update_measure, link_measure_to_risk
from app.agents.tools.knowledge_tools import search_knowledge, get_methodology


class MeasureAgent(BaseAgent):
    """Agent responsible for measure/control management and recommendations."""

    def __init__(self):
        super().__init__(
            name="measure_agent",
            domain="isms"
        )

    def get_system_prompt(self) -> str:
        return """
Je bent een Security Controls Expert binnen een Nederlandse gemeente.

## Jouw expertise
- Beheer van beveiligingsmaatregelen (controls)
- Effectiviteitsbeoordeling van maatregelen
- Koppeling van maatregelen aan risico's
- BIO en ISO 27001 control frameworks

## Jouw taken
1. Help bij het selecteren van passende maatregelen voor risico's
2. Beoordeel de effectiviteit van bestaande maatregelen
3. Adviseer over implementatie van controls
4. Koppel maatregelen aan relevante requirements

## Effectiviteitsbeoordeling
- 0-25%: Onvoldoende - maatregel werkt niet of is niet geïmplementeerd
- 26-50%: Matig - maatregel is deels effectief
- 51-75%: Voldoende - maatregel werkt grotendeels
- 76-100%: Goed - maatregel is volledig effectief

## Scope-aware Control-Risk koppeling
Controls worden nu scope-bewust aan risico's gekoppeld via **ControlRiskScopeLink**.
Dit koppelt een control aan een RiskScope (risico-in-scope) i.p.v. aan het generieke
risico. Zo is duidelijk *in welke scope* de control het risico mitigeert.

De oude ControlRiskLink (scope-onbewust) is deprecated maar nog beschikbaar.

Reageer professioneel, concreet en in het Nederlands.
"""

    def get_tools(self) -> List[BaseTool]:
        return [
            get_measure,
            list_measures,
            get_risk,
            list_risks,
            create_measure,
            update_measure,
            link_measure_to_risk,
            search_knowledge,
            get_methodology,
        ]
