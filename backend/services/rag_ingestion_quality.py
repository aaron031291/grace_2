"""
RAG Ingestion Quality - Production-Grade Content Processing
Deterministic chunking, deduplication, PII scrubbing, and quality metrics
"""

import hashlib
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class DeterministicChunker:
    """
    Deterministic text chunking with consistent boundaries
    Ensures same input always produces same chunks
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Deterministically chunk text with consistent boundaries

        Args:
            text: Text to chunk
            source_id: Source identifier for tracking

        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []

        chunks = []
        text_length = len(text)

        # Use sentence boundaries for more natural chunking
        sentences = self._split_sentences(text)
        current_chunk = ""
        chunk_start = 0

        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + sentence

            if len(potential_chunk) > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk_data = self._create_chunk(
                    text=current_chunk.strip(),
                    chunk_index=len(chunks),
                    start_pos=chunk_start,
                    end_pos=chunk_start + len(current_chunk),
                    source_id=source_id,
                    total_chunks=None  # Will update later
                )
                chunks.append(chunk_data)

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(text, chunk_start + len(current_chunk) - self.overlap)
                current_chunk = overlap_text + sentence
                chunk_start = max(0, chunk_start + len(current_chunk) - self.overlap)
            else:
                current_chunk = potential_chunk

        # Add final chunk
        if current_chunk.strip():
            chunk_data = self._create_chunk(
                text=current_chunk.strip(),
                chunk_index=len(chunks),
                start_pos=chunk_start,
                end_pos=min(text_length, chunk_start + len(current_chunk)),
                source_id=source_id,
                total_chunks=None
            )
            chunks.append(chunk_data)

        # Update total_chunks count
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk["total_chunks"] = total_chunks

        logger.info(f"[DETERMINISTIC-CHUNKER] Split text into {total_chunks} chunks")
        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex"""
        # Simple sentence splitting - can be enhanced with NLP
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text.strip())

        # Filter out empty sentences
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_text(self, full_text: str, start_pos: int) -> str:
        """Get overlap text from position"""
        if start_pos < 0:
            return ""

        overlap_end = min(len(full_text), start_pos + self.overlap)
        return full_text[start_pos:overlap_end]

    def _create_chunk(self, text: str, chunk_index: int, start_pos: int, end_pos: int,
                     source_id: str, total_chunks: Optional[int]) -> Dict[str, Any]:
        """Create standardized chunk data structure"""
        return {
            "text": text,
            "chunk_index": chunk_index,
            "start_position": start_pos,
            "end_position": end_pos,
            "char_count": len(text),
            "source_id": source_id,
            "total_chunks": total_chunks,
            "chunk_hash": self._hash_text(text),
            "created_at": datetime.utcnow().isoformat()
        }

    def _hash_text(self, text: str) -> str:
        """Generate deterministic hash for chunk"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


class ContentDeduplicator:
    """
    Content deduplication based on fingerprints and similarity
    Prevents duplicate content from polluting knowledge base
    """

    def __init__(self):
        self.fingerprint_cache: Dict[str, str] = {}  # fingerprint -> source_id
        self.similarity_threshold = 0.85

    async def deduplicate_content(self, content_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Remove duplicate content based on fingerprints and similarity

        Args:
            content_items: List of content items to deduplicate

        Returns:
            Tuple of (deduplicated_items, stats)
        """
        deduplicated = []
        stats = {
            "original_count": len(content_items),
            "duplicates_removed": 0,
            "similarity_removed": 0,
            "kept_count": 0
        }

        for item in content_items:
            text = item.get("text", "")
            source_id = item.get("source_id", "unknown")

            # Generate fingerprint
            fingerprint = self._generate_fingerprint(text)

            # Check exact duplicate
            if fingerprint in self.fingerprint_cache:
                existing_source = self.fingerprint_cache[fingerprint]
                logger.debug(f"[DEDUPLICATOR] Exact duplicate found: {source_id} matches {existing_source}")
                stats["duplicates_removed"] += 1
                continue

            # Check similarity with existing content
            is_similar = await self._check_similarity(text, deduplicated)
            if is_similar:
                logger.debug(f"[DEDUPLICATOR] Similar content removed: {source_id}")
                stats["similarity_removed"] += 1
                continue

            # Keep this item
            self.fingerprint_cache[fingerprint] = source_id
            deduplicated.append(item)
            stats["kept_count"] += 1

        logger.info(f"[DEDUPLICATOR] Deduplication complete: {stats['kept_count']} kept, {stats['duplicates_removed'] + stats['similarity_removed']} removed")
        return deduplicated, stats

    def _generate_fingerprint(self, text: str) -> str:
        """Generate content fingerprint"""
        # Normalize text for fingerprinting
        normalized = text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation

        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    async def _check_similarity(self, text: str, existing_items: List[Dict[str, Any]]) -> bool:
        """Check if text is similar to existing content"""
        # Simple Jaccard similarity for now - can be enhanced with embeddings
        text_words = set(text.lower().split())

        for existing in existing_items[-10:]:  # Check last 10 items for performance
            existing_words = set(existing.get("text", "").lower().split())

            if not text_words or not existing_words:
                continue

            intersection = len(text_words & existing_words)
            union = len(text_words | existing_words)

            if union > 0:
                similarity = intersection / union
                if similarity >= self.similarity_threshold:
                    return True

        return False


