"""
Simple Terminal Chat with GRACE
Direct LLM interaction via API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def chat():
    """Interactive chat with GRACE"""
    
    print("\n" + "="*70)
    print("  GRACE - Terminal Chat")
    print("  Type 'exit' to quit, 'status' for system status")
    print("="*70 + "\n")

    # Check if GRACE is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=30)
        if health.status_code != 200:
            print("ERROR: GRACE is not responding. Make sure she's running on port 8000")
            return
        
        print("GRACE: Hello! I'm operational and ready to assist.\n")
    except Exception as e:
        print(f"ERROR: Cannot connect to GRACE: {e}")
        print("Make sure GRACE is running: .venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return

    # Select chat mode
    while True:
        mode = input("Select chat mode (normal, multimodal, voice): ").lower()
        if mode in ["normal", "multimodal", "voice"]:
            break
        else:
            print("Invalid mode. Please choose 'normal', 'multimodal', or 'voice'.")

    session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Exit commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nGRACE: Goodbye! Session saved.\n")
                break
            
            # Status command
            if user_input.lower() == "status":
                show_status()
                continue
            
            # Chat with GRACE via API
            if mode == "normal":
                chat_normal(user_input, session_id)
            elif mode == "multimodal":
                chat_multimodal(user_input, session_id)
            elif mode == "voice":
                chat_voice(user_input, session_id)
        
        
def chat_normal(user_input, session_id):
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": user_input,
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            grace_response = data.get("response", "...")
            print(f"\nGRACE: {grace_response}\n")
        else:
            print(f"\nGRACE: [Error {response.status_code}] {response.text}\n")
    
    except requests.exceptions.Timeout:
        print("\nGRACE: (thinking...) Request timed out. Try again.\n")
    except Exception as e:
        print(f"\nERROR: {e}\n")

def chat_multimodal(user_input, session_id):
    try:
        modality = input("Select modality (text, vision, code, reasoning, fast): ").lower()
        if modality not in ["text", "vision", "code", "reasoning", "fast"]:
            print("Invalid modality. Defaulting to 'text'.")
            modality = "text"

        response = requests.post(
            f"{BASE_URL}/api/multimodal/chat",
            json={
                "message": user_input,
                "session_id": session_id,
                "modality": modality
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            grace_response = data.get("response", "...")
            print(f"\nGRACE: {grace_response}\n")
        else:
            print(f"\nGRACE: [Error {response.status_code}] {response.text}\n")
    
    except requests.exceptions.Timeout:
        print("\nGRACE: (thinking...) Request timed out. Try again.\n")
    except Exception as e:
        print(f"\nERROR: {e}\n")

def chat_voice(user_input, session_id):
    try:
        response = requests.post(
            f"{BASE_URL}/api/multimodal/voice/tts",
            json={
                "text": user_input,
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"\nGRACE: [Audio generated at {data.get('audio_url')}]\n")
            else:
                print(f"\nGRACE: [Error generating audio]\n")
        else:
            print(f"\nGRACE: [Error {response.status_code}] {response.text}\n")
    
    except requests.exceptions.Timeout:
        print("\nGRACE: (thinking...) Request timed out. Try again.\n")
    except Exception as e:
        print(f"\nERROR: {e}\n")
        
        

def show_status():
    """Show GRACE system status"""
    try:
        health = requests.get(f"{BASE_URL}/health").json()
        
        print("\n=== GRACE System Status ===")
        print(f"Status: {health.get('status', 'unknown').upper()}")
        print(f"Version: {health.get('version', 'unknown')}")
        print(f"Uptime: {health.get('uptime_seconds', 0) / 3600:.1f} hours")
        
        services = health.get('services', {})
        print("\nServices:")
        for name, service in services.items():
            status = service.get('status', 'unknown')
            print(f"  - {name}: {status}")
        
        metrics = health.get('metrics', {})
        print(f"\nMetrics:")
        print(f"  CPU: {metrics.get('cpu_usage_percent', 0)}%")
        print(f"  Memory: {metrics.get('memory_usage_mb', 0):.0f} MB")
        print(f"  Requests: {metrics.get('total_requests', 0)}")
        print()
    
    except Exception as e:
        print(f"Error getting status: {e}\n")


if __name__ == "__main__":
    chat()
