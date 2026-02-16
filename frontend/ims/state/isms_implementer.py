import asyncio
from typing import List, Optional

import reflex as rx
from .base import BaseState
from ..api.client import api_client

class IsmsImplementerState(BaseState):
    """
    State for the ISMS Implementation Guide (ISO 27001).
    Manages the 7-step process and data for each step.
    """
    
    # UI Control (-1=Business Case, 0=Projectplan, 1-7=ISMS stappen)
    active_step: int = -1
    
    # Data Loading
    is_loading: bool = False
    error: str = ""
    
    # --- Step 1 Data (Context) ---
    stakeholders: List[dict] = []
    organization_profile: Optional[dict] = None
    organization_context: List[dict] = [] # SWOT/PESTLE items
    scopes: List[dict] = []
    
    # --- SWOT ---
    swot_strengths: str = ""
    swot_weaknesses: str = ""
    swot_opportunities: str = ""
    swot_threats: str = ""
    swot_editing: str = ""
    swot_edit_text: str = ""

    # --- Step 2 Data (Leadership) ---
    policies: List[dict] = []
    objectives: List[dict] = []
    risk_appetite: Optional[dict] = None
    
    # --- Step 3 Data (Planning) ---
    risks: List[dict] = []
    risk_framework: Optional[dict] = None
    
    # ... other steps data can be loaded on demand or initially
    
    async def load_data(self):
        """Load initial data for the implementer page."""
        self.is_loading = True
        self.error = ""
        
        try:
            # Helper for safe fetching
            async def safe_fetch(coro):
                try:
                    return await coro
                except Exception as e:
                    print(f"Fetch error: {e}")
                    return [] if "list" in str(type(coro)).lower() else None

            # Parallel fetch of core data needed for the overview
            # We fetch Step 1 & 2 data initially as they are most critical
            results = await asyncio.gather(
                safe_fetch(api_client.get_stakeholders()),
                safe_fetch(api_client.get_organization_profile()),
                safe_fetch(api_client.get_policies()),
                safe_fetch(api_client.get_risks(limit=10)), # Just a sample to show status
                safe_fetch(api_client.get_scopes()),
            )
            
            self.stakeholders = results[0] or []
            self.organization_profile = results[1]
            self.policies = results[2] or []
            self.risks = results[3] or []
            self.scopes = results[4] or []
            
            # Context (SWOT) is usually fetched via generic "context" endpoint if exists, 
            # or we might need to filter a generic table. 
            # For now, we assume we might need to add a method to client or use existing.
            # let's skip explicit context fetch for now until we confirmed the endpoint.
            
        except Exception as e:
            self.error = f"Kon data niet laden: {str(e)}"
            print(f"ISMS Load Error: {e}")
        
        self.is_loading = False
        
    def set_step(self, step: int):
        self.active_step = step

    # --- SWOT Actions ---

    def open_swot_edit(self, quadrant: str):
        """Open the edit dialog for a SWOT quadrant."""
        self.swot_editing = quadrant
        if quadrant == "strengths":
            self.swot_edit_text = self.swot_strengths
        elif quadrant == "weaknesses":
            self.swot_edit_text = self.swot_weaknesses
        elif quadrant == "opportunities":
            self.swot_edit_text = self.swot_opportunities
        elif quadrant == "threats":
            self.swot_edit_text = self.swot_threats

    def save_swot_edit(self):
        """Save the edited SWOT text."""
        if self.swot_editing == "strengths":
            self.swot_strengths = self.swot_edit_text
        elif self.swot_editing == "weaknesses":
            self.swot_weaknesses = self.swot_edit_text
        elif self.swot_editing == "opportunities":
            self.swot_opportunities = self.swot_edit_text
        elif self.swot_editing == "threats":
            self.swot_threats = self.swot_edit_text
        self.swot_editing = ""
        self.swot_edit_text = ""

    def close_swot_edit(self):
        """Close the SWOT edit dialog without saving."""
        self.swot_editing = ""
        self.swot_edit_text = ""

    # --- Actions for Step 1 ---

    async def add_stakeholder_from_ui(self):
        """Create a new stakeholder from the UI form."""
        form_data = await self.get_state(rx.State.get_value("sh_name"), rx.State.get_value("sh_type"), rx.State.get_value("sh_reqs"), rx.State.get_value("sh_rel")) 
        # Reflex weirdness with get_value... let's try a different approach.
        # Actually reflex form handling usually involves State vars bound to input value.
        pass

    # We need bound variables for the form
    new_stakeholder_name: str = ""
    new_stakeholder_type: str = "Internal"
    new_stakeholder_reqs: str = ""
    new_stakeholder_rel: str = "High"

    async def add_stakeholder(self):
        """Create a new stakeholder."""
        if not self.new_stakeholder_name:
            return
            
        try:
            data = {
                "name": self.new_stakeholder_name,
                "type": self.new_stakeholder_type,
                "requirements": self.new_stakeholder_reqs,
                "relevance_level": self.new_stakeholder_rel,
                "tenant_id": 1 # Should be dynamic but for now
            }
            await api_client.create_stakeholder(data)
            
            # Refresh list
            self.stakeholders = await api_client.get_stakeholders()
            
            # Reset form
            self.new_stakeholder_name = ""
            self.new_stakeholder_reqs = ""
            
        except Exception as e:
            self.error = f"Fout bij toevoegen stakeholder: {str(e)}"
        
    async def delete_stakeholder(self, id: int):
        """Delete a stakeholder."""
        try:
            await api_client.delete_stakeholder(id)
            # Remove from local list to avoid re-fetch or just re-fetch
            self.stakeholders = [s for s in self.stakeholders if s["id"] != id]
        except Exception as e:
            self.error = f"Fout bij verwijderen stakeholder: {str(e)}"

    # --- Kritische Processen & Uitsluitingen ---
    critical_processes: List[str] = []
    new_critical_process: str = ""
    scope_exclusions: str = ""

    def add_critical_process(self):
        """Add a critical process to the scope."""
        if not self.new_critical_process.strip():
            return
        self.critical_processes = self.critical_processes + [self.new_critical_process.strip()]
        self.new_critical_process = ""

    def delete_critical_process(self, index: int):
        """Remove a critical process by index."""
        self.critical_processes = [
            p for i, p in enumerate(self.critical_processes) if i != index
        ]

    # --- Business Model Canvas ---
    bmc_partners: str = (
        "• Gemeentesecretaris, CIO en directie\n"
        "• CISO / informatiebeveiligingscoördinator\n"
        "• Functioneel beheer ISMS-tool\n"
        "• Privacy officer / FG\n"
        "• Proces- en systeemeigenaren\n"
        "• Interne audit functie\n"
        "• Leveranciers van (kritieke) gemeentelijke systemen\n"
        "• GRC Leverancier\n"
        "• IBD – Levert dreigingsinformatie, ondersteuning incidenten, is CSIRT voor incident meldingen\n"
        "• RDI (Rijksinspectie Digitale Infrastructuur) – Toezichthouder\n"
        "• NCSC ontvangt incidentmeldingen en beheert het register van essentiële en belangrijke entiteiten."
    )
    bmc_activiteiten: str = (
        "• Uitvoeren risicoanalyses (BIA, MAPGOOD, DPIA) door proceseigenaren\n"
        "• Opstellen/onderhouden beveiligingsbeleid, processen en maatregelen (BIO/BIO2)\n"
        "• Monitoren & opvolgen van incidenten\n"
        "• Monitoren van de beheersing van de informatiebeveiligingsprocessen\n"
        "• Registreren van de gemeente als kritieke entiteit\n"
        "• Naleving meldplicht ernstige incidenten bij RDI\n"
        "• Melden incidenten bij CSIRT\n"
        "• Begeleiden van audits en reviews\n"
        "• ISMS beheren (PDCA-cyclus, rapportages)"
    )
    bmc_waarde: str = (
        "• Gemeente is aantoonbaar in control op informatiebeveiliging\n"
        "• Voldoet aan wet- en regelgeving (BIO2, AVG, CBW/NIS2)\n"
        "• Voorkomt boetes, toezichtmaatregelen en imagoschade\n"
        "• Biedt overzicht en stuurinformatie aan bestuur en directie\n"
        "• Biedt verantwoording en zekerheid aan de gemeenteraad en college van B&W\n"
        "• Ondersteunt het ENSIA proces"
    )
    bmc_relaties: str = (
        "• Advies en begeleiding voor proceseigenaren\n"
        "• Interactie bij risicoanalyses en audits\n"
        "• Contractmanagement en leveranciersrelaties (incl. TPRM)\n"
        "• Interne auditfunctie (borging ISMS-doelstellingen)\n"
        "• Proactieve communicatie bij incidenten en dreigingen\n"
        "• Naleving rapportage- en meldverplichtingen"
    )
    bmc_segmenten: str = (
        "• Proces-, informatie- en systeemeigenaren\n"
        "• Gemeentesecretaris, CIO, directie\n"
        "• PO / FG / privacyjuristen\n"
        "• Binnengemeentelijke partijen met ISMS relatie, HR, Audit, contractmanagement, inkoop, I&A/ICT\n"
        "• IBD\n"
        "• RDI (als toezichthouder)\n"
        "• College en raad bij \"grote\" incidenten en datalekken"
    )
    bmc_middelen: str = (
        "• GRC- of ISMS-tool (SaaS)\n"
        "• Risico- en maatregelregister\n"
        "• Templates voor DPIA, incidentmeldingen, maatregelen\n"
        "• Toegang tot BIO2, CBW\n"
        "• Interne capaciteit: CISO, FG, beheer, lijnmanagement\n"
        "• Leveranciers\n"
        "• Procedures en rapportage (formats)"
    )
    bmc_kanalen: str = (
        "• ISMS-dashboard en rapportages\n"
        "• Operationele maandrapportages directie\n"
        "• Incidentenregistratie- en meldsysteem\n"
        "• Awareness programma's\n"
        "• Intranet, mailingen\n"
        "• Rapportages richting RDI\n"
        "• Persoonlijk contact (teams, live)"
    )
    bmc_kosten: str = (
        "• Interne personeelskosten\n"
        "• Incident kosten\n"
        "• Toolinglicenties\n"
        "• Auditkosten\n"
        "• Externe personeelskosten/inhuur\n"
        "• Bewustwordingstrainingen\n"
        "• Non compliancy kosten en boetes"
    )
    bmc_inkomsten: str = (
        "• Geen directe inkomsten\n"
        "• Indirect: voorkomen toezichtmaatregelen, boetes en faalkosten\n"
        "• Verlaging gevolgen van incidenten\n"
        "• Verbeterde continuïteit en bestuurlijke zekerheid"
    )
    bmc_aspecten: str = (
        "Kritieke succesfactoren:\n"
        "• Balans tussen risico en maatregelen\n"
        "• Goede samenwerking met stakeholders\n"
        "• Transparante communicatie\n"
        "• Kennis en kunde bestuur en leiding\n\n"
        "Wettelijk kader:\n"
        "• Cbw, Cbb, AMvB, BIO2, AVG, Wpg\n"
        "• Archiefwet - dossiers moeten permanent bewaard worden"
    )

    # --- Business Case Elementen ---
    bc_omgeving: str = "Beschrijving van de interne en externe context waarin de organisatie opereert en die aanleiding geeft tot de behoefte aan een ISMS."
    bc_doelen: str = "Het overkoepelende doel van het ISMS en de specifieke, meetbare doelstellingen die ermee worden nagestreefd."
    bc_samenvatting: str = "Een beknopt overzicht van het implementatieproject: wat wordt er gedaan, voor wie en waarom."
    bc_voordelen: str = "De verwachte baten van het ISMS, zoals verbeterde beveiliging, compliance, vertrouwen van stakeholders en risicoreductie."
    bc_scope: str = "Een eerste afbakening van het toepassingsgebied: welke processen, afdelingen en systemen vallen binnen het ISMS."
    bc_succesfactoren: str = "Voorwaarden die bepalend zijn voor het slagen van het project, zoals draagvlak van de directie en beschikbaarheid van middelen."
    bc_projectplan: str = "Een globaal overzicht van de aanpak, fasen en activiteiten die nodig zijn om het ISMS te implementeren."
    bc_deadlines: str = "De belangrijkste tijdsgebonden momenten en oplevermomenten gedurende het implementatietraject."
    bc_rollen: str = "Wie is betrokken bij het project en welke rol en verantwoordelijkheid heeft elke betrokkene."
    bc_middelen: str = "De benodigde resources: personeel, tooling, externe ondersteuning en overige faciliteiten."
    bc_budget: str = "De financiële raming voor het implementatietraject, inclusief interne en externe kosten."
    bc_beperkingen: str = "Randvoorwaarden en beperkingen die van invloed zijn op het project, zoals tijd, capaciteit of organisatorische restricties."

    bc_editing: str = ""
    bc_edit_text: str = ""

    def open_bc_edit(self, block: str):
        self.bc_editing = block
        mapping = {
            "omgeving": self.bc_omgeving,
            "doelen": self.bc_doelen,
            "samenvatting": self.bc_samenvatting,
            "voordelen": self.bc_voordelen,
            "scope": self.bc_scope,
            "succesfactoren": self.bc_succesfactoren,
            "projectplan": self.bc_projectplan,
            "deadlines": self.bc_deadlines,
            "rollen": self.bc_rollen,
            "middelen": self.bc_middelen,
            "budget": self.bc_budget,
            "beperkingen": self.bc_beperkingen,
        }
        self.bc_edit_text = mapping.get(block, "")

    def save_bc_edit(self):
        if self.bc_editing == "omgeving":
            self.bc_omgeving = self.bc_edit_text
        elif self.bc_editing == "doelen":
            self.bc_doelen = self.bc_edit_text
        elif self.bc_editing == "samenvatting":
            self.bc_samenvatting = self.bc_edit_text
        elif self.bc_editing == "voordelen":
            self.bc_voordelen = self.bc_edit_text
        elif self.bc_editing == "scope":
            self.bc_scope = self.bc_edit_text
        elif self.bc_editing == "succesfactoren":
            self.bc_succesfactoren = self.bc_edit_text
        elif self.bc_editing == "projectplan":
            self.bc_projectplan = self.bc_edit_text
        elif self.bc_editing == "deadlines":
            self.bc_deadlines = self.bc_edit_text
        elif self.bc_editing == "rollen":
            self.bc_rollen = self.bc_edit_text
        elif self.bc_editing == "middelen":
            self.bc_middelen = self.bc_edit_text
        elif self.bc_editing == "budget":
            self.bc_budget = self.bc_edit_text
        elif self.bc_editing == "beperkingen":
            self.bc_beperkingen = self.bc_edit_text
        self.bc_editing = ""
        self.bc_edit_text = ""

    def close_bc_edit(self):
        self.bc_editing = ""
        self.bc_edit_text = ""

    bmc_editing: str = ""
    bmc_edit_text: str = ""

    def open_bmc_edit(self, block: str):
        self.bmc_editing = block
        mapping = {
            "partners": self.bmc_partners,
            "activiteiten": self.bmc_activiteiten,
            "waarde": self.bmc_waarde,
            "relaties": self.bmc_relaties,
            "segmenten": self.bmc_segmenten,
            "middelen": self.bmc_middelen,
            "kanalen": self.bmc_kanalen,
            "kosten": self.bmc_kosten,
            "inkomsten": self.bmc_inkomsten,
            "aspecten": self.bmc_aspecten,
        }
        self.bmc_edit_text = mapping.get(block, "")

    def save_bmc_edit(self):
        if self.bmc_editing == "partners":
            self.bmc_partners = self.bmc_edit_text
        elif self.bmc_editing == "activiteiten":
            self.bmc_activiteiten = self.bmc_edit_text
        elif self.bmc_editing == "waarde":
            self.bmc_waarde = self.bmc_edit_text
        elif self.bmc_editing == "relaties":
            self.bmc_relaties = self.bmc_edit_text
        elif self.bmc_editing == "segmenten":
            self.bmc_segmenten = self.bmc_edit_text
        elif self.bmc_editing == "middelen":
            self.bmc_middelen = self.bmc_edit_text
        elif self.bmc_editing == "kanalen":
            self.bmc_kanalen = self.bmc_edit_text
        elif self.bmc_editing == "kosten":
            self.bmc_kosten = self.bmc_edit_text
        elif self.bmc_editing == "inkomsten":
            self.bmc_inkomsten = self.bmc_edit_text
        elif self.bmc_editing == "aspecten":
            self.bmc_aspecten = self.bmc_edit_text
        self.bmc_editing = ""
        self.bmc_edit_text = ""

    def close_bmc_edit(self):
        self.bmc_editing = ""
        self.bmc_edit_text = ""

    # --- Projectplan WBS Tabel ---
    wbs_rows: List[dict] = [
        {
            "fase": "Define and establish",
            "stap": "Business Case",
            "activiteit": "Het opstellen en vaststellen van een business case voor de implementatie van het ISMS. Het beheer van het ISMS, dat na de implementatie volgt, valt buiten de scope.",
            "output": "Vastgestelde business case",
            "verantwoordelijke": "CISO",
            "planning": "Q2 2026",
        },
    ]
    wbs_fase: str = ""
    wbs_stap: str = ""
    wbs_activiteit: str = ""
    wbs_output: str = ""
    wbs_verantwoordelijke: str = ""
    wbs_planning: str = ""
    show_wbs_dialog: bool = False

    def open_wbs_dialog(self):
        self.wbs_fase = ""
        self.wbs_stap = ""
        self.wbs_activiteit = ""
        self.wbs_output = ""
        self.wbs_verantwoordelijke = ""
        self.wbs_planning = ""
        self.show_wbs_dialog = True

    def close_wbs_dialog(self):
        self.show_wbs_dialog = False

    def add_wbs_row(self):
        if not self.wbs_activiteit.strip():
            return
        self.wbs_rows = self.wbs_rows + [{
            "fase": self.wbs_fase,
            "stap": self.wbs_stap,
            "activiteit": self.wbs_activiteit,
            "output": self.wbs_output,
            "verantwoordelijke": self.wbs_verantwoordelijke,
            "planning": self.wbs_planning,
        }]
        self.show_wbs_dialog = False

    def delete_wbs_row(self, index: int):
        self.wbs_rows = [r for i, r in enumerate(self.wbs_rows) if i != index]

    # --- Actions for Scope ---

    new_scope_description: str = ""
    
    async def add_scope(self):
        """Add a scope definition."""
        if not self.new_scope_description:
            return
            
        try:
            # We treat scope as a single item or list of items defining the ISMS boundaries
            data = {"description": self.new_scope_description, "tenant_id": 1}
            # Assuming create_scope exists, if not we might need to adapt
            await api_client.create_scope(data) # Placeholder if not exists
            
            self.scopes = await api_client.get_scopes()
            self.new_scope_description = ""
        except Exception as e:
            self.error = f"Fout bij toevoegen scope: {str(e)}"

    async def delete_scope(self, id: int):
        try:
            await api_client.delete_scope(id)
            self.scopes = [s for s in self.scopes if s["id"] != id]
        except Exception as e:
            self.error = f"Fout bij verwijderen scope: {str(e)}"

    # --- Progress Calculation ---

    @rx.var
    def context_progress(self) -> int:
        """
        Calculate percentage completion for Context phase.
        Based on:
        1. Issues/Context (using organization_profile or context items) - 33%
        2. Stakeholders (at least 1) - 33%
        3. Scope (at least 1) - 34%
        """
        progress = 0
        
        # 1. Context / Issues (simple check if profile exists for now, or use context items if valid)
        if self.organization_profile: 
            progress += 33
            
        # 2. Stakeholders
        if self.stakeholders and len(self.stakeholders) > 0:
            progress += 33
            
        # 3. Scope
        if self.scopes and len(self.scopes) > 0:
            progress += 34
            
        return progress

    @rx.var
    def has_context_issues(self) -> bool:
        return self.organization_profile is not None or bool(
            self.swot_strengths or self.swot_weaknesses
            or self.swot_opportunities or self.swot_threats
        )

    @rx.var
    def has_stakeholders(self) -> bool:
        return len(self.stakeholders) > 0

    @rx.var
    def has_scope(self) -> bool:
        return len(self.scopes) > 0

