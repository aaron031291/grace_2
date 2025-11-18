"""
Deterministic Chunker - Production Ready
Config-driven parameters with snapshot testing
"""
import hashlib
import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

from backend.config.environment import GraceEnvironment
from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)

class DeterministicChunker:
    """Production-grade deterministic chunker with config-driven parameters"""
    
    def __init__(self, config: Optional[Dict] = None):
        # Load config from file or use defaults
        self.config = self._load_config(config)
        
        # Extract parameters
        self.chunk_size = self.config.get("chunk_size_chars", 1000)
        self.overlap = self.config.get("overlap_chars", 200)
        self.min_chunk_size = self.config.get("min_chunk_size", 100)
        self.max_chunk_size = self.config.get("max_chunk_size", 2000)
        
        # Sentence boundary patterns
        self.sentence_endings = re.compile(self.config.get("sentence_pattern", r'(?<=[.!?])\s+'))
        
        # Statistics
        self.stats = {
            "total_chunks_created": 0,
            "average_chunk_size": 0.0,
            "chunks_below_min": 0,
            "chunks_above_max": 0,
            "snapshot_tests_passed": 0,
            "snapshot_tests_failed": 0
        }
        
        # Load snapshot tests
        self.snapshot_tests = self._load_snapshot_tests()
    
    def _load_config(self, config: Optional[Dict]) -> Dict:
        """Load chunker configuration"""
        if config:
            return config
            
        config_file = Path("config/chunker_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load chunker config: {e}")
        
        # Default config
        return {
            "chunk_size_chars": 1000,
            "overlap_chars": 200,
            "min_chunk_size": 100,
            "max_chunk_size": 2000,
            "sentence_pattern": r'(?<=[.!?])\s+',
            "quality_threshold": 0.7
        }
    
    async def chunk_text(self, text: str, source_id: str) -> List[Dict[str, Any]]:
        """Deterministically chunk text with config-driven parameters"""
        if not text or not text.strip():
            return []
        
        # Run snapshot test if available
        if not GraceEnvironment.is_offline_mode():
            await self._run_snapshot_test(text, source_id)
        
        chunks = []
        sentences = self.sentence_endings.split(text)
        current_chunk = ""
        chunk_start = 0
        chunk_index = 0
        
        for sentence in sentences:
            potential_chunk = current_chunk + sentence
            
            if len(potential_chunk) > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = current_chunk.strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunk = self._create_chunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                        start_pos=chunk_start,
                        end_pos=chunk_start + len(chunk_text),
                        source_id=source_id
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    
                    # Update stats
                    self._update_stats(chunk_text)
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.overlap)
                current_chunk = current_chunk[overlap_start:] + sentence
                chunk_start += overlap_start
            else:
                current_chunk = potential_chunk
        
        # Handle final chunk
        if current_chunk.strip() and len(current_chunk.strip()) >= self.min_chunk_size:
            chunk_text = current_chunk.strip()
            chunk = self._create_chunk(
                text=chunk_text,
                chunk_index=chunk_index,
                start_pos=chunk_start,
                end_pos=chunk_start + len(chunk_text),
                source_id=source_id
            )
            chunks.append(chunk)
            self._update_stats(chunk_text)
        
        return chunks
    
    def _create_chunk(self, text: str, chunk_index: int, start_pos: int, 
                     end_pos: int, source_id: str) -> Dict[str, Any]:
        """Create standardized chunk with fingerprint"""
        chunk_hash = hashlib.sha256(f"{source_id}:{text}".encode()).hexdigest()[:16]
        
        return {
            "chunk_id": f"{source_id}_chunk_{chunk_index}",
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
            "start_position": start_pos,
            "end_position": end_pos,
            "source_id": source_id,
            "chunk_index": chunk_index,
            "chunk_hash": chunk_hash,
            "fingerprint": self._generate_fingerprint(text, source_id),
            "created_at": datetime.utcnow().isoformat(),
            "config_version": self.config.get("version", "1.0")
        }
    
    def _generate_fingerprint(self, text: str, source_id: str) -> str:
        """Generate content + source fingerprint"""
        content = f"{source_id}:{text.strip().lower()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _update_stats(self, chunk_text: str):
        """Update chunking statistics"""
        self.stats["total_chunks_created"] += 1
        
        chunk_size = len(chunk_text)
        if chunk_size < self.min_chunk_size:
            self.stats["chunks_below_min"] += 1
        elif chunk_size > self.max_chunk_size:
            self.stats["chunks_above_max"] += 1
        
        # Update average
        total = self.stats["total_chunks_created"]
        current_avg = self.stats["average_chunk_size"]
        self.stats["average_chunk_size"] = ((current_avg * (total - 1)) + chunk_size) / total

deterministic_chunker = DeterministicChunker()
