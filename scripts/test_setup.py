import requests
import sys

print("=" * 50)
print("Grace Backend Connection Test")
print("=" * 50)
print()

# Test 1: Health check
print("1. Testing backend health endpoint...")
try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("   ✅ Backend is running!")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Got status code: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Backend is NOT running!")
    print(f"   Error: {e}")
    print()
    print("   START THE BACKEND FIRST:")
    print("   Run: python3 main.py")
    sys.exit(1)

print()

# Test 2: Register a user
print("2. Registering test user...")
try:
    response = requests.post(
        "http://localhost:8000/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "test123"}
    )
    if response.status_code in [201, 400]:  # 201 = created, 400 = already exists
        if response.status_code == 201:
            print("   ✅ User registered successfully!")
        else:
            print("   ℹ️  User already exists (that's OK)")
    else:
        print(f"   ❌ Registration failed with status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Registration failed: {e}")

print()

# Test 3: Login
print("3. Testing login...")
try:
    response = requests.post(
        "http://localhost:8000/auth/login",
        json={"username": "testuser", "password": "test123"}
    )
    if response.status_code == 200:
        print("   ✅ Login successful!")
        token = response.json().get("access_token")
        print(f"   Token: {token[:20]}...")
    else:
        print(f"   ❌ Login failed with status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Login failed: {e}")

print()

# Test 4: Chat
print("4. Testing chat endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": "Hello Grace!", "user_id": 1}
    )
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Chat working!")
        print(f"   Grace replied: {data.get('response')}")
    else:
        print(f"   ❌ Chat failed with status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Chat failed: {e}")

print()
print("=" * 50)
print("NEXT STEPS:")
print("=" * 50)
print("1. Keep the backend running (python3 main.py)")
print("2. Open a NEW terminal")
print("3. cd grace-frontend")
print("4. npm run dev")
print("5. Open browser: http://localhost:5173")
print("6. Login with username: testuser, password: test123")
print("=" * 50)
