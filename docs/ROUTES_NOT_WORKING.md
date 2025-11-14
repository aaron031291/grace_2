"""
Simple test endpoint to verify routing works
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {
        "status": "working",
        "message": "If you see this, routes are registered correctly!"
    }

@router.get("/books/test")
async def books_test():
    return {
        "total_books": 0,
        "message": "Books route is working"
    }
