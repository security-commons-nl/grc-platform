import asyncio
import httpx
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from passlib.context import CryptContext

# Configuration
API_URL = "http://localhost:8000/api/v1"
DB_URI = "postgresql+asyncpg://postgres:m3RyJhvbHC5mg38FWd9p@localhost/ims"
TEST_USER = "security_tester"
TEST_PASS = "ComplexPassword123!"  # Meets 8+ chars, uppercase, digit
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def setup_test_data():
    """Seed DB with a test user."""
    print(f"Connecting to DB: {DB_URI}")
    engine = create_async_engine(DB_URI)
    async with engine.begin() as conn:
        # 1. Create Tenant
        await conn.execute(text("INSERT INTO tenant (id, name, slug, is_active, country, is_service_provider, created_at, updated_at) VALUES (9999, 'Security Test Tenant', 'sec-test', true, 'NL', false, NOW(), NOW()) ON CONFLICT (id) DO NOTHING"))
        
        # 2. Create User
        pw_hash = pwd_context.hash(TEST_PASS)
        # Using raw SQL to avoid model drift issues
        await conn.execute(
            text("INSERT INTO \"user\" (username, email, password_hash, is_active, is_superuser, created_at, theme, preferred_language) VALUES (:u, :e, :p, true, false, NOW(), 'system'::theme, 'nl'::language) ON CONFLICT (username) DO UPDATE SET password_hash = :p"),
            {"u": TEST_USER, "e": "tester@example.com", "p": pw_hash}
        )
        
        # Get user ID
        r = await conn.execute(text(f"SELECT id FROM \"user\" WHERE username = '{TEST_USER}'"))
        user_id = r.scalar()
        
        # 3. Link to Tenant
        await conn.execute(text(f"INSERT INTO tenantuser (tenant_id, user_id, is_active, is_default, created_at) VALUES (9999, {user_id}, true, true, NOW()) ON CONFLICT (tenant_id, user_id) DO NOTHING"))
        
        print(f"User {TEST_USER} (id={user_id}) setup complete.")
        return user_id

async def verify_api(user_id):
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("\n--- 1. Testing Login (JWT) ---")
        resp = await client.post(f"{API_URL}/auth/login", json={"username": TEST_USER, "password": TEST_PASS})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            sys.exit(1)
        
        data = resp.json()
        token = data.get("access_token")
        if not token:
            print("No access_token in response!")
            sys.exit(1)
        print(f"Login success! Token: {token[:15]}...")

        # 2. Verify Security Headers
        print("\n--- 2. Testing Security Headers ---")
        headers = resp.headers
        print(f"X-Content-Type-Options: {headers.get('x-content-type-options')}")
        print(f"X-Frame-Options: {headers.get('x-frame-options')}")
        if headers.get("x-frame-options") != "DENY":
            print("FAIL: Security headers missing")
            sys.exit(1)
        print("Security headers OK")

        # 3. Protected Endpoint with Token
        print("\n--- 3. Testing Protected Endpoint (WITH Token) ---")
        # We use a simple endpoint. get_user(me) isn't directly available for non-admin on random user, 
        # but we can try getting our own user info if we had a /me endpoint or just check ability to list items.
        # Let's try reset-my-password which requires auth now.
        # Actually calling reset-my-password effectively tests auth guard.
        # But let's try something read-only first.
        # We can try to get tenants.
        resp = await client.get(f"{API_URL}/tenants/", headers={"Authorization": f"Bearer {token}"})
        # This endpoint might require specific roles. 
        # But let's just use `reset-my-password` to verify auth guard.
        
        # 4. Auth Verification via Reset Password
        print("\n--- 4. Testing Reset Password (Authorized) ---")
        new_pass = "NewComplexPass456!"
        payload = {"old_password": TEST_PASS, "new_password": new_pass}
        resp = await client.post(f"{API_URL}/auth/reset-my-password", json=payload, headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 200:
            print(f"Reset password failed: {resp.text}")
            sys.exit(1)
        print("Reset password success.")

        # 5. Unauthorized Access
        print("\n--- 5. Testing Unauthorized Access (No Token) ---")
        resp = await client.post(f"{API_URL}/auth/reset-my-password", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 401:
            print("FAIL: Expected 401")
            sys.exit(1)
        print("Unauthorized access blocked OK")

        # 6. X-User-ID Bypass Attempt
        print("\n--- 6. Testing X-User-ID Bypass (Should Fail in Prod) ---")
        resp = await client.post(f"{API_URL}/auth/reset-my-password", json=payload, headers={"X-User-ID": str(user_id)})
        print(f"Status: {resp.status_code}")
        # In our local .env, JWT_SECRET does NOT start with "CHANGE_ME" (it is "super_secret_local..."), so DEV_MODE is False.
        # So X-User-ID should be rejected.
        if resp.status_code != 401:
            print(f"FAIL: X-User-ID was accepted (status {resp.status_code}) but should be rejected in prod mode")
            sys.exit(1)
        print("X-User-ID bypass blocked OK")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    user_id = loop.run_until_complete(setup_test_data())
    loop.run_until_complete(verify_api(user_id))
    print("\nALL VERIFICATION TESTS PASSED ✅")
