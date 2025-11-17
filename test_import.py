#!/usr/bin/env python3
try:
    from backend.routes.vault_api import router
    print("SUCCESS: Vault API imports successfully")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
