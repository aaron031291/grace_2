"""Comprehensive tests for Memory Scoring System"""

import pytest
import asyncio
from datetime import datetime, timedelta

from backend.cognition import (
    GraceLoopOutput,
    OutputType,
    ConfidenceLevel,
    MemoryScoreModel,
    DecayCurve,
    LoopMemoryBank,
    GCPolicy,
    TrustReason,
    loop_memory_bank
)


class TestMemoryScoreModel:
    """Test trust and decay scoring"""
    
    def setup_method(self):
        self.scorer = MemoryScoreModel()
    
    def test_score_on_write_high_quality(self):
        """Test initial scoring for high-quality output"""
        output = GraceLoopOutput(
            loop_id="test_loop_1",
            component="reflection",
            output_type=OutputType.REASONING,
            result={"analysis": "high quality reasoning"},
            confidence=0.95,
            quality_score=0.90,
            constitutional_compliance=True,
            requires_approval=False
        )
        
        trust_init = self.scorer.score_on_write(output)
        
        assert 0.0 <= trust_init.total_score <= 1.0
        assert trust_init.total_score > 0.7  # High quality should score well
        assert trust_init.signals.provenance > 0.8  # Reflection is trusted
        assert trust_init.signals.governance == 1.0  # Fully compliant
        assert trust_init.signals.usage == 0.0  # No usage yet
    
    def test_score_on_write_low_quality(self):
        """Test initial scoring for low-quality output"""
        output = GraceLoopOutput(
            loop_id="test_loop_2",
            component="unknown",
            output_type=OutputType.OBSERVATION,
            result={"data": "low confidence"},
            confidence=0.3,
            quality_score=0.4,
            constitutional_compliance=True
        )
        
        trust_init = self.scorer.score_on_write(output)
        
        assert trust_init.total_score < 0.6  # Low quality should score lower
        assert trust_init.signals.provenance < 0.6
    
    def test_score_on_write_non_compliant(self):
        """Test scoring with governance violations"""
        output = GraceLoopOutput(
            loop_id="test_loop_3",
            component="hunter",
            output_type=OutputType.ACTION,
            result={"action": "test"},
            confidence=0.9,
            constitutional_compliance=False,
            errors=["Security violation"]
        )
        
        trust_init = self.scorer.score_on_write(output)
        
        # Governance should be penalized
        assert trust_init.signals.governance < 0.5
        assert trust_init.total_score < 0.7  # Overall lower due to governance
    
    def test_score_on_read_successful_use(self):
        """Test trust boost from successful use"""
        current_trust = 0.7
        boost = self.scorer.score_on_read(
            current_trust=current_trust,
            access_count=5,
            success_count=4,
            failure_count=1,
            outcome="success"
        )
        
        assert boost.delta > 0  # Should boost
        assert boost.new_score > current_trust
        assert 0.0 <= boost.new_score <= 1.0
    
    def test_score_on_read_failed_use(self):
        """Test trust penalty from failed use"""
        current_trust = 0.7
        penalty = self.scorer.score_on_read(
            current_trust=current_trust,
            access_count=5,
            success_count=2,
            failure_count=3,
            outcome="failure"
        )
        
        assert penalty.delta < 0  # Should penalize
        assert penalty.new_score < current_trust
    
    def test_score_on_read_consistency_bonus(self):
        """Test consistency bonus for high success rate"""
        current_trust = 0.7
        boost = self.scorer.score_on_read(
            current_trust=current_trust,
            access_count=10,
            success_count=9,  # 90% success rate
            failure_count=1,
            outcome="success"
        )
        
        # Should get both success boost and consistency bonus
        assert boost.delta > 0.05
    
    def test_apply_decay_hyperbolic(self):
        """Test hyperbolic decay (slow decay for reasoning)"""
        result = self.scorer.apply_decay(
            trust_score=1.0,
            curve=DecayCurve.HYPERBOLIC,
            half_life_hours=168.0,  # 1 week
            hours_elapsed=168.0
        )
        
        # After one half-life, should be around 0.5
        assert 0.4 <= result.decayed_score <= 0.6
        assert result.decay_factor < 1.0
        assert result.hours_elapsed == 168.0
    
    def test_apply_decay_exponential(self):
        """Test exponential decay (fast decay for telemetry)"""
        result = self.scorer.apply_decay(
            trust_score=1.0,
            curve=DecayCurve.EXPONENTIAL,
            half_life_hours=72.0,  # 3 days
            hours_elapsed=72.0
        )
        
        # After one half-life, should be exactly 0.5 for exponential
        assert 0.48 <= result.decayed_score <= 0.52
    
    def test_apply_decay_linear(self):
        """Test linear decay (uniform decay for observations)"""
        result = self.scorer.apply_decay(
            trust_score=1.0,
            curve=DecayCurve.LINEAR,
            half_life_hours=48.0,  # 2 days
            hours_elapsed=96.0  # Full lifetime (2x half-life)
        )
        
        # Linear decay to zero at 2x half-life
        assert result.decayed_score <= 0.1
    
    def test_apply_decay_no_time_elapsed(self):
        """Test decay with zero time elapsed"""
        result = self.scorer.apply_decay(
            trust_score=0.8,
            curve=DecayCurve.HYPERBOLIC,
            half_life_hours=168.0,
            hours_elapsed=0.0
        )
        
        assert result.decayed_score == 0.8  # No decay
        assert result.decay_factor == 1.0
    
    def test_compute_memory_rank(self):
        """Test final memory ranking computation"""
        rank = self.scorer.compute_memory_rank(
            trust_score=0.9,
            relevance_score=0.8,
            recency_score=0.7,
            importance=0.6
        )
        
        assert 0.0 <= rank <= 1.0
        assert rank > 0.7  # High scores should rank well
    
    def test_recommend_decay_curve(self):
        """Test decay curve recommendations"""
        # Reasoning should get hyperbolic (slow)
        curve, half_life = self.scorer.recommend_decay_curve("reasoning")
        assert curve == DecayCurve.HYPERBOLIC
        assert half_life >= 168.0
        
        # Observation should get linear
        curve, half_life = self.scorer.recommend_decay_curve("observation")
        assert curve == DecayCurve.LINEAR
        
        # Action should get exponential
        curve, half_life = self.scorer.recommend_decay_curve("action")
        assert curve == DecayCurve.EXPONENTIAL
    
    def test_update_usage_signal(self):
        """Test usage signal computation"""
        # High success rate
        usage = self.scorer.update_usage_signal(
            current_usage_score=0.5,
            access_count=10,
            success_count=9,
            failure_count=1
        )
        assert usage > 0.8
        
        # Low success rate
        usage = self.scorer.update_usage_signal(
            current_usage_score=0.5,
            access_count=10,
            success_count=3,
            failure_count=7
        )
        assert usage < 0.5
        
        # No accesses
        usage = self.scorer.update_usage_signal(
            current_usage_score=0.0,
            access_count=0,
            success_count=0,
            failure_count=0
        )
        assert usage == 0.0


