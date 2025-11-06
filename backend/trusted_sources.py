"""Trust scoring system for knowledge sources"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .models import Base, async_session
from sqlalchemy import select
from urllib.parse import urlparse

class TrustedSource(Base):
    """Catalog of trusted knowledge sources"""
    __tablename__ = "trusted_sources"
    id = Column(Integer, primary_key=True)
    domain = Column(String(256), unique=True, nullable=False)
    trust_score = Column(Float, nullable=False)
    category = Column(String(64))
    description = Column(Text)
    verified_by = Column(String(64))
    auto_approve_threshold = Column(Float, default=70.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_verified = Column(DateTime(timezone=True))

class TrustScoreManager:
    """Evaluate and manage source trust scores"""
    
    DEFAULT_TRUSTED = [
        {"domain": "python.org", "score": 95, "category": "official_docs"},
        {"domain": "github.com", "score": 70, "category": "code_repository"},
        {"domain": "stackoverflow.com", "score": 75, "category": "community"},
        {"domain": "wikipedia.org", "score": 80, "category": "reference"},
        {"domain": "arxiv.org", "score": 90, "category": "research"},
        {"domain": "localhost", "score": 100, "category": "internal"},
    ]
    
    async def initialize_defaults(self):
        """Seed default trusted sources"""
        async with async_session() as session:
            for source in self.DEFAULT_TRUSTED:
                existing = await session.execute(
                    select(TrustedSource).where(TrustedSource.domain == source["domain"])
                )
                if not existing.scalar_one_or_none():
                    trusted = TrustedSource(
                        domain=source["domain"],
                        trust_score=source["score"],
                        category=source["category"],
                        verified_by="system"
                    )
                    session.add(trusted)
            await session.commit()
        print("✓ Trusted sources initialized")
    
    async def get_trust_score(self, url: str) -> float:
        """Get trust score for a URL"""
        domain = urlparse(url).netloc
        
        async with async_session() as session:
            result = await session.execute(
                select(TrustedSource).where(TrustedSource.domain == domain)
            )
            source = result.scalar_one_or_none()
            
            if source:
                return source.trust_score
            
            return await self._derive_trust_score(domain)
    
    async def _derive_trust_score(self, domain: str) -> float:
        """Derive trust score for unknown domain"""
        
        if any(tld in domain for tld in ['.gov', '.edu']):
            return 85.0
        
        if any(tld in domain for tld in ['.org']):
            return 70.0
        
        if any(suspicious in domain for suspicious in ['bit.ly', 'tinyurl', 'temp']):
            return 20.0
        
        return 50.0
    
    async def should_auto_approve(self, url: str) -> tuple[bool, float]:
        """Auto-approve only if domain exists in TrustedSource and meets threshold.
        Unknown domains are never auto-approved (require explicit approval).
        """
        score = await self.get_trust_score(url)

        async with async_session() as session:
            domain = urlparse(url).netloc
            result = await session.execute(
                select(TrustedSource).where(TrustedSource.domain == domain)
            )
            source = result.scalar_one_or_none()

            if not source:
                # Explicit whitelist required for auto-approval
                return (False, score)

            threshold = source.auto_approve_threshold

        return (score >= threshold, score)

trust_manager = TrustScoreManager()
