import asyncio
from backend.services.google_search_service import google_search_service

async def reset_search_service():
    print("Resetting Google Search Service state...")
    
    # Initialize service (triggers reset logic we just added)
    await google_search_service.initialize()
    
    # Explicitly clear memory state
    google_search_service.offline_mode = False
    google_search_service.consecutive_failures = 0
    google_search_service.backoff_until = 0
    
    # Check status
    metrics = await google_search_service.get_metrics()
    print(f"Status: {'Online' if not metrics['offline_mode'] else 'Offline'}")
    print(f"Backoff: {'Active' if metrics['in_backoff'] else 'Clear'}")
    print(f"Failures: {metrics['consecutive_failures']}")
    print("Reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_search_service())
