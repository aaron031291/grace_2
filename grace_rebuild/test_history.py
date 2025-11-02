import requests

# Login
login_res = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Send a test message
chat_res = requests.post(
    "http://localhost:8000/api/chat/",
    json={"message": "show me my history"},
    headers=headers
)

print("Status:", chat_res.status_code)
print("Response:", chat_res.json())