class PIIScrubber:
    """
    PII Detection and Scrubbing for Content Safety
    Removes or masks sensitive information before ingestion
    """

    def __init__(self):
        # PII patterns - can be enhanced with ML models
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            "api_key": r'\b[A-Za-z0-9]{32,}\b',  # Simple API key pattern
        }

        self.scrub_stats = {
            "emails_scrubbed": 0,
            "phones_scrubbed": 0,
            "ssns_scrubbed": 0,
            "credit_cards_scrubbed": 0,
            "ips_scrubbed": 0,
            "api_keys_scrubbed": 0,
            "total_items_processed": 0
        }

    async def scrub_content(self, content_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Scrub PII from content items

        Args:
            content_items: List of content items to scrub

        Returns:
            Tuple of (scrubbed_items, stats)
        """
        scrubbed_items = []
        self.scrub_stats = {k: 0 for k in self.scrub_stats.keys()}  # Reset stats

        for item in content_items:
            scrubbed_item = await self._scrub_item(item)
            scrubbed_items.append(scrubbed_item)
            self.scrub_stats["total_items_processed"] += 1

        # Log PII detection
        if any(v > 0 for k, v in self.scrub_stats.items() if k != "total_items_processed"):
            await immutable_log.append(
                actor="pii_scrubber",
                action="content_scrubbed",
                resource="knowledge_base",
                outcome="pii_detected",
                payload=self.scrub_stats
            )

        logger.info(f"[PII-SCRUBBER] Processed {self.scrub_stats['total_items_processed']} items, scrubbed PII: {dict((k, v) for k, v in self.scrub_stats.items() if k != 'total_items_processed' and v > 0)}")
        return scrubbed_items, self.scrub_stats

    async def _scrub_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub PII from a single content item"""
        scrubbed_item = item.copy()
        text = item.get("text", "")

        if not text:
            return scrubbed_item

        original_text = text

        # Apply each PII pattern
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                # Replace with placeholder
                placeholder = f"[REDACTED_{pii_type.upper()}]"
                text = re.sub(pattern, placeholder, text)

                # Update stats
                stat_key = f"{pii_type}s_scrubbed"
                if stat_key in self.scrub_stats:
                    self.scrub_stats[stat_key] += len(matches)

        # Update item if text changed
        if text != original_text:
            scrubbed_item["text"] = text
            scrubbed_item["pii_scrubbed"] = True
            scrubbed_item["original_length"] = len(original_text)
        else:
            scrubbed_item["pii_scrubbed"] = False

        return scrubbed_item


class IngestionQualityMetrics:
    """
    Quality metrics for ingestion pipeline
    Tracks chunk size distribution, deduplication rates, PII detection
    """

    def __init__(self):
        self.metrics = {
            "total_chunks_processed": 0,
            "chunk_size_distribution": {},
            "deduplication_rate": 0.0,
            "pii_detection_rate": 0.0,
            "quality_score": 0.0,
            "processing_times": [],
            "error_rate": 0.0
        }

    async def update_metrics(self, chunks: List[Dict[str, Any]], dedup_stats: Dict[str, Any],
                           pii_stats: Dict[str, Any], processing_time: float):
        """Update quality metrics after processing"""

        # Chunk size distribution
        size_bins = {"small": 0, "medium": 0, "large": 0}
        for chunk in chunks:
            size = chunk.get("char_count", 0)
            if size < 500:
                size_bins["small"] += 1
            elif size < 1500:
                size_bins["medium"] += 1
            else:
                size_bins["large"] += 1

        self.metrics["chunk_size_distribution"] = size_bins
        self.metrics["total_chunks_processed"] += len(chunks)

        # Deduplication rate
        original_count = dedup_stats.get("original_count", 0)
        if original_count > 0:
            removed = dedup_stats.get("duplicates_removed", 0) + dedup_stats.get("similarity_removed", 0)
            self.metrics["deduplication_rate"] = removed / original_count

        # PII detection rate
        total_processed = pii_stats.get("total_items_processed", 0)
        if total_processed > 0:
            pii_found = sum(v for k, v in pii_stats.items() if k.endswith("_scrubbed") and k != "total_items_processed")
            self.metrics["pii_detection_rate"] = pii_found / total_processed

        # Processing time
        self.metrics["processing_times"].append(processing_time)
        if len(self.metrics["processing_times"]) > 100:
            self.metrics["processing_times"] = self.metrics["processing_times"][-100:]

        # Overall quality score (0-1, higher is better)
        dedup_score = 1.0 - self.metrics["deduplication_rate"]  # Lower dedup rate = higher quality
        pii_score = 1.0 - self.metrics["pii_detection_rate"]  # Lower PII = higher quality
        size_balance = self._calculate_size_balance(size_bins)

        self.metrics["quality_score"] = (dedup_score + pii_score + size_balance) / 3.0

        # Log metrics
        await immutable_log.append(
            actor="ingestion_quality_metrics",
            action="metrics_updated",
            resource="ingestion_pipeline",
            outcome="quality_assessed",
            payload=self.metrics
        )

    def _calculate_size_balance(self, size_bins: Dict[str, int]) -> float:
        """Calculate how well-balanced chunk sizes are (0-1)"""
        total = sum(size_bins.values())
        if total == 0:
            return 0.0

        # Ideal distribution: 20% small, 60% medium, 20% large
        ideal = {"small": 0.2, "medium": 0.6, "large": 0.2}

        balance_score = 0
        for size_type, count in size_bins.items():
            actual_ratio = count / total
            ideal_ratio = ideal.get(size_type, 0)
            balance_score += 1.0 - abs(actual_ratio - ideal_ratio)

        return balance_score / len(size_bins)

    def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive quality report"""
        return {
            "metrics": self.metrics,
            "recommendations": self._generate_recommendations(),
            "thresholds": {
                "deduplication_rate_max": 0.3,  # Max 30% duplicates
                "pii_detection_rate_max": 0.05,  # Max 5% PII detection
                "quality_score_min": 0.7  # Min 70% quality score
            }
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []

        if self.metrics["deduplication_rate"] > 0.3:
            recommendations.append("High deduplication rate detected - review content sources for duplicates")

        if self.metrics["pii_detection_rate"] > 0.05:
            recommendations.append("High PII detection rate - enhance PII scrubbing patterns")

        size_dist = self.metrics["chunk_size_distribution"]
        total_chunks = sum(size_dist.values())
        if total_chunks > 0:
            small_ratio = size_dist.get("small", 0) / total_chunks
            large_ratio = size_dist.get("large", 0) / total_chunks

            if small_ratio > 0.5:
                recommendations.append("Too many small chunks - increase chunk size or adjust overlap")
            if large_ratio > 0.5:
                recommendations.append("Too many large chunks - decrease chunk size or improve sentence splitting")

        if self.metrics["quality_score"] < 0.7:
            recommendations.append("Overall quality score below threshold - review ingestion pipeline configuration")

        return recommendations


# Global instances
deterministic_chunker = DeterministicChunker()
content_deduplicator = ContentDeduplicator()
pii_scrubber = PIIScrubber()
ingestion_quality_metrics = IngestionQualityMetrics()
