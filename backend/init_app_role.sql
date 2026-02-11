-- Create non-superuser role for the IMS API
-- This role has NOBYPASSRLS, ensuring RLS policies are enforced
-- Run this as superuser (postgres) against the ims database

DO $$ BEGIN
  CREATE ROLE ims_app WITH LOGIN PASSWORD 'ims_app_secure_2026' NOBYPASSRLS;
  RAISE NOTICE 'Role ims_app created';
EXCEPTION WHEN duplicate_object THEN
  RAISE NOTICE 'Role ims_app already exists, skipping';
END $$;

-- Grant table and sequence access
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ims_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ims_app;

-- Ensure future tables also get permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ims_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ims_app;
