"""Enable Row Level Security for tenant isolation

Revision ID: 002
Revises: 001
Create Date: 2026-03-25
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

# Tables with tenant_id that need RLS
TENANT_TABLES = [
    "users",
    "user_tenant_roles",
    "ai_audit_logs",
    "ims_step_executions",
    "ims_decisions",
    "ims_documents",
    "ims_document_versions",
    "ims_step_input_documents",
    "ims_gap_analysis_results",
    "ims_tenant_normenkader",
    "ims_standard_ingestions",
    "ims_scopes",
    "ims_risks",
    "ims_controls",
    "ims_assessments",
    "ims_findings",
    "ims_corrective_actions",
    "ims_evidence",
    "ims_incidents",
    "ims_maturity_profiles",
    "ims_setup_scores",
    "ims_grc_scores",
]


def upgrade() -> None:
    # 1. Create the app user if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ims_app') THEN
                CREATE ROLE ims_app WITH LOGIN PASSWORD 'ims_app_secure_2026';
            END IF;
        END $$;
    """)

    # 2. Grant permissions
    op.execute("GRANT CONNECT ON DATABASE ims TO ims_app;")
    op.execute("GRANT USAGE ON SCHEMA public TO ims_app;")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ims_app;")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ims_app;")

    # 3. Enable RLS on all tenant tables (except ims_knowledge_chunks)
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY {table}_tenant_isolation ON {table}
                USING (tenant_id::text = current_setting('app.current_tenant_id', true))
                WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
        """)

    # 4. Special RLS for ims_knowledge_chunks (tenant_id is nullable for normatief layer)
    op.execute("ALTER TABLE ims_knowledge_chunks ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ims_knowledge_chunks FORCE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY ims_knowledge_chunks_tenant_isolation ON ims_knowledge_chunks
            USING (
                tenant_id IS NULL
                OR tenant_id::text = current_setting('app.current_tenant_id', true)
            )
            WITH CHECK (
                tenant_id IS NULL
                OR tenant_id::text = current_setting('app.current_tenant_id', true)
            );
    """)


def downgrade() -> None:
    # Drop all policies and disable RLS
    all_tables = TENANT_TABLES + ["ims_knowledge_chunks"]
    for table in all_tables:
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_isolation ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    # Revoke permissions
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM ims_app;")
    op.execute("REVOKE SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM ims_app;")
    op.execute("REVOKE USAGE ON SCHEMA public FROM ims_app;")
    op.execute("REVOKE CONNECT ON DATABASE ims FROM ims_app;")

    # Drop the ims_app role
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'ims_app') THEN
                DROP ROLE ims_app;
            END IF;
        END $$;
    """)
