#!/usr/bin/env python
"""Test memory API import"""

try:
    from backend.routes import memory_api
    print("✓ Memory API router imported successfully")
    print(f"✓ Router prefix: {memory_api.router.prefix}")
    print(f"✓ Router tags: {memory_api.router.tags}")
    
    # Count routes
    routes = [r for r in memory_api.router.routes]
    print(f"✓ Number of routes: {len(routes)}")
    
    for route in routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = list(route.methods)
            print(f"  - {methods[0] if methods else 'GET'} {route.path}")
    
except Exception as e:
    print(f"✗ Failed to import memory API: {e}")
    import traceback
    traceback.print_exc()
