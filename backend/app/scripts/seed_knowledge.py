import asyncio
from app.core.db import init_db, get_session
from app.services.knowledge_service import knowledge_service
from app.models.core_models import AIKnowledgeBase
from sqlmodel import select

async def seed_knowledge():
    print("Initializing Database...")
    await init_db()
    
    # Get a session
    async for session in get_session():
        print("Checking existing knowledge...")
        existing = await session.exec(select(AIKnowledgeBase))
        if existing.first():
            print("Knowledge base already seeded.")
            return

        print("Seeding 'In Control' methodology...")
        in_control_content = """
# In Control Model
De gemeente gebruikt het 'In Control' model voor risicobenadering. Dit model bepaalt de aandacht die een risico verdient op basis van twee assen: **Inherente Impact** en **Kwetsbaarheid**.

## De 4 Kwadranten
1. **Mitigeren (Hoog Impact / Hoge Kwetsbaarheid)**
   - Risico is te groot en we zijn er kwetsbaar voor.
   - Actie: Maatregelen nemen om kans of gevolg te verlagen.

2. **Zekerheid Verkrijgen (Hoog Impact / Lage Kwetsbaarheid)**
   - Risico is groot, maar we denken het goed geregeld te hebben.
   - Actie: Testen en verifiëren dat maatregelen echt werken (audit, pen-test).

3. **Meten & Monitoren (Laag Impact / Hoge Kwetsbaarheid)**
   - Risico is klein, maar gaat vaak mis.
   - Actie: Incidenten bijhouden, trendanalyse. Niet direct investeren in dure maatregelen.

4. **Accepteren (Laag Impact / Lage Kwetsbaarheid)**
   - Risico is klein en we zijn er niet vatbaar voor.
   - Actie: Geen specifieke actie, regulier beheer.
"""
        await knowledge_service.add_knowledge(
            session,
            key="METHODOLOGY_IN_CONTROL",
            title="In Control Model",
            content=in_control_content,
            category="methodology"
        )

        print("Seeding MAPGOOD categories...")
        mapgood_content = """
# MAPGOOD Dreigingscategorieën
Wij gebruiken de MAPGOOD indeling voor dreigingen (Standard Dutch Municipality Threat Categories):

- **M (Menselijk falen):** Fouten door medewerkers, onbedoeld wissen data, phishing slachtoffer.
- **A (Applicatie/Software):** Bugs, software fouten, legacy systemen.
- **P (Proces):** Ontbrekende procedures, niet volgen van werkinstructies.
- **G (Gegevens/Data):** Data corruptie, conversiefouten.
- **O (Omgeving):** Brand, overstroming, stroomuitval, kabelbreuk.
- **O (Opzet):** Hackers, malware, ransomware, diefstal, sabotage.
- **D (Derden):** Leveranciers faillissement, supply chain attacks.
"""
        await knowledge_service.add_knowledge(
            session,
            key="METHODOLOGY_MAPGOOD",
            title="MAPGOOD Dreigingen",
            content=mapgood_content,
            category="methodology"
        )
        
        print("Knowledge seeding complete!")
        break

if __name__ == "__main__":
    asyncio.run(seed_knowledge())
