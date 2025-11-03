"""
Backend integration tests
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from grace_client import GraceAPIClient, GraceResponse


@pytest.mark.asyncio
class TestAPIClient:
    """Test API client"""
    
    async def test_client_connection(self):
        """Test client connection"""
        async with GraceAPIClient() as client:
            assert client._client is not None
    
    async def test_health_check(self):
        """Test health check endpoint"""
        async with GraceAPIClient() as client:
            # This will fail if backend not running, but tests the method
            response = await client.health_check()
            assert isinstance(response, GraceResponse)
    
    async def test_authentication_required(self):
        """Test that protected endpoints require auth"""
        async with GraceAPIClient() as client:
            # Without authentication, should get auth error
            response = await client.list_tasks()
            
            if not response.success:
                assert "Authentication" in response.error or "401" in str(response.error)
    
    async def test_response_structure(self):
        """Test response structure"""
        response = GraceResponse(success=True, data={"test": "value"})
        
        assert response.success == True
        assert response.data == {"test": "value"}
        assert response.error is None


@pytest.mark.asyncio
class TestMockBackend:
    """Test with mock backend responses"""
    
    async def test_mock_login(self, mocker):
        """Test login with mocked response"""
        async with GraceAPIClient() as client:
            # Mock the request method
            mock_response = GraceResponse(
                success=True,
                data={"access_token": "test_token", "token_type": "bearer"}
            )
            
            mocker.patch.object(client, '_request', return_value=mock_response)
            
            response = await client.login("test_user", "test_pass")
            
            assert response.success
            assert client.token == "test_token"
            assert client.username == "test_user"
    
    async def test_mock_chat(self, mocker):
        """Test chat with mocked response"""
        async with GraceAPIClient() as client:
            client.token = "test_token"  # Fake authentication
            
            mock_response = GraceResponse(
                success=True,
                data={"response": "Hello, I am Grace!"}
            )
            
            mocker.patch.object(client, '_request', return_value=mock_response)
            
            response = await client.chat("Hello")
            
            assert response.success
            assert "Grace" in response.data["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
