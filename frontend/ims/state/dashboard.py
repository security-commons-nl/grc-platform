"""
Dashboard State — aggregated dashboard data including ACT-overdue and My Tasks
"""
import reflex as rx
from typing import Dict, Any, List
from ims.api.client import api_client
from ims.state.auth import AuthState


class DashboardState(rx.State):
    """Dashboard aggregation state."""

    act_overdue: Dict[str, Any] = {}

    # My Tasks
    my_tasks: List[Dict[str, Any]] = []
    tasks_total: int = 0
    tasks_overdue: int = 0
    tasks_due_soon: int = 0
    tasks_loading: bool = False

    @rx.var
    def blocked_count(self) -> int:
        return self.act_overdue.get("blocked_count", 0)

    @rx.var
    def no_action_count(self) -> int:
        return self.act_overdue.get("no_action_count", 0)

    @rx.var
    def open_findings_count(self) -> int:
        return self.act_overdue.get("open_findings_count", 0)

    @rx.var
    def has_act_warnings(self) -> bool:
        return (self.act_overdue.get("blocked_count", 0) + self.act_overdue.get("no_action_count", 0)) > 0

    @rx.var
    def has_tasks(self) -> bool:
        return self.tasks_total > 0

    async def load_dashboard_data(self):
        try:
            self.act_overdue = await api_client.get_act_overdue_summary(tenant_id=1)
        except Exception:
            self.act_overdue = {}

        # Load my tasks
        auth = await self.get_state(AuthState)
        user_id = auth.user_id
        if user_id and user_id > 0:
            self.tasks_loading = True
            try:
                data = await api_client.get_my_tasks(user_id=user_id, tenant_id=1)
                self.my_tasks = data.get("tasks", [])
                summary = data.get("summary", {})
                self.tasks_total = summary.get("total", 0)
                self.tasks_overdue = summary.get("overdue", 0)
                self.tasks_due_soon = summary.get("due_soon", 0)
            except Exception:
                self.my_tasks = []
                self.tasks_total = 0
                self.tasks_overdue = 0
                self.tasks_due_soon = 0
            self.tasks_loading = False
