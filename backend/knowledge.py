from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .models import Base, async_session
from .metric_publishers import KnowledgeMetrics

class KnowledgeEntry(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True)
    source = Column(String(256))
    content = Column(Text, nullable=False)
    category = Column(String(64))
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    relevance_score = Column(Integer, default=0)

class KnowledgeManager:
    """Manages knowledge ingestion and retrieval"""
    
    async def ingest_text(self, content: str, source: str = "manual", category: str = "general"):
        """Store new knowledge"""
        async with async_session() as session:
            entry = KnowledgeEntry(
                source=source,
                content=content,
                category=category
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            print(f"[OK] Ingested knowledge: {content[:50]}...")

            # Publish metrics for knowledge ingestion
            await KnowledgeMetrics.publish_ingestion_completed(0.8, 1)

            return entry.id
    
    async def search_knowledge(self, query: str, limit: int = 5):
        """Simple keyword search in knowledge base"""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(KnowledgeEntry)
                .where(KnowledgeEntry.content.contains(query))
                .order_by(KnowledgeEntry.relevance_score.desc())
                .limit(limit)
            )
            entries = result.scalars().all()

            # Publish metrics for knowledge search
            if entries:
                await KnowledgeMetrics.publish_search_performed(0.9, len(entries))

            return [
                {
                    "id": e.id,
                    "source": e.source,
                    "content": e.content,
                    "category": e.category,
                    "ingested_at": e.ingested_at
                }
                for e in entries
            ]

knowledge_manager = KnowledgeManager()
