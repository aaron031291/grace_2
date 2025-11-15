"""
Immutable Log Service
Append-only audit trail - Grace's black box

Every action goes here. Cannot be modified or deleted.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ImmutableLogEntry:
    """Single log entry"""
    
    def __init__(
        self,
        entry_id: str,
        timestamp: datetime,
        actor: str,
        action: str,
        resource: str,
        subsystem: Optional[str],
        decision: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.actor = actor
        self.action = action
        self.resource = resource
        self.subsystem = subsystem
        self.decision = decision
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat(),
            'actor': self.actor,
            'action': self.action,
            'resource': self.resource,
            'subsystem': self.subsystem,
            'decision': self.decision,
            'metadata': self.metadata
        }


class ImmutableLog:
    """
    Immutable audit log
    
    Features:
    - Append-only (no modification/deletion)
    - Local file + optional remote mirror
    - Indexed for fast search
    - Cryptographically signed (future)
    """
    
    def __init__(self):
        self.log_file = Path('logs/immutable_audit.jsonl')
        self.entry_count = 0
        self.running = False
        
        # In-memory index for fast search
        self.index = []
    
    async def start(self):
        """Start immutable log service"""
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create log file if doesn't exist
        if not self.log_file.exists():
            self.log_file.touch()
        
        # Load index
        await self._load_index()
        
        self.running = True
        
        logger.info(f"[IMMUTABLE-LOG] Started - {self.entry_count} existing entries")
    
    async def append(
        self,
        actor: str,
        action: str,
        resource: str,
        decision: Dict[str, Any],
        metadata: Dict[str, Any] = None,
        subsystem: Optional[str] = None
    ) -> str:
        """
        Append entry to log (immutable)
        
        Args:
            actor: Who performed the action
            action: What action was performed
            resource: What resource was affected
            decision: Decision details
            metadata: Additional metadata
        
        Returns:
            Entry ID
        """
        
        self.entry_count += 1
        entry_id = f"log_{self.entry_count}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        
        entry = ImmutableLogEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            actor=actor,
            action=action,
            resource=resource,
            subsystem=subsystem,
            decision=decision,
            metadata=metadata or {}
        )
        
        # Append to file (immutable)
        async with asyncio.Lock():
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')
        
        # Add to index
        self.index.append({
            'entry_id': entry_id,
            'timestamp': entry.timestamp,
            'actor': actor,
            'action': action
        })
        
        logger.debug(f"[IMMUTABLE-LOG] Appended: {entry_id}")
        
        return entry_id
    
    async def _load_index(self):
        """Load index from log file"""
        
        if not self.log_file.exists():
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self.index.append({
                            'entry_id': entry['entry_id'],
                            'timestamp': datetime.fromisoformat(entry['timestamp']),
                            'actor': entry['actor'],
                            'action': entry['action']
                        })
                        self.entry_count += 1
        
        except Exception as e:
            logger.error(f"[IMMUTABLE-LOG] Error loading index: {e}")
    
    async def search(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search log entries"""
        
        results = []
        
        for idx_entry in reversed(self.index):  # Most recent first
            # Apply filters
            if actor and idx_entry['actor'] != actor:
                continue
            
            if action and idx_entry['action'] != action:
                continue
            
            if start_time and idx_entry['timestamp'] < start_time:
                continue
            
            if end_time and idx_entry['timestamp'] > end_time:
                continue
            
            results.append(idx_entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get log statistics"""
        return {
            'total_entries': self.entry_count,
            'log_file': str(self.log_file),
            'log_size_bytes': self.log_file.stat().st_size if self.log_file.exists() else 0,
            'running': self.running
        }


# Global instance - Grace's black box
immutable_log = ImmutableLog()
