import asyncio
import asyncpg
import os
from datetime import datetime

# Set DB params
DB_USER = "postgres"
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "ims"

BACKLOG_ITEMS = [
    ("Integratie met TopDesk", "Koppeling realiseren met TopDesk voor het ophalen van Assets en Incidenten.", "Technisch", "Middel"),
    ("Integratie met ServiceNow", "Koppeling realiseren met ServiceNow voor het ophalen van CMDB (Assets) en Incidenten.", "Technisch", "Middel"),
    ("Integratie met Proquro", "Koppeling realiseren met Proquro voor het ophalen van Leveranciers en Contracten.", "Technisch", "Middel")
]

async def add_backlog_raw():
    dsn = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"Connecting to {dsn}...")
    
    try:
        conn = await asyncpg.connect(dsn)
        print("Connected.")
        
        # Create table if not exists (Manually, since ORM init is broken)
        print("Ensuring table exists...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS backlogitem (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                item_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                submitted_by_id INTEGER,
                submitter_name TEXT,
                admin_notes TEXT,
                votes INTEGER DEFAULT 0,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc')
            );
        """)

        for title, desc, item_type, priority in BACKLOG_ITEMS:
            # Check if exists
            exists = await conn.fetchval(
                "SELECT id FROM backlogitem WHERE title = $1", title
            )
            if exists:
                print(f"Item '{title}' already exists. Skipping.")
                continue
                
            print(f"Inserting '{title}'...")
            await conn.execute(
                """
                INSERT INTO backlogitem (title, description, item_type, priority, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, 'Nieuw', $5, $5)
                """,
                title, desc, item_type, priority, datetime.utcnow()
            )
            
        print("Done!")
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_backlog_raw())
