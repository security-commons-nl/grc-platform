"""
Deadline Components - Universal deadline visualization
Following the color principle: Orange = approaching (≤30 days), Red = overdue
"""
import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


# =============================================================================
# CONSTANTS
# =============================================================================

DEADLINE_WARNING_DAYS = 30  # Days before deadline to show warning (orange)


# =============================================================================
# UTILITY FUNCTIONS (for use in State classes)
# =============================================================================

def compute_deadline_status(deadline_str: Optional[str]) -> str:
    """
    Compute deadline status from ISO date string.

    Args:
        deadline_str: ISO format date string (e.g., "2024-03-15T00:00:00")

    Returns:
        'normal' | 'warning' | 'danger'
    """
    if not deadline_str:
        return 'normal'

    try:
        # Parse ISO date string
        if 'T' in deadline_str:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        else:
            deadline = datetime.fromisoformat(deadline_str)

        # Make naive for comparison if needed
        if deadline.tzinfo:
            deadline = deadline.replace(tzinfo=None)

        now = datetime.utcnow()
        days_until = (deadline - now).days

        if days_until < 0:
            return 'danger'  # Red - overdue
        elif days_until <= DEADLINE_WARNING_DAYS:
            return 'warning'  # Orange - approaching
        else:
            return 'normal'  # Green/neutral
    except (ValueError, TypeError):
        return 'normal'


def compute_days_until(deadline_str: Optional[str]) -> Optional[int]:
    """
    Compute days until deadline (negative if overdue).

    Returns:
        Number of days, or None if no deadline
    """
    if not deadline_str:
        return None

    try:
        if 'T' in deadline_str:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        else:
            deadline = datetime.fromisoformat(deadline_str)

        if deadline.tzinfo:
            deadline = deadline.replace(tzinfo=None)

        now = datetime.utcnow()
        return (deadline - now).days
    except (ValueError, TypeError):
        return None


def enrich_with_deadline_status(
    items: List[Dict[str, Any]],
    deadline_field: str = "review_date",
    status_field: str = "_deadline_status",
    days_field: str = "_days_until"
) -> List[Dict[str, Any]]:
    """
    Enrich a list of items with computed deadline status.
    Call this in your State after loading data from API.

    Args:
        items: List of dicts from API
        deadline_field: Name of the date field to check
        status_field: Name for the computed status field
        days_field: Name for the computed days field

    Returns:
        Same list with added _deadline_status and _days_until fields
    """
    for item in items:
        deadline_str = item.get(deadline_field)
        item[status_field] = compute_deadline_status(deadline_str)
        item[days_field] = compute_days_until(deadline_str)
    return items


