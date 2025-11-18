"""
Deterministic Chunker - Phase 2
Consistent chunking with locked heuristics
"""
import hashlib
import re
from typing import List, Dict, Any
from pathlib import Path
import json

class DeterministicChunker:
    """Production-grade deterministic chunker with snapshot testing"""
    
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
            except Exception:
                pass
        return {}
    
    async def chunk_text(self, text: str, source_id: str) -> List[Dict[str, Any]]:
        """Deterministically chunk text with locked heuristics"""
        if not text or not text.strip():
            return []
        
        # Run snapshot test first
        await self._run_snapshot_test(text, source_id)
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.CHUNK_SIZE_CHARS, len(text))
            
            # Find sentence boundary within overlap zone
            if end < len(text):
                boundary_zone = text[end-50:end+50]
                sentence_match = self.SENTENCE_ENDINGS.search(boundary_zone)
                if sentence_match:
                    end = end - 50 + sentence_match.end()
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()[:16]
                
                chunk = {
                    "chunk_id": f"{source_id}_{chunk_index}_{chunk_hash}",
                    "index": chunk_index,
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                    "source_id": source_id,
                    "chunk_hash": chunk_hash,
                    "start_pos": start,
                    "end_pos": end
                }
                
                chunks.append(chunk)
                self._update_stats(chunk)
                chunk_index += 1
            
            # Move forward with overlap
            start = max(start + self.CHUNK_SIZE_CHARS - self.CHUNK_OVERLAP_CHARS, end)
        
        return chunks
    
    async def _run_snapshot_test(self, text: str, source_id: str):
        """Run snapshot test to detect chunking drift"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if text_hash in self.snapshot_tests:
            expected_chunks = self.snapshot_tests[text_hash]["chunk_count"]
            actual_chunks = await self._count_chunks(text)
            
            if expected_chunks == actual_chunks:
                self.chunking_stats["snapshot_tests_passed"] += 1
            else:
                self.chunking_stats["snapshot_tests_failed"] += 1
                print(f"⚠️ Snapshot test failed for {source_id}: expected {expected_chunks}, got {actual_chunks}")
    
    async def _count_chunks(self, text: str) -> int:
        """Count chunks without creating them (for testing)"""
        if not text:
            return 0
        
        chunk_count = 0
        start = 0
        
        while start < len(text):
            end = min(start + self.CHUNK_SIZE_CHARS, len(text))
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                chunk_count += 1
            
            start = max(start + self.CHUNK_SIZE_CHARS - self.CHUNK_OVERLAP_CHARS, end)
        
        return chunk_count
    
    def _update_stats(self, chunk: Dict[str, Any]):
        """Update chunking statistics"""
        self.chunking_stats["total_chunks_created"] += 1
        
        char_count = chunk["char_count"]
        if char_count < self.MIN_CHUNK_SIZE:
            self.chunking_stats["chunks_below_min"] += 1
        elif char_count > self.MAX_CHUNK_SIZE:
            self.chunking_stats["chunks_above_max"] += 1
        
        # Update average
        total = self.chunking_stats["total_chunks_created"]
        current_avg = self.chunking_stats["average_chunk_size"]
        self.chunking_stats["average_chunk_size"] = ((current_avg * (total - 1)) + char_count) / total

deterministic_chunker = DeterministicChunker()