import sys
import os
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv

# Add backend to path so we can import app modules
# Assumes script is run from project root x:\DEV\IMS
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Load env vars from .env in current dir
load_dotenv()

# Import app modules
from app.core.config import settings
from app.models.core_models import User, Tenant, TenantUser, Theme, Language
from app.core.security import get_password_hash

# Configuration
API_URL = "http://localhost:8000/api/v1"
TEST_USER = "orm_security_tester"
TEST_PASS = "ComplexPassword123!"

async def setup_test_data():
    """Seed DB with a test user using ORM."""
    print(f"Connecting to DB: {settings.SQLALCHEMY_DATABASE_URI}")
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if user exists
        stmt = select(User).where(User.username == TEST_USER)
        res = await session.execute(stmt)
        user = res.scalars().first()

        if not user:
            print(f"Creating user {TEST_USER}...")
            user = User(
                username=TEST_USER,
                email="orm_tester@example.com",
                password_hash=get_password_hash(TEST_PASS),
                is_active=True,
                is_superuser=False,
                theme=Theme.SYSTEM,
                preferred_language=Language.NL
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            print(f"User {TEST_USER} exists. Updating password.")
            user.password_hash = get_password_hash(TEST_PASS)
            session.add(user)
            await session.commit()

        # Check if tenant exists
        stmt = select(Tenant).where(Tenant.slug == "orm-test-tenant")
        res = await session.execute(stmt)
        tenant = res.scalars().first()

        if not tenant:
            print("Creating tenant...")
            tenant = Tenant(
                name="ORM Security Test Tenant",
                slug="orm-test-tenant",
                is_active=True,
                country="NL"
            )
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
        
        # Link user to tenant
        stmt = select(TenantUser).where(TenantUser.user_id == user.id, TenantUser.tenant_id == tenant.id)
        res = await session.execute(stmt)
        link = res.scalars().first()

        if not link:
            print("Linking user to tenant...")
            link = TenantUser(
                tenant_id=tenant.id,
                user_id=user.id,
                is_active=True,
                is_default=True
            )
            session.add(link)
            await session.commit()
        
        print(f"Test data setup complete. User ID: {user.id}")
        return user.id

async def verify_api(user_id):
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("\n--- 1. Testing Login (JWT) ---")
        try:
            resp = await client.post(f"{API_URL}/auth/login", json={"username": TEST_USER, "password": TEST_PASS})
            if resp.status_code != 200:
                print(f"Login failed: {resp.status_code} {resp.text}")
                sys.exit(1)
            
            data = resp.json()
            token = data.get("access_token")
            if not token:
                print("No access_token in response!")
                sys.exit(1)
            print(f"Login success! Token: {token[:15]}...")
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            sys.exit(1)

        # 2. Verify Security Headers
        print("\n--- 2. Testing Security Headers ---")
        headers = resp.headers
        print(f"X-Content-Type-Options: {headers.get('x-content-type-options')}")
        print(f"X-Frame-Options: {headers.get('x-frame-options')}")
        if headers.get("x-frame-options") != "DENY":
            print("FAIL: Security headers missing")
            sys.exit(1)
        print("Security headers OK")

        # 3. Auth Verification via Reset Password
        print("\n--- 3. Testing Reset Password (Authorized) ---")
        new_pass = "NewComplexPass456!"
        payload = {"old_password": TEST_PASS, "new_password": new_pass}
        resp = await client.post(f"{API_URL}/auth/reset-my-password", json=payload, headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 200:
            print(f"Reset password failed: {resp.status_code} {resp.text}")
            sys.exit(1)
        print("Reset password success.")

        # Revert password to keep test idempotent-ish (or fail next time? no, setup updates pw)

        # 4. Unauthorized Access
        print("\n--- 4. Testing Unauthorized Access (No Token) ---")
        resp = await client.post(f"{API_URL}/auth/reset-my-password", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 401:
            print("FAIL: Expected 401")
            sys.exit(1)
        print("Unauthorized access blocked OK")

        # 5. X-User-ID Bypass Attempt
        print("\n--- 5. Testing X-User-ID Bypass (Should Fail in Prod) ---")
        resp = await client.post(f"{API_URL}/auth/reset-my-password", json=payload, headers={"X-User-ID": str(user_id)})
        print(f"Status: {resp.status_code}")
        if resp.status_code != 401:
            print(f"FAIL: X-User-ID was accepted (status {resp.status_code}) but should be rejected in prod mode")
            sys.exit(1)
        print("X-User-ID bypass blocked OK")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    user_id = loop.run_until_complete(setup_test_data())
    loop.run_until_complete(verify_api(user_id))
    print("\nALL VERIFICATION TESTS PASSED ✅")