def enrich_with_multiple_deadlines(
    items: List[Dict[str, Any]],
    deadline_fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Check multiple deadline fields and use the most urgent one.

    Args:
        items: List of dicts from API
        deadline_fields: List of field names to check (e.g., ["review_date", "expiration_date"])

    Returns:
        Items with _deadline_status set to most urgent status
    """
    for item in items:
        most_urgent_status = 'normal'
        most_urgent_days = None

        for field in deadline_fields:
            deadline_str = item.get(field)
            if deadline_str:
                status = compute_deadline_status(deadline_str)
                days = compute_days_until(deadline_str)

                # Update if more urgent
                if status == 'danger':
                    most_urgent_status = 'danger'
                    if most_urgent_days is None or (days is not None and days < most_urgent_days):
                        most_urgent_days = days
                elif status == 'warning' and most_urgent_status != 'danger':
                    most_urgent_status = 'warning'
                    if most_urgent_days is None or (days is not None and days < most_urgent_days):
                        most_urgent_days = days
                elif most_urgent_status == 'normal' and days is not None:
                    if most_urgent_days is None or days < most_urgent_days:
                        most_urgent_days = days

        item['_deadline_status'] = most_urgent_status
        item['_days_until'] = most_urgent_days

    return items


# =============================================================================
# REFLEX COMPONENTS
# =============================================================================

def deadline_badge(status: rx.Var, days: rx.Var = None, show_days: bool = True) -> rx.Component:
    """
    Badge component that shows deadline status with color coding.

    Args:
        status: Var containing 'normal', 'warning', or 'danger'
        days: Var containing days until deadline (optional)
        show_days: Whether to show the number of days
    """
    return rx.match(
        status,
        (
            "danger",
            rx.badge(
                rx.hstack(
                    rx.icon("alert-circle", size=12),
                    rx.cond(
                        (days != None) & show_days,
                        rx.text(days, " dagen over"),
                        rx.text("Verlopen"),
                    ),
                    spacing="1",
                ),
                color_scheme="red",
                variant="solid",
                size="1",
            ),
        ),
        (
            "warning",
            rx.badge(
                rx.hstack(
                    rx.icon("clock", size=12),
                    rx.cond(
                        (days != None) & show_days,
                        rx.text(days, " dagen"),
                        rx.text("Nadert"),
                    ),
                    spacing="1",
                ),
                color_scheme="orange",
                variant="solid",
                size="1",
            ),
        ),
        # Normal - no badge or subtle badge
        rx.fragment(),
    )


def deadline_badge_compact(status: rx.Var) -> rx.Component:
    """Compact version - just colored dot."""
    return rx.match(
        status,
        ("danger", rx.box(width="8px", height="8px", border_radius="full", background="var(--red-9)")),
        ("warning", rx.box(width="8px", height="8px", border_radius="full", background="var(--orange-9)")),
        rx.fragment(),
    )


def deadline_indicator(status: rx.Var, days: rx.Var) -> rx.Component:
    """
    Full deadline indicator with icon, text, and color.
    For use in detail views or cards.
    """
    return rx.cond(
        status != "normal",
        rx.hstack(
            rx.match(
                status,
                ("danger", rx.icon("alert-circle", size=16, color="var(--red-9)")),
                ("warning", rx.icon("clock", size=16, color="var(--orange-9)")),
                rx.fragment(),
            ),
            rx.match(
                status,
                (
                    "danger",
                    rx.text(
                        rx.cond(
                            days != None,
                            rx.fragment(days.abs(), " dagen over deadline"),
                            "Deadline verlopen",
                        ),
                        size="2",
                        color="red",
                        weight="medium",
                    ),
                ),
                (
                    "warning",
                    rx.text(
                        rx.cond(
                            days != None,
                            rx.fragment("Nog ", days, " dagen"),
                            "Deadline nadert",
                        ),
                        size="2",
                        color="orange",
                        weight="medium",
                    ),
                ),
                rx.fragment(),
            ),
            spacing="2",
            align="center",
        ),
        rx.fragment(),
    )


def deadline_row_style(status: rx.Var) -> dict:
    """
    Returns style dict for table row based on deadline status.
    Apply with: _style=deadline_row_style(item["_deadline_status"])
    """
    return rx.match(
        status,
        ("danger", {"background": "var(--red-a2)", "border_left": "3px solid var(--red-9)"}),
        ("warning", {"background": "var(--orange-a2)", "border_left": "3px solid var(--orange-9)"}),
        {},
    )


# =============================================================================
# DASHBOARD WIDGETS
# =============================================================================

def action_required_card(
    danger_count: rx.Var,
    warning_count: rx.Var,
    danger_items: rx.Var = None,
    warning_items: rx.Var = None,
) -> rx.Component:
    """
    Dashboard card showing items requiring action.

    Args:
        danger_count: Number of overdue items
        warning_count: Number of approaching items
        danger_items: Optional list of danger items for detail view
        warning_items: Optional list of warning items for detail view
    """
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("alert-triangle", size=20, color="var(--orange-9)"),
                rx.text("Actie Vereist", weight="bold", size="3"),
                spacing="2",
            ),
            rx.divider(),
            rx.hstack(
                rx.hstack(
                    rx.box(
                        width="12px",
                        height="12px",
                        border_radius="full",
                        background="var(--red-9)",
                    ),
                    rx.text(danger_count, " verlopen", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="12px",
                        height="12px",
                        border_radius="full",
                        background="var(--orange-9)",
                    ),
                    rx.text(warning_count, " naderen", size="2"),
                    spacing="2",
                ),
                spacing="4",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        padding="16px",
    )
