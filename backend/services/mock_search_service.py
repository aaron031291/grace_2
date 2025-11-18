"""Mock search service for CI/testing environments.

Provides a drop-in replacement for real search providers (Google, DuckDuckGo)
that returns pre-defined mock results without making external network calls.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MockSearchService:
    """Mock search service that returns canned responses."""
    
    def __init__(self):
        self.search_count = 0
        logger.info("MockSearchService initialized (no external API calls)")
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Return mock search results for any query.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            **kwargs: Additional search parameters (ignored)
        
        Returns:
            List of mock search results
        """
        self.search_count += 1
        
        logger.info(
            f"MockSearchService.search(query='{query}', num_results={num_results}) "
            f"[call #{self.search_count}]"
        )
        
        # Return generic mock results
        results = []
        for i in range(min(num_results, 5)):  # Cap at 5 mock results
            results.append({
                "title": f"Mock Result {i+1} for '{query}'",
                "link": f"https://example.com/result_{i+1}",
                "snippet": f"This is a mock search result snippet for query: {query}. "
                          f"Result number {i+1} of {num_results} requested.",
                "source": "mock",
                "rank": i + 1,
            })
        
        return results
    
    async def get_status(self) -> Dict[str, Any]:
        """Return mock service status."""
        return {
            "provider": "mock",
            "status": "healthy",
            "total_searches": self.search_count,
            "note": "Mock search service - no external API calls",
        }


# Singleton instance
mock_search_service = MockSearchService()


def get_search_service() -> MockSearchService:
    """Get the mock search service instance."""
    return mock_search_service
