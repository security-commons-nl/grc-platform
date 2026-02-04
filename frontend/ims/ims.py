"""
IMS - Integrated Management System
Main Reflex Application Entry Point
"""
import reflex as rx

# Import pages
from ims.pages.login import login_page
from ims.pages.index import dashboard_page
from ims.pages.risks import risks_page
from ims.pages.policies import policies_page
from ims.pages.assessments import assessments_page
from ims.pages.incidents import incidents_page
from ims.pages.scopes import scopes_page
from ims.pages.measures import measures_page
from ims.pages.compliance import compliance_page
from ims.pages.assets import assets_page
from ims.pages.suppliers import suppliers_page
from ims.pages.backlog import backlog_page

# Import state (to ensure it's registered)
from ims.state.auth import AuthState
from ims.state.risk import RiskState
from ims.state.policy import PolicyState
from ims.state.assessment import AssessmentState
from ims.state.incident import IncidentState
from ims.state.scope import ScopeState
from ims.state.measure import MeasureState
from ims.state.compliance import ComplianceState
from ims.state.asset import AssetState
from ims.state.supplier import SupplierState
from ims.state.backlog import BacklogState


# Create app
app = rx.App(
    theme=rx.theme(
        accent_color="blue",
        gray_color="slate",
        radius="medium",
        scaling="95%",
    ),
)

# Add pages
app.add_page(login_page, route="/login", title="Login - IMS")
app.add_page(dashboard_page, route="/", title="Dashboard - IMS")
app.add_page(risks_page, route="/risks", title="Risico's - IMS")
app.add_page(measures_page, route="/measures", title="Maatregelen - IMS")
app.add_page(assessments_page, route="/assessments", title="Assessments - IMS")
app.add_page(incidents_page, route="/incidents", title="Incidenten - IMS")
app.add_page(policies_page, route="/policies", title="Beleid - IMS")
app.add_page(scopes_page, route="/scopes", title="Scopes - IMS")
app.add_page(compliance_page, route="/compliance", title="Compliance - IMS")
app.add_page(assets_page, route="/assets", title="Assets - IMS")
app.add_page(suppliers_page, route="/suppliers", title="Leveranciers - IMS")
app.add_page(backlog_page, route="/backlog", title="Backlog - IMS")
