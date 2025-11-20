"""
Live Remote Access Client
Interactive client for Grace's remote access system
"""

import requests
import json
import getpass
import os
import argparse
from pathlib import Path

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api/remote-access"  # Fixed: was /api/remote, should be /api/remote-access
CONFIG_FILE = Path(".remote_access_config.json")


class RemoteAccessClient:
    def __init__(self):
        self.api_url = API_URL
        self.device_id = None
        self.token = None
        self.session_id = None  # Add session_id
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.device_id = config.get("device_id")
                self.token = config.get("token")
                self.session_id = config.get("session_id") # Load session_id

    def save_config(self):
        """Save device ID and token"""
        config = {
            'device_id': self.device_id,
            'token': self.token,
            'session_id': self.session_id
        }
        CONFIG_FILE.write_text(json.dumps(config, indent=2))

    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def allowlist_device(self, approved_by="aaron"):
        """Allowlist this device"""
        print(f"\n🔓 Allowlisting device...")
        
        data = {
            "device_id": self.device_id,
            "approved_by": approved_by
        }
        
        response = requests.post(f"{self.api_url}/devices/allowlist", json=data)
        result = response.json()
        
        if 'allowlisted' in result:
            print(f"✅ Device allowlisted")
            return True
        else:
            print(f"⚠️  {result}")
            raise ValueError(f"API error: {result.get('detail') or result.get('message')}")  # Raise exception for failed allowlisting

    def assign_role(self, role="developer", approved_by="aaron"):
        """Assign RBAC role"""
        print(f"\n🎭 Assigning role: {role}")
        
        data = {
            "device_id": self.device_id,
            "role_name": role,
            "approved_by": approved_by
        }
        
        response = requests.post(f"{self.api_url}/roles/assign", json=data)
        result = response.json()
        
        if 'role' in result:
            print(f"✅ Role assigned: {result['role']}")
            print(f"   Permissions: {', '.join(result['permissions'][:8])}")
            return True
        else:
            print(f"⚠️  {result}")
            raise ValueError(f"API error: {result.get('detail') or result.get('message')}")  # Raise exception for failed role assignment

    def create_session(self):
        """Create remote session"""
        print(f"\n🔐 Creating session with MFA...")
        
        data = {
            "device_id": self.device_id,
            "mfa_token": "TEST_123456"  # Dev MFA token
        }
        
        response = requests.post(f"{self.api_url}/session/create", json=data)
        result = response.json()
        
        if result.get('allowed'):
            self.token = result['token']
            self.session_id = result['session_id']
            self.save_config()
            
            print(f"✅ Session created: {self.session_id}")
            print(f"   Token: {self.token[:40]}...")
            print(f"   Expires: {result['expires_at']}")
            print(f"   Recording: {result.get('recording_id')}")
            return True
        else:
            print(f"❌ Session creation failed: {result}")
            return False

    def get_token(self):
        """Authenticate and get JWT token"""
        if self.token:
            return True

        username = "admin"
        password = "password"
        
        try:
            response = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.save_config()
                print("\u2713 Authenticated successfully.")
                return True
            else:
                print(f"[X] Authentication failed: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[X] Error connecting to backend: {e}")
            return False

    def interactive_shell(self):
        """Start an interactive shell."""
        if not self.session_id:
            print("[X] No active session. Please run 'setup' first.")
            return

        print("\nConnected to remote shell. Type 'exit' to quit.")
        while True:
            try:
                command = input(f"({self.device_id}) grace> ")
                if command.lower() == 'exit':
                    break
                self.execute_command(command)
            except KeyboardInterrupt:
                break
        print("Disconnected.")

    def execute_command(self, command: str):
        """Execute a single command."""
        if not self.session_id:
            print("[X] No active session. Please run 'setup' first.")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.post(f"{self.api_url}/execute", headers=headers, json={
                "session_id": self.session_id,
                "command": command
            })
            result = response.json()
            if response.status_code == 200:
                print(result.get("output"))
            else:
                print(f"[X] Error: {result.get('detail')}")
        except requests.exceptions.RequestException as e:
            print(f"[X] Error connecting to backend: {e}")

    def get_status(self):
        """Get the status of the current session."""
        if not self.session_id:
            print("[X] No active session.")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(f"{self.api_url}/session/{self.session_id}", headers=headers)
            if response.status_code == 200:
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"[X] Error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[X] Error connecting to backend: {e}")

    def setup(self, device_name):
        """Setup device and start a session"""
        self.device_id = device_name
        print(f"\n[+] Starting session for device: {self.device_id}")
        self.start_session(target_system="local_shell", reason="Initial setup")

    def start_session(self, target_system: str, reason: str):
        """Start a new remote access session"""
        try:
            # First, get a token
            if not self.get_token():
                return

            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{self.api_url}/session/start", headers=headers, json={
                "target_system": target_system,
                "reason": reason
            })

            if response.status_code == 201:
                result = response.json()
                self.session_id = result.get("session_id")
                self.save_config()
                print(f"\u2713 Session started successfully! Session ID: {self.session_id}")
            else:
                print(f"[X] Failed to start session: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[X] Error connecting to backend: {e}")

    def register(self, username, password):
        """Register a new user"""
        try:
            response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
            if response.status_code == 201:
                print(f"\u2713 User '{username}' registered successfully.")
                return True
            else:
                print(f"[X] Registration failed: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[X] Error connecting to backend: {e}")
            return False


def main():
    client = RemoteAccessClient()
    parser = argparse.ArgumentParser(description="Grace Remote Access Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser("register", help="Register a new user")
    register_parser.add_argument("username", help="Username")
    register_parser.add_argument("password", help="Password")

    setup_parser = subparsers.add_parser("setup", help="Setup a new device and session")
    setup_parser.add_argument("device_name", help="A name for this device")

    shell_parser = subparsers.add_parser("shell", help="Start an interactive shell")
    
    exec_parser = subparsers.add_parser("exec", help="Execute a single command")
    exec_parser.add_argument("cmd", help="The command to execute")

    status_parser = subparsers.add_parser("status", help="Get session status")

    setup_and_shell_parser = subparsers.add_parser("setup_and_shell", help="Setup a new device and immediately enter the shell")
    setup_and_shell_parser.add_argument("device_name", help="A name for this device")

    args = parser.parse_args()

    if args.command == "register":
        client.register(args.username, args.password)
    elif args.command == "setup":
        client.setup(args.device_name)
    elif args.command == "shell":
        client.interactive_shell()
    elif args.command == "exec":
        client.execute_command(args.cmd)
    elif args.command == "status":
        client.get_status()
    elif args.command == "setup_and_shell":
        client.setup(args.device_name)
        client.interactive_shell()

if __name__ == "__main__":
    main()
