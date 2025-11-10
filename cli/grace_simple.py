#!/usr/bin/env python3
"""
Grace Simple CLI - Direct access without complex imports
Works standalone for immediate testing
"""

import sys
import requests
import json
from pathlib import Path

BACKEND_URL = "http://localhost:8000"

def check_backend():
    """Check if backend is running"""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if resp.status_code == 200:
            print("✓ Backend connected")
            return True
    except:
        pass
    print("✗ Backend not available - Start with: uvicorn backend.main:app --reload")
    return False

def chat(message: str, token: str = None):
    """Send a chat message to Grace"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={"message": message},
            headers=headers,
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "No response")
        else:
            return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {e}"

def get_health():
    """Get health status"""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except:
        return {"status": "error", "message": "Backend not available"}

def get_metrics():
    """Get cognition metrics"""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/cognition/metrics", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        return {}

def register(username: str, password: str):
    """Register new user"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": username, "password": password},
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": resp.text}
    except Exception as e:
        return {"error": str(e)}

def login(username: str, password: str):
    """Login and get token"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": username, "password": password},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token")
        else:
            return None
    except:
        return None

def main():
    print("=" * 50)
    print("  GRACE AI - Simple CLI")
    print("=" * 50)
    print()
    
    if not check_backend():
        sys.exit(1)
    
    # Get command
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python grace_simple.py health        - Check health")
        print("  python grace_simple.py metrics       - View metrics")
        print("  python grace_simple.py register      - Register user")
        print("  python grace_simple.py login         - Login")
        print("  python grace_simple.py chat <msg>    - Chat with Grace")
        print()
        print("Example:")
        print('  python grace_simple.py chat "Hello Grace"')
        return
    
    command = sys.argv[1].lower()
    
    if command == "health":
        health = get_health()
        print(json.dumps(health, indent=2))
    
    elif command == "metrics":
        metrics = get_metrics()
        print(json.dumps(metrics, indent=2))
    
    elif command == "register":
        username = input("Username: ")
        password = input("Password: ")
        result = register(username, password)
        print(json.dumps(result, indent=2))
    
    elif command == "login":
        username = input("Username: ")
        password = input("Password: ")
        token = login(username, password)
        if token:
            print(f"✓ Login successful!")
            print(f"Token: {token}")
            # Save token
            config_dir = Path.home() / ".grace"
            config_dir.mkdir(exist_ok=True)
            (config_dir / "token").write_text(token)
            print(f"Token saved to {config_dir / 'token'}")
        else:
            print("✗ Login failed")
    
    elif command == "chat":
        if len(sys.argv) < 3:
            print("Usage: python grace_simple.py chat <message>")
            return
        
        message = " ".join(sys.argv[2:])
        
        # Try to load token
        token = None
        token_file = Path.home() / ".grace" / "token"
        if token_file.exists():
            token = token_file.read_text().strip()
        
        print(f"You: {message}")
        response = chat(message, token)
        print(f"Grace: {response}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
