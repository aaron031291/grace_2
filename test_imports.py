"""Test if all imports work"""

print("Testing imports...")

try:
    from backend.routes.remote_session_api import router
    print("✅ remote_session_api imports OK")
except Exception as e:
    print(f"❌ remote_session_api failed: {e}")

try:
    from backend.routes.autonomous_learning_api import router
    print("✅ autonomous_learning_api imports OK")
except Exception as e:
    print(f"❌ autonomous_learning_api failed: {e}")

try:
    from backend.main import app
    print("✅ main.py imports OK")
except Exception as e:
    print(f"❌ main.py failed: {e}")

print("\nAll imports successful! Backend should start now.")
