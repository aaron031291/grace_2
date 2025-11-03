"""Integration helpers for Memory Scoring System

Provides convenience functions for integrating LoopMemoryBank with existing services.
"""

from typing import Optional, List, Dict, Any
from .GraceLoopOutput import GraceLoopOutput, OutputType
from .LoopMemoryBank import LoopMemoryBank, MemoryHit, TrustReason, loop_memory_bank


class MemoryIntegration:
    """
    Integration layer for memory scoring system
    
    Wraps LoopMemoryBank with convenience methods for common use cases.
    """
    
    def __init__(self):
        self.bank = loop_memory_bank
    
    async def store_reasoning(
        self,
        loop_id: str,
        component: str,
        result: Any,
        confidence: float = 1.0,
        reasoning_chain_id: Optional[str] = None,
        quality_score: Optional[float] = None,
        importance: float = 0.5,
        **kwargs
    ) -> str:
        """
        Store reasoning output
        
        Args:
            loop_id: Loop identifier
            component: Component name (reflection, hunter, meta, etc.)
            result: Reasoning result
            confidence: Confidence level (0-1)
            reasoning_chain_id: Optional chain ID
            quality_score: Optional quality assessment
            importance: Importance hint (0-1)
            **kwargs: Additional GraceLoopOutput fields
            
        Returns:
            Memory reference string
        """
        output = GraceLoopOutput(
            loop_id=loop_id,
            component=component,
            output_type=OutputType.REASONING,
            result=result,
            confidence=confidence,
            reasoning_chain_id=reasoning_chain_id,
            quality_score=quality_score,
            importance=importance,
            **kwargs
        )
        
        ref = await self.bank.store(output, domain="reasoning")
        return ref.memory_ref
    
    async def store_decision(
        self,
        loop_id: str,
        component: str,
        decision: Dict[str, Any],
        confidence: float = 1.0,
        requires_approval: bool = False,
        **kwargs
    ) -> str:
        """Store decision output"""
        output = GraceLoopOutput(
            loop_id=loop_id,
            component=component,
            output_type=OutputType.DECISION,
            result=decision,
            confidence=confidence,
            requires_approval=requires_approval,
            importance=0.8,  # Decisions are important
            **kwargs
        )
        
        ref = await self.bank.store(output, domain="decisions")
        return ref.memory_ref
    
    async def store_observation(
        self,
        loop_id: str,
        component: str,
        observation: Any,
        importance: float = 0.3,
        **kwargs
    ) -> str:
        """Store observation (raw data)"""
        output = GraceLoopOutput(
            loop_id=loop_id,
            component=component,
            output_type=OutputType.OBSERVATION,
            result=observation,
            importance=importance,
            **kwargs
        )
        
        ref = await self.bank.store(output, domain="observations")
        return ref.memory_ref
    
    async def recall_by_component(
        self,
        component: str,
        k: int = 10,
        min_trust: float = 0.0,
        constitutional_only: bool = True
    ) -> List[MemoryHit]:
        """
        Recall memories from a specific component
        
        Args:
            component: Component name
            k: Number of results
            min_trust: Minimum trust threshold
            constitutional_only: Only compliant memories
            
        Returns:
            List of MemoryHit objects
        """
        filters = {"min_trust": min_trust}
        if constitutional_only:
            filters["constitutional_compliance"] = True
        
        return await self.bank.read(
            query={"component": component},
            k=k,
            filters=filters,
            apply_decay=True
        )
    
    async def recall_by_loop(
        self,
        loop_id: str,
        k: int = 10
    ) -> List[MemoryHit]:
        """Recall all memories from a specific loop execution"""
        return await self.bank.read(
            query={"loop_id": loop_id},
            k=k,
            apply_decay=False  # Don't decay when retrieving by exact loop
        )
    
    async def recall_reasoning(
        self,
        k: int = 10,
        min_trust: float = 0.5
    ) -> List[MemoryHit]:
        """Recall high-trust reasoning outputs"""
        return await self.bank.read(
            query={"output_type": "reasoning"},
            k=k,
            filters={
                "min_trust": min_trust,
                "constitutional_compliance": True
            },
            apply_decay=True
        )
    
    async def mark_successful_use(
        self,
        memory_ref: str,
        actor: str = "system"
    ):
        """Mark a memory as successfully used"""
        await self.bank.update_trust(
            memory_ref=memory_ref,
            outcome="success",
            reason=TrustReason.SUCCESSFUL_USE,
            actor=actor
        )
    
    async def mark_failed_use(
        self,
        memory_ref: str,
        actor: str = "system"
    ):
        """Mark a memory as failed in use"""
        await self.bank.update_trust(
            memory_ref=memory_ref,
            outcome="failure",
            reason=TrustReason.FAILED_USE,
            actor=actor
        )
    
    async def boost_trust(
        self,
        memory_ref: str,
        amount: float = 0.1,
        actor: str = "admin"
    ):
        """Manually boost trust score"""
        await self.bank.update_trust(
            memory_ref=memory_ref,
            delta=amount,
            reason=TrustReason.MANUAL_BOOST,
            actor=actor
        )
    
    async def get_component_stats(self, component: str) -> Dict[str, Any]:
        """
        Get statistics for a component's memories
        
        Returns:
            Dict with count, avg_trust, avg_confidence, etc.
        """
        hits = await self.bank.read(
            query={"component": component},
            k=1000,  # Get all
            apply_decay=False
        )
        
        if not hits:
            return {
                "count": 0,
                "avg_trust": 0.0,
                "avg_confidence": 0.0,
                "avg_rank": 0.0,
                "total_accesses": 0
            }
        
        return {
            "count": len(hits),
            "avg_trust": sum(h.trust_score for h in hits) / len(hits),
            "avg_confidence": sum(h.output.confidence for h in hits) / len(hits),
            "avg_rank": sum(h.rank_score for h in hits) / len(hits),
            "total_accesses": sum(h.access_count for h in hits),
            "top_trust": max(h.trust_score for h in hits),
            "low_trust": min(h.trust_score for h in hits)
        }


# Global integration instance
memory_integration = MemoryIntegration()


# Decorator for automatic memory storage
def remember_output(
    component: str,
    output_type: str = "reasoning",
    domain: str = "general"
):
    """
    Decorator to automatically store function outputs in memory
    
    Usage:
        @remember_output(component="reflection", output_type="reasoning")
        async def analyze_code(code: str) -> dict:
            return {"analysis": "..."}
    """
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Create output
            loop_id = kwargs.get("loop_id", f"{component}_{func.__name__}")
            output = GraceLoopOutput(
                loop_id=loop_id,
                component=component,
                output_type=OutputType(output_type),
                result=result,
                confidence=kwargs.get("confidence", 1.0),
                constitutional_compliance=True
            )
            
            # Store in memory
            ref = await loop_memory_bank.store(output, domain=domain)
            print(f"✓ Stored {func.__name__} output: {ref.memory_ref}")
            
            return result
        
        return wrapper
    return decorator
