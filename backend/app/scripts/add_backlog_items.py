import asyncio
import os

# Set DB port to 5433 (as seen in docker ps)
os.environ["POSTGRES_SERVER"] = "localhost:5433"

from app.core.db import init_db, get_session
from app.models.core_models import BacklogItem, BacklogType, BacklogPriority, BacklogStatus

async def add_backlog_items():
    print("Initializing Database... SKIPPED (Avoiding vector extension check)")
    # await init_db()
    
    items_to_add = [
        {
            "title": "Integratie met TopDesk",
            "description": "Koppeling realiseren met TopDesk voor het ophalen van Assets en Incidenten.",
            "item_type": BacklogType.TECHNICAL,
            "priority": BacklogPriority.MEDIUM
        },
        {
            "title": "Integratie met ServiceNow",
            "description": "Koppeling realiseren met ServiceNow voor het ophalen van CMDB (Assets) en Incidenten.",
            "item_type": BacklogType.TECHNICAL,
            "priority": BacklogPriority.MEDIUM
        },
        {
            "title": "Integratie met Proquro",
            "description": "Koppeling realiseren met Proquro voor het ophalen van Leveranciers en Contracten.",
            "item_type": BacklogType.TECHNICAL,
            "priority": BacklogPriority.MEDIUM
        }
    ]

    async for session in get_session():
        print(f"Adding {len(items_to_add)} items to backlog...")
        
        for item_data in items_to_add:
            item = BacklogItem(
                title=item_data["title"],
                description=item_data["description"],
                item_type=item_data["item_type"],
                priority=item_data["priority"],
                status=BacklogStatus.NEW
            )
            session.add(item)
        
        await session.commit()
        print("Backlog items added successfully!")
        break

if __name__ == "__main__":
    asyncio.run(add_backlog_items())
