"""
Test endpoints to verify routing works
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Simple test to verify routes are registered"""
    return {
        "status": "working",
        "message": "Routes are registered correctly!",
        "endpoints_available": [
            "/api/test",
            "/api/books/stats",
            "/api/books/recent",
            "/api/librarian/file-operations",
            "/api/librarian/organization-suggestions"
        ]
    }

@router.get("/books/test")
async def books_test():
    """Test book routes specifically"""
    return {
        "status": "working",
        "message": "Book routes are working!",
        "total_books": 0
    }
