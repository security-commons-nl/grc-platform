from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_community.embeddings import OllamaEmbeddings
from app.core.config import settings
from app.models.core_models import AIKnowledgeBase

class KnowledgeService:
    def __init__(self):
        # Use nomic-embed-text for better embeddings if available, otherwise fallback or use mistral
        # Ideally we should configure this. For now we use the main model or a specific embedder.
        # Nomic-embed-text is recommended for Ollama RAG.
        self.embeddings = OllamaEmbeddings(
            base_url=settings.AI_API_BASE.replace("/v1", ""), # Ollama native URL
            model="nomic-embed-text" # Default to a good embedding model
        )

    async def add_knowledge(
        self, 
        session: AsyncSession, 
        key: str, 
        title: str, 
        content: str, 
        category: str
    ) -> AIKnowledgeBase:
        """
        Add a new knowledge entry and generate its embedding.
        """
        # Generate embedding
        vector = self.embeddings.embed_query(content)
        
        knowledge = AIKnowledgeBase(
            key=key,
            title=title,
            content=content,
            category=category,
            is_embedded=True,
            embedded_at=datetime.utcnow(),
            embedding=vector
        )
        
        session.add(knowledge)
        await session.commit()
        await session.refresh(knowledge)
        return knowledge

    async def search_knowledge(
        self, 
        session: AsyncSession, 
        query: str, 
        limit: int = 3
    ) -> List[AIKnowledgeBase]:
        """
        Semantic search for knowledge using cosine distance.
        """
        query_vector = self.embeddings.embed_query(query)
        
        # pgvector syntax for cosine distance is <=>
        # We order by distance (closest first)
        stmt = select(AIKnowledgeBase).order_by(
            AIKnowledgeBase.embedding.cosine_distance(query_vector)
        ).limit(limit)
        
        result = await session.exec(stmt)
        return result.all()

knowledge_service = KnowledgeService()