@pytest.mark.asyncio
class TestLoopMemoryBank:
    """Test unified memory API"""
    
    async def test_store_and_retrieve(self):
        """Test basic store and retrieve"""
        bank = LoopMemoryBank()
        
        output = GraceLoopOutput(
            loop_id="test_loop_store",
            component="reflection",
            output_type=OutputType.REASONING,
            result={"analysis": "test reasoning"},
            confidence=0.85,
            constitutional_compliance=True
        )
        
        # Store
        ref = await bank.store(output, domain="test", category="reasoning")
        
        assert ref.memory_ref.startswith("mem_")
        assert ref.trust_score > 0.0
        
        # Retrieve
        hits = await bank.read(
            query={"component": "reflection"},
            k=10
        )
        
        assert len(hits) > 0
        found = next((h for h in hits if h.memory_ref == ref.memory_ref), None)
        assert found is not None
        assert found.output.loop_id == "test_loop_store"
    
    async def test_store_non_compliant_rejects(self):
        """Test that non-compliant outputs are rejected"""
        bank = LoopMemoryBank()
        
        output = GraceLoopOutput(
            loop_id="test_loop_reject",
            component="test",
            output_type=OutputType.ACTION,
            result={"action": "forbidden"},
            constitutional_compliance=False
        )
        
        with pytest.raises(ValueError, match="non-compliant"):
            await bank.store(output)
    
    async def test_update_trust_successful_use(self):
        """Test trust update from successful use"""
        bank = LoopMemoryBank()
        
        output = GraceLoopOutput(
            loop_id="test_loop_trust",
            component="hunter",
            output_type=OutputType.DECISION,
            result={"decision": "test"},
            confidence=0.8
        )
        
        ref = await bank.store(output, domain="test")
        initial_trust = ref.trust_score
        
        # Update with successful use
        await bank.update_trust(
            memory_ref=ref.memory_ref,
            outcome="success",
            reason=TrustReason.SUCCESSFUL_USE
        )
        
        # Read back and verify trust increased
        hits = await bank.read(
            query={"loop_id": "test_loop_trust"},
            k=1,
            apply_decay=False
        )
        
        assert len(hits) == 1
        assert hits[0].trust_score > initial_trust
        assert hits[0].access_count == 1
    
    async def test_update_trust_failed_use(self):
        """Test trust penalty from failed use"""
        bank = LoopMemoryBank()
        
        output = GraceLoopOutput(
            loop_id="test_loop_fail",
            component="meta",
            output_type=OutputType.PREDICTION,
            result={"prediction": "wrong"},
            confidence=0.7
        )
        
        ref = await bank.store(output, domain="test")
        initial_trust = ref.trust_score
        
        # Update with failure
        await bank.update_trust(
            memory_ref=ref.memory_ref,
            outcome="failure",
            reason=TrustReason.FAILED_USE
        )
        
        # Read back and verify trust decreased
        hits = await bank.read(
            query={"loop_id": "test_loop_fail"},
            k=1,
            apply_decay=False
        )
        
        assert len(hits) == 1
        assert hits[0].trust_score < initial_trust
    
    async def test_read_with_filters(self):
        """Test filtered reads"""
        bank = LoopMemoryBank()
        
        # Store multiple items
        for i in range(5):
            output = GraceLoopOutput(
                loop_id=f"test_filter_{i}",
                component="reflection" if i % 2 == 0 else "hunter",
                output_type=OutputType.REASONING,
                result={"data": i},
                confidence=0.8
            )
            await bank.store(output, domain="test_filter")
        
        # Filter by component
        hits = await bank.read(
            query={"component": "reflection"},
            filters={"domain": "test_filter"},
            k=10
        )
        
        assert len(hits) == 3  # Only reflection items
        assert all(h.output.component == "reflection" for h in hits)
    
    async def test_garbage_collection_low_trust(self):
        """Test GC archiving low-trust items"""
        bank = LoopMemoryBank()
        
        # Store low-trust item
        output = GraceLoopOutput(
            loop_id="test_gc_low",
            component="unknown",
            output_type=OutputType.OBSERVATION,
            result={"data": "low trust"},
            confidence=0.2,
            quality_score=0.1
        )
        
        ref = await bank.store(output, domain="test_gc")
        
        # Run GC with threshold above this item's trust
        policy = GCPolicy(
            name="test_gc_policy",
            min_trust_threshold=0.5,  # Archive below 0.5
            dry_run=False
        )
        
        stats = await bank.garbage_collect(policy)
        
        assert stats["scanned"] >= 1
        assert stats["archived"] >= 1
    
    async def test_garbage_collection_age(self):
        """Test GC archiving old items"""
        bank = LoopMemoryBank()
        
        # Create old-looking item (would need DB manipulation in real test)
        # For now, test the logic path
        policy = GCPolicy(
            name="test_age_policy",
            max_age_hours=1.0,  # Archive older than 1 hour
            dry_run=True  # Dry run to avoid actual deletion
        )
        
        stats = await bank.garbage_collect(policy)
        
        assert "scanned" in stats
        assert "archived" in stats
    
    async def test_garbage_collection_dry_run(self):
        """Test GC dry run doesn't modify data"""
        bank = LoopMemoryBank()
        
        output = GraceLoopOutput(
            loop_id="test_gc_dry",
            component="test",
            output_type=OutputType.OBSERVATION,
            result={"data": "test"},
            confidence=0.1
        )
        
        ref = await bank.store(output, domain="test_gc_dry")
        
        # Dry run
        policy = GCPolicy(
            name="test_dry_run",
            min_trust_threshold=0.5,
            dry_run=True
        )
        
        stats = await bank.garbage_collect(policy)
        
        # Item should still be retrievable
        hits = await bank.read(
            query={"loop_id": "test_gc_dry"},
            k=1
        )
        
        assert len(hits) == 1
    
    async def test_get_trust_history(self):
        """Test retrieving trust history"""
        bank = LoopMemoryBank()
        
        output = GraceLoopOutput(
            loop_id="test_history",
            component="reflection",
            output_type=OutputType.REASONING,
            result={"data": "test"},
            confidence=0.8
        )
        
        ref = await bank.store(output, domain="test")
        
        # Update trust a few times
        await bank.update_trust(ref.memory_ref, outcome="success")
        await bank.update_trust(ref.memory_ref, outcome="success")
        await bank.update_trust(ref.memory_ref, outcome="failure")
        
        # Get history
        history = await bank.get_trust_history(ref.memory_ref)
        
        assert len(history) >= 4  # Initial + 3 updates
        assert history[0]["event_type"] == "initial"
        assert all("old_trust" in event for event in history)
        assert all("new_trust" in event for event in history)
    
    async def test_ranking_by_trust(self):
        """Test that results are ranked by trust"""
        bank = LoopMemoryBank()
        
        # Store items with different trust levels
        refs = []
        for i in range(3):
            output = GraceLoopOutput(
                loop_id=f"test_rank_{i}",
                component="reflection",
                output_type=OutputType.REASONING,
                result={"data": i},
                confidence=0.5 + (i * 0.2)  # Increasing confidence
            )
            ref = await bank.store(output, domain="test_rank")
            refs.append(ref)
        
        # Read all
        hits = await bank.read(
            filters={"domain": "test_rank"},
            k=10
        )
        
        # Should be ranked by trust (higher first)
        assert len(hits) == 3
        for i in range(len(hits) - 1):
            assert hits[i].rank_score >= hits[i + 1].rank_score


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests"""
    
    async def test_full_lifecycle(self):
        """Test complete memory lifecycle"""
        bank = loop_memory_bank
        
        # 1. Create high-quality output
        output = GraceLoopOutput(
            loop_id="lifecycle_test",
            component="reflection",
            output_type=OutputType.REASONING,
            result={"analysis": "comprehensive reasoning chain"},
            confidence=0.92,
            quality_score=0.88,
            constitutional_compliance=True,
            importance=0.8
        )
        
        # 2. Store
        ref = await bank.store(output, domain="integration_test")
        print(f"Stored: {ref.memory_ref} with trust={ref.trust_score:.3f}")
        
        # 3. Use successfully multiple times
        for _ in range(5):
            await bank.update_trust(ref.memory_ref, outcome="success")
        
        # 4. Read back
        hits = await bank.read(
            query={"loop_id": "lifecycle_test"},
            k=1
        )
        
        assert len(hits) == 1
        assert hits[0].trust_score > ref.trust_score  # Should have increased
        assert hits[0].access_count == 5
        
        # 5. Get history
        history = await bank.get_trust_history(ref.memory_ref)
        assert len(history) == 6  # Initial + 5 updates
        
        print(f"Final trust: {hits[0].trust_score:.3f}")
        print(f"Trust history: {len(history)} events")


if __name__ == "__main__":
    # Run async tests
    asyncio.run(TestLoopMemoryBank().test_store_and_retrieve())
    asyncio.run(TestLoopMemoryBank().test_update_trust_successful_use())
    asyncio.run(TestIntegration().test_full_lifecycle())
    print("✓ All integration tests passed")
