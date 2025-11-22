# memory_buffer.py
"""Short‑term memory buffer for GraceAgent.
Stores recent observations in memory for quick retrieval.
"""
import asyncio
from typing import List, Dict, Any

class MemoryBuffer:
    """In‑memory buffer for recent observations.
    Simple async interface compatible with GraceAgent.
    """
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._buffer: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def store_observation(self, observation: Dict[str, Any]):
        """Store a new observation, evict oldest if over capacity."""
        async with self._lock:
            self._buffer.append(observation)
            if len(self._buffer) > self.max_size:
                self._buffer.pop(0)

    async def get_recent(self, count: int = 5) -> List[Dict[str, Any]]:
        """Return the most recent `count` observations."""
        async with self._lock:
            return self._buffer[-count:]
