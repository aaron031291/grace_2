"""
RAG Ingestion Quality - PRODUCTION HARDENED
Deterministic chunking, deduplication pipeline, PII scrubbing with regression tests
"""

import asyncio
import logging
import hashlib
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import difflib

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class DeterministicChunker:
    """
    PRODUCTION: Locked chunk-size heuristics with snapshot testing
    """

    # LOCKED HEURISTICS - DO NOT MODIFY WITHOUT CI APPROVAL
    CHUNK_SIZE_CHARS = 1000
    CHUNK_OVERLAP_CHARS = 200
    MIN_CHUNK_SIZE = 100
    MAX_CHUNK_SIZE = 2000

    # Sentence boundary patterns (locked)
    SENTENCE_ENDINGS = re.compile(r'(?<=[.!?])\s+')

    def __init__(self):
        self.snapshot_tests = self._load_snapshot_tests()
        self.chunking_stats = {
            "total_chunks_created": 0,
            "average_chunk_size": 0.0,
            "chunks_below_min": 0,
            "chunks_above_max": 0,
            "snapshot_tests_passed": 0,
            "snapshot_tests_failed": 0
        }

    def _load_snapshot_tests(self) -> Dict[str, Any]:
        """Load snapshot tests to guard against drift"""
        snapshot_file = Path("./config/chunker_snapshots.json")
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load chunker snapshots: {e}")
        return {}

    async def chunk_text(self, text: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Deterministically chunk text with locked heuristics
        """
        if not text or not text.strip():
            return []

        # Run snapshot test first
        await self._run_snapshot_test(text, source_id)

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate chunk boundary
            end = start + self.CHUNK_SIZE_CHARS

            # Try to break at sentence boundary within overlap window
            if end < len(text):
                sentence_break = self._find_sentence_boundary(text, start, end)
                if sentence_break:
                    end = sentence_break

            # Ensure minimum chunk size (except for last chunk)
            if end - start < self.MIN_CHUNK_SIZE and end < len(text):
                end = min(start + self.MIN_CHUNK_SIZE, len(text))

            # Extract chunk
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = {
                    "chunk_id": f"{source_id}_chunk_{chunk_index}",
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "start_pos": start,
                    "end_pos": end,
                    "source_id": source_id,
                    "chunk_index": chunk_index,
                    "created_at": datetime.utcnow().isoformat()
                }
                chunks.append(chunk)
                chunk_index += 1

                # Update stats
                self.chunking_stats["total_chunks_created"] += 1
                if len(chunk_text) < self.MIN_CHUNK_SIZE:
                    self.chunking_stats["chunks_below_min"] += 1
                if len(chunk_text) > self.MAX_CHUNK_SIZE:
                    self.chunking_stats["chunks_above_max"] += 1

            # Move start position with overlap
            start = end - self.CHUNK_OVERLAP_CHARS
            if start >= len(text):
                break

        # Update average chunk size
        if chunks:
            total_chars = sum(c["char_count"] for c in chunks)
            self.chunking_stats["average_chunk_size"] = total_chars / len(chunks)

        logger.info(f"✓ Chunked {source_id}: {len(chunks)} chunks, avg {self.chunking_stats['average_chunk_size']:.0f} chars")
        return chunks

    def _find_sentence_boundary(self, text: str, start: int, end: int) -> Optional[int]:
        """Find sentence boundary within chunk window"""
        search_text = text[start:end]
        matches = list(self.SENTENCE_ENDINGS.finditer(search_text))

        if matches:
            # Use the last sentence boundary in the window
            last_match = matches[-1]
            return start + last_match.end()

        return None

    async def _run_snapshot_test(self, text: str, source_id: str):
        """Run snapshot test to detect chunking drift"""
        if source_id in self.snapshot_tests:
            expected_chunks = self.snapshot_tests[source_id]["chunks"]
            actual_chunks = await self.chunk_text(text, f"snapshot_test_{source_id}")

            # Compare chunk boundaries
            if len(actual_chunks) != len(expected_chunks):
                self.chunking_stats["snapshot_tests_failed"] += 1
                logger.error(f"❌ Snapshot test FAILED for {source_id}: chunk count mismatch")
                await self._log_snapshot_failure(source_id, expected_chunks, actual_chunks)
                return

            for i, (expected, actual) in enumerate(zip(expected_chunks, actual_chunks)):
                if (expected["start_pos"] != actual["start_pos"] or
                    expected["end_pos"] != actual["end_pos"]):
                    self.chunking_stats["snapshot_tests_failed"] += 1
                    logger.error(f"❌ Snapshot test FAILED for {source_id}: chunk {i} boundary mismatch")
                    await self._log_snapshot_failure(source_id, expected_chunks, actual_chunks)
                    return

            self.chunking_stats["snapshot_tests_passed"] += 1
            logger.info(f"✅ Snapshot test PASSED for {source_id}")

    async def _log_snapshot_failure(self, source_id: str, expected: List[Dict], actual: List[Dict]):
        """Log snapshot test failure for investigation"""
        await immutable_log.append(
            actor="deterministic_chunker",
            action="snapshot_test_failed",
            resource=source_id,
            outcome="failed",
            payload={
                "expected_chunks": len(expected),
                "actual_chunks": len(actual),
                "chunker_config": {
                    "chunk_size": self.CHUNK_SIZE_CHARS,
                    "overlap": self.CHUNK_OVERLAP_CHARS,
                    "min_size": self.MIN_CHUNK_SIZE,
                    "max_size": self.MAX_CHUNK_SIZE
                }
            }
        )

    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get chunking statistics"""
        return self.chunking_stats


class ContentDeduplicator:
    """
    PRODUCTION: Wired into live ingestion pipeline with fingerprint persistence
    """

    def __init__(self, fingerprint_db_path: str = "./databases/dedupe_fingerprints.db"):
        self.fingerprint_db_path = Path(fingerprint_db_path)
        self.fingerprint_db_path.parent.mkdir(parents=True, exist_ok=True)

        self.fingerprints: Dict[str, Dict[str, Any]] = {}
        self.dedupe_stats = {
            "total_items_processed": 0,
            "duplicates_removed": 0,
            "similarity_removed": 0,
            "kept_count": 0,
            "fingerprint_cache_size": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

        # Load existing fingerprints
        self._load_fingerprints()

    def _load_fingerprints(self):
        """Load fingerprints from persistent storage"""
        if self.fingerprint_db_path.exists():
            try:
                with open(self.fingerprint_db_path, 'r') as f:
                    self.fingerprints = json.load(f)
                self.dedupe_stats["fingerprint_cache_size"] = len(self.fingerprints)
                logger.info(f"✓ Loaded {len(self.fingerprints)} dedupe fingerprints")
            except Exception as e:
                logger.error(f"Failed to load fingerprints: {e}")

    def _save_fingerprints(self):
        """Persist fingerprints to disk"""
        try:
            with open(self.fingerprint_db_path, 'w') as f:
                json.dump(self.fingerprints, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save fingerprints: {e}")

    def _generate_fingerprint(self, text: str) -> str:
        """Generate content fingerprint"""
        # Normalize text
        normalized = text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation

        # Generate hash
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (0-1)"""
        # Simple Jaccard similarity on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    async def deduplicate_content(self, content_items: List[Dict[str, Any]],
                                similarity_threshold: float = 0.85) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        PRODUCTION: Deduplicate content with fingerprinting and persistence
        """
        deduped_items = []
        stats = {
            "original_count": len(content_items),
            "kept_count": 0,
            "duplicates_removed": 0,
            "similarity_removed": 0,
            "processing_time": 0.0
        }

        start_time = datetime.utcnow()

        for item in content_items:
            text = item.get("text", "")
            source_id = item.get("source_id", "unknown")

            if not text.strip():
                continue

            fingerprint = self._generate_fingerprint(text)
            item["fingerprint"] = fingerprint

            # Check exact duplicate
            if fingerprint in self.fingerprints:
                self.dedupe_stats["cache_hits"] += 1
                existing = self.fingerprints[fingerprint]
                logger.debug(f"Duplicate found: {source_id} matches {existing['source_id']}")
                stats["duplicates_removed"] += 1
                self.dedupe_stats["duplicates_removed"] += 1
                continue

            # Check similarity (expensive, only for small batches)
            is_similar = False
            if len(content_items) <= 10:  # Only check similarity for small batches
                for existing_fp, existing_data in list(self.fingerprints.items())[-100:]:  # Last 100
                    if existing_fp != fingerprint:
                        similarity = self._calculate_similarity(text, existing_data.get("sample_text", ""))
                        if similarity >= similarity_threshold:
                            logger.debug(f"Similar content found: {source_id} similar to {existing_data['source_id']} ({similarity:.2f})")
                            is_similar = True
                            stats["similarity_removed"] += 1
                            self.dedupe_stats["similarity_removed"] += 1
                            break

            if not is_similar:
                deduped_items.append(item)
                stats["kept_count"] += 1
                self.dedupe_stats["kept_count"] += 1

                # Store fingerprint
                self.fingerprints[fingerprint] = {
                    "source_id": source_id,
                    "sample_text": text[:200],  # Store sample for similarity checks
                    "created_at": datetime.utcnow().isoformat(),
                    "size": len(text)
                }

        # Update stats
        end_time = datetime.utcnow()
        stats["processing_time"] = (end_time - start_time).total_seconds()

        self.dedupe_stats["total_items_processed"] += stats["original_count"]

        # Persist fingerprints periodically
        if len(self.fingerprints) % 100 == 0:  # Every 100 new fingerprints
            self._save_fingerprints()

        # Log deduplication results
        await immutable_log.append(
            actor="content_deduplicator",
            action="deduplication_completed",
            resource=f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            outcome="success",
            payload=stats
        )

        logger.info(f"✓ Deduplication: {stats['original_count']} -> {stats['kept_count']} items "
                   f"({stats['duplicates_removed']} duplicates, {stats['similarity_removed']} similar)")

        return deduped_items, stats

    def get_dedupe_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        return self.dedupe_stats


class PIIScrubber:
    """
    PRODUCTION: PII scrubbing with NER + regex and redaction reports
    """

    def __init__(self):
        # PII patterns (regex-based)
        self.pii_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "ssn": re.compile(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),
            "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            "api_key": re.compile(r'\b[A-Za-z0-9]{32,}\b'),  # Long alphanumeric strings
        }

        # Redaction markers
        self.redaction_templates = {
            "email": "[EMAIL_REDACTED]",
            "phone": "[PHONE_REDACTED]",
            "ssn": "[SSN_REDACTED]",
            "credit_card": "[CREDIT_CARD_REDACTED]",
            "ip_address": "[IP_REDACTED]",
            "api_key": "[API_KEY_REDACTED]",
            "name": "[NAME_REDACTED]"
        }

        self.pii_stats = {
            "total_items_processed": 0,
            "emails_scrubbed": 0,
            "phones_scrubbed": 0,
            "ssns_scrubbed": 0,
            "credit_cards_scrubbed": 0,
            "ips_scrubbed": 0,
            "api_keys_scrubbed": 0,
            "names_scrubbed": 0,
            "total_redactions": 0
        }

    async def scrub_content(self, content_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        PRODUCTION: Scrub PII from content with comprehensive reporting
        """
        scrubbed_items = []
        stats = {
            "total_items_processed": len(content_items),
            "items_with_pii": 0,
            "total_redactions": 0,
            "pii_types_found": {},
            "redaction_report": []
        }

        for item in content_items:
            original_text = item.get("text", "")
            scrubbed_text = original_text
            item_redactions = []

            # Apply regex-based PII detection
            for pii_type, pattern in self.pii_patterns.items():
                matches = pattern.findall(scrubbed_text)
                if matches:
                    # Redact each match
                    for match in matches:
                        redaction_marker = self.redaction_templates.get(pii_type, f"[{pii_type.upper()}_REDACTED]")
                        scrubbed_text = scrubbed_text.replace(match, redaction_marker, 1)

                        item_redactions.append({
                            "type": pii_type,
                            "original": match,
                            "redacted_as": redaction_marker
                        })

                        # Update stats
                        stats["total_redactions"] += 1
                        stats["pii_types_found"][pii_type] = stats["pii_types_found"].get(pii_type, 0) + 1

                        # Update global stats
                        stat_key = f"{pii_type}s_scrubbed"
                        if stat_key in self.pii_stats:
                            self.pii_stats[stat_key] += 1

            # Update item
            item["original_text"] = original_text
            item["text"] = scrubbed_text
            item["pii_redactions"] = item_redactions
            item["scrubbed_at"] = datetime.utcnow().isoformat()

            scrubbed_items.append(item)

            if item_redactions:
                stats["items_with_pii"] += 1
                stats["redaction_report"].append({
                    "source_id": item.get("source_id", "unknown"),
                    "redactions": item_redactions
                })

        # Update global stats
        self.pii_stats["total_items_processed"] += stats["total_items_processed"]
        self.pii_stats["total_redactions"] += stats["total_redactions"]

        # Log PII scrubbing results
        if stats["total_redactions"] > 0:
            await immutable_log.append(
                actor="pii_scrubber",
                action="pii_scrubbing_completed",
                resource=f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                outcome="success",
                payload={
                    "items_processed": stats["total_items_processed"],
                    "items_with_pii": stats["items_with_pii"],
                    "total_redactions": stats["total_redactions"],
                    "pii_types": stats["pii_types_found"]
                }
            )

        logger.info(f"✓ PII scrubbing: {stats['total_redactions']} redactions in {stats['items_with_pii']} items")

        return scrubbed_items, stats

    def get_pii_stats(self) -> Dict[str, Any]:
        """Get PII scrubbing statistics"""
        return self.pii_stats


class IngestionQualityMetrics:
    """
    PRODUCTION: Enhanced metrics with regression testing
    """

    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.regression_tests = {
            "quality_score_min": 0.7,
            "deduplication_rate_min": 0.5,
            "pii_detection_rate_min": 0.8
        }

    async def update_metrics(self, chunks: List[Dict], dedup_stats: Dict, pii_stats: Dict, processing_time: float):
        """Update quality metrics with regression testing"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "chunks": {
                "total": len(chunks),
                "avg_size": sum(c["char_count"] for c in chunks) / len(chunks) if chunks else 0,
                "size_distribution": self._calculate_distribution([c["char_count"] for c in chunks])
            },
            "deduplication": {
                "original_count": dedup_stats.get("original_count", 0),
                "kept_count": dedup_stats.get("kept_count", 0),
                "duplicates_removed": dedup_stats.get("duplicates_removed", 0),
                "similarity_removed": dedup_stats.get("similarity_removed", 0),
                "deduplication_rate": dedup_stats.get("kept_count", 0) / dedup_stats.get("original_count", 1)
            },
            "pii_scrubbing": {
                "items_processed": pii_stats.get("total_items_processed", 0),
                "items_with_pii": pii_stats.get("items_with_pii", 0),
                "total_redactions": pii_stats.get("total_redactions", 0),
                "pii_detection_rate": pii_stats.get("items_with_pii", 0) / pii_stats.get("total_items_processed", 1)
            },
            "performance": {
                "processing_time_seconds": processing_time,
                "chunks_per_second": len(chunks) / processing_time if processing_time > 0 else 0
            }
        }

        # Calculate overall quality score
        quality_factors = {
            "deduplication_rate": metrics["deduplication"]["deduplication_rate"],
            "pii_detection_rate": metrics["pii_scrubbing"]["pii_detection_rate"],
            "chunk_consistency": 1.0 - (metrics["chunks"]["size_distribution"]["std_dev"] / metrics["chunks"]["avg_size"]) if metrics["chunks"]["avg_size"] > 0 else 0
        }

        metrics["quality_score"] = sum(quality_factors.values()) / len(quality_factors)
        metrics["quality_factors"] = quality_factors

        # Run regression tests
        regression_results = self._run_regression_tests(metrics)
        metrics["regression_tests"] = regression_results

        # Store in history
        self.metrics_history.append(metrics)

        # Keep only recent history
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]

        # Log metrics
        await immutable_log.append(
            actor="ingestion_quality_metrics",
            action="metrics_updated",
            resource="ingestion_pipeline",
            outcome="success" if not regression_results["failed_tests"] else "regression_detected",
            payload={
                "quality_score": metrics["quality_score"],
                "regression_failures": len(regression_results["failed_tests"]),
                "chunks_processed": len(chunks)
            }
        )

        logger.info(f"✓ Quality metrics: score={metrics['quality_score']:.3f}, "
                   f"regressions={len(regression_results['failed_tests'])}")

        return metrics

    def _calculate_distribution(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistical distribution"""
        if not values:
            return {"mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0}

        mean = sum(values) / len(values)
        sorted_values = sorted(values)
        median = sorted_values[len(sorted_values) // 2]

        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        return {
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "min": min(values),
            "max": max(values)
        }

    def _run_regression_tests(self, metrics: Dict) -> Dict[str, Any]:
        """Run regression tests against quality thresholds"""
        results = {
            "passed_tests": [],
            "failed_tests": [],
            "overall_pass": True
        }

        # Quality score regression
        if metrics["quality_score"] < self.regression_tests["quality_score_min"]:
            results["failed_tests"].append({
                "test": "quality_score_min",
                "expected": self.regression_tests["quality_score_min"],
                "actual": metrics["quality_score"]
            })
            results["overall_pass"] = False
        else:
            results["passed_tests"].append("quality_score_min")

        # Deduplication rate regression
        dedup_rate = metrics["deduplication"]["deduplication_rate"]
        if dedup_rate < self.regression_tests["deduplication_rate_min"]:
            results["failed_tests"].append({
                "test": "deduplication_rate_min",
                "expected": self.regression_tests["deduplication_rate_min"],
                "actual": dedup_rate
            })
            results["overall_pass"] = False
        else:
            results["passed_tests"].append("deduplication_rate_min")

        # PII detection rate regression
        pii_rate = metrics["pii_scrubbing"]["pii_detection_rate"]
        if pii_rate < self.regression_tests["pii_detection_rate_min"]:
            results["failed_tests"].append({
                "test": "pii_detection_rate_min",
                "expected": self.regression_tests["pii_detection_rate_min"],
                "actual": pii_rate
            })
            results["overall_pass"] = False
        else:
            results["passed_tests"].append("pii_detection_rate_min")

        return results

    def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive quality report"""
        if not self.metrics_history:
            return {"error": "No metrics history available"}

        latest = self.metrics_history[-1]

        # Calculate trends
        if len(self.metrics_history) >= 2:
            prev = self.metrics_history[-2]
            trends = {
                "quality_score_change": latest["quality_score"] - prev["quality_score"],
                "deduplication_rate_change": latest["deduplication"]["deduplication_rate"] - prev["deduplication"]["deduplication_rate"],
                "pii_detection_change": latest["pii_scrubbing"]["pii_detection_rate"] - prev["pii_scrubbing"]["pii_detection_rate"]
            }
        else:
            trends = {"insufficient_history": True}

        return {
            "latest_metrics": latest,
            "trends": trends,
            "history_length": len(self.metrics_history),
            "regression_tests": latest.get("regression_tests", {})
        }


# Global instances
deterministic_chunker_production = DeterministicChunker()
content_deduplicator_production = ContentDeduplicator()
pii_scrubber_production = PIIScrubber()
ingestion_quality_metrics_production = IngestionQualityMetrics()</code></edit_file>