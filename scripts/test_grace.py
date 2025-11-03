import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_chat(message):
    print(f"Testing /chat with message: '{message}'")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"User: {result['user_message']}")
    print(f"Grace: {result['response']}\n")
    return result

def test_metrics():
    print("Testing /chat/metrics endpoint...")
    response = requests.get(f"{BASE_URL}/chat/metrics")
    print(f"Status: {response.status_code}")
    print(f"Metrics: {json.dumps(response.json(), indent=2)}\n")

def test_tasks():
    print("Creating a test task...")
    response = requests.post(
        f"{BASE_URL}/tasks",
        json={"title": "Test Grace integration", "description": "Make sure Grace can list tasks"}
    )
    print(f"Status: {response.status_code}")
    print(f"Task created: {response.json()}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Grace API Test Suite")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        
        print("Creating a task first...")
        test_tasks()
        
        print("Starting conversation with Grace...")
        test_chat("Hello Grace!")
        test_chat("Show me my tasks")
        test_chat("How are you?")
        test_chat("Thanks!")
        
        test_metrics()
        
        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"Error: {e}")
