"""HITL reviewer_user_id nullable — dev-tokens hebben geen echte users-rij

Maakt `ai_hitl_checkpoints.reviewer_user_id` nullable, identiek aan
de eerdere oplossing voor `ai_audit_logs.user_id` en
`ims_risk_simulations.user_id`. Het endpoint kreeg eerder 500-errors
wanneer een dev-token met een random UUID werd gebruikt (de FK naar
`users.id` faalde). Voor productie-rollout met SSO blijft de FK
gewenst maar dan altijd gevuld; tot die tijd staan we NULL toe.

Revision ID: 018
Revises: 017
Create Date: 2026-05-27
"""
from alembic import op


revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE ai_hitl_checkpoints "
        "ALTER COLUMN reviewer_user_id DROP NOT NULL;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE ai_hitl_checkpoints "
        "ALTER COLUMN reviewer_user_id SET NOT NULL;"
    )
