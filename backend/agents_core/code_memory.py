"""
Code Memory Module for Elite Coding Agent
Provides codebase memory and context for coding operations
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class CodeMemoryEntry:
    """Entry in code memory"""
    file_path: str
    code_snippet: str
    context: str
    language: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CodeMemory:
    """
    Code memory system for elite coding agent
    Stores and retrieves code context, patterns, and knowledge
    """
    
    def __init__(self):
        self.memory: Dict[str, CodeMemoryEntry] = {}
        self.patterns: Dict[str, List[str]] = {}
        logger.info("[CODE_MEMORY] Initialized")
    
    async def store(self, file_path: str, code: str, context: str, language: str = "python", tags: List[str] = None) -> str:
        """Store code in memory"""
        entry = CodeMemoryEntry(
            file_path=file_path,
            code_snippet=code,
            context=context,
            language=language,
            tags=tags or []
        )
        
        self.memory[file_path] = entry
        logger.debug(f"[CODE_MEMORY] Stored: {file_path}")
        return file_path
    
    async def retrieve(self, file_path: str) -> Optional[CodeMemoryEntry]:
        """Retrieve code from memory"""
        return self.memory.get(file_path)
    
    async def search(self, query: str, language: str = None) -> List[CodeMemoryEntry]:
        """Search code memory"""
        results = []
        for entry in self.memory.values():
            if language and entry.language != language:
                continue
            if query.lower() in entry.code_snippet.lower() or query.lower() in entry.context.lower():
                results.append(entry)
        return results
    
    async def get_patterns(self, pattern_type: str) -> List[str]:
        """Get code patterns of a specific type"""
        return self.patterns.get(pattern_type, [])
    
    async def learn_pattern(self, pattern_type: str, pattern: str):
        """Learn a new code pattern"""
        if pattern_type not in self.patterns:
            self.patterns[pattern_type] = []
        if pattern not in self.patterns[pattern_type]:
            self.patterns[pattern_type].append(pattern)
            logger.debug(f"[CODE_MEMORY] Learned pattern: {pattern_type}")

# Global instance
code_memory = CodeMemory()
