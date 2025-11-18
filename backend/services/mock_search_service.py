"""
Mock Search Service - For CI/testing/offline mode

Returns canned responses to avoid hitting real APIs (DuckDuckGo, Google)
"""

from typing import List, Dict, Any
import asyncio


class MockSearchService:
    """
    Mock search service that returns predefined results
    
    Use in CI or when SEARCH_PROVIDER=mock
    """
    
    def __init__(self):
        self.name = "mock"
        self._call_count = 0
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Mock search - returns canned results
        
        Args:
            query: Search query (ignored, for testing)
            max_results: Number of results to return
            **kwargs: Ignored
        
        Returns:
            List of mock search results
        """
        await asyncio.sleep(0.1)  # Simulate API latency
        
        self._call_count += 1
        
        # Return mock results that look like real search results
        results = [
            {
                "title": f"Mock Result 1: {query}",
                "link": "https://example.com/mock-1",
                "snippet": f"This is a mock search result for '{query}'. In production, this would be real search data.",
                "source": "mock",
                "rank": 1
            },
            {
                "title": f"Mock Result 2: Documentation for {query}",
                "link": "https://example.com/docs/mock-2",
                "snippet": f"Comprehensive documentation about {query}. This mock result simulates a documentation page.",
                "source": "mock",
                "rank": 2
            },
            {
                "title": f"Mock Result 3: Tutorial on {query}",
                "link": "https://example.com/tutorial/mock-3",
                "snippet": f"Learn how to use {query} with this step-by-step tutorial. (Mock result)",
                "source": "mock",
                "rank": 3
            }
        ]
        
        return results[:max_results]
    
    async def search_news(
        self,
        query: str,
        max_results: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Mock news search"""
        await asyncio.sleep(0.1)
        
        return [
            {
                "title": f"Breaking: {query} News Update",
                "link": "https://example.com/news/mock-1",
                "snippet": f"Latest news about {query}. (Mock result)",
                "source": "mock_news",
                "date": "2024-01-15",
                "rank": 1
            }
        ][:max_results]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mock service stats"""
        return {
            "provider": "mock",
            "total_calls": self._call_count,
            "status": "active",
            "rate_limit": "unlimited",
            "note": "Mock service - not hitting real APIs"
        }


# Singleton instance
mock_search_service = MockSearchService()


async def get_mock_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Convenience function for mock search"""
    return await mock_search_service.search(query, max_results)
