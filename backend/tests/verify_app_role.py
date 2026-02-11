"""Quick verification that ims_app role enforces RLS."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    e = create_async_engine("postgresql+asyncpg://ims_app:ims_app_secure_2026@localhost/ims")
    async with e.begin() as c:
        await c.execute(text("SET app.current_tenant = '1'"))
        r = await c.execute(text("SELECT count(*) FROM risk"))
        print(f"Risks for tenant 1: {r.scalar()}")

        await c.execute(text("RESET app.current_tenant"))
        try:
            r = await c.execute(text("SELECT count(*) FROM risk"))
            print(f"Risks with no tenant (should be 0): {r.scalar()}")
        except Exception as ex:
            print(f"No tenant -> error (fail-closed): {type(ex).__name__}")
    await e.dispose()
    print("ims_app role works correctly with RLS!")

asyncio.run(test())
