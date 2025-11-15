"""
Live Remote Access Client
Interactive client for Grace's remote access system
"""

import requests
import json
import sys
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
CONFIG_FILE = Path(".remote_access_config.json")


class RemoteAccessClient:
    def __init__(self):
        self.device_id = None
        self.token = None
        self.session_id = None
        self.load_config()
    
    def load_config(self):
        """Load saved device ID and token"""
        if CONFIG_FILE.exists():
            try:
                config = json.loads(CONFIG_FILE.read_text())
                self.device_id = config.get('device_id')
                self.token = config.get('token')
                self.session_id = config.get('session_id')
                print(f"✅ Loaded saved device: {self.device_id}")
            except:
                pass
    
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
    
    def register_device(self, device_name, user_identity="aaron"):
        """Register this device"""
        print(f"\n📝 Registering device: {device_name}")
        
        # Create unique fingerprint
        import hashlib
        fingerprint = hashlib.md5(f"{device_name}{user_identity}".encode()).hexdigest()
        
        data = {
            "device_name": device_name,
            "device_type": "laptop",
            "user_identity": user_identity,
            "device_fingerprint": fingerprint,
            "approved_by": user_identity
        }
        
        response = requests.post(f"{BASE_URL}/api/remote/devices/register", json=data)
        result = response.json()
        
        if 'device_id' in result:
            self.device_id = result['device_id']
            print(f"✅ Device registered: {self.device_id}")
            return True
        elif result.get('error') == 'device_already_registered':
            self.device_id = result['device_id']
            print(f"✅ Device already registered: {self.device_id}")
            return True
        else:
            print(f"❌ Registration failed: {result}")
            return False
    
    def allowlist_device(self, approved_by="aaron"):
        """Allowlist this device"""
        print(f"\n🔓 Allowlisting device...")
        
        data = {
            "device_id": self.device_id,
            "approved_by": approved_by
        }
        
        response = requests.post(f"{BASE_URL}/api/remote/devices/allowlist", json=data)
        result = response.json()
        
        if 'allowlisted' in result:
            print(f"✅ Device allowlisted")
            return True
        else:
            print(f"⚠️  {result}")
            return True  # May already be allowlisted
    
    def assign_role(self, role="developer", approved_by="aaron"):
        """Assign RBAC role"""
        print(f"\n🎭 Assigning role: {role}")
        
        data = {
            "device_id": self.device_id,
            "role_name": role,
            "approved_by": approved_by
        }
        
        response = requests.post(f"{BASE_URL}/api/remote/roles/assign", json=data)
        result = response.json()
        
        if 'role' in result:
            print(f"✅ Role assigned: {result['role']}")
            print(f"   Permissions: {', '.join(result['permissions'][:8])}")
            return True
        else:
            print(f"⚠️  {result}")
            return True  # May already have role
    
    def create_session(self):
        """Create remote session"""
        print(f"\n🔐 Creating session with MFA...")
        
        data = {
            "device_id": self.device_id,
            "mfa_token": "TEST_123456"  # Dev MFA token
        }
        
        response = requests.post(f"{BASE_URL}/api/remote/session/create", json=data)
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
    
    def execute_command(self, command):
        """Execute remote command"""
        if not self.token:
            print("❌ No active session. Run 'setup' first.")
            return None
        
        data = {
            "token": self.token,
            "command": command,
            "timeout": 30
        }
        
        response = requests.post(f"{BASE_URL}/api/remote/execute", json=data)
        result = response.json()
        
        if result.get('success'):
            return result
        else:
            print(f"❌ Command failed: {result.get('error', 'unknown error')}")
            return None
    
    def setup(self, device_name="my_computer"):
        """Complete setup process"""
        if not self.check_backend():
            print("\n❌ Backend not running!")
            print("Start it with: python serve.py")
            return False
        
        print("\n" + "="*60)
        print("REMOTE ACCESS SETUP")
        print("="*60)
        
        if not self.register_device(device_name):
            return False
        
        if not self.allowlist_device():
            return False
        
        if not self.assign_role():
            return False
        
        if not self.create_session():
            return False
        
        self.save_config()
        
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE - READY FOR REMOTE ACCESS")
        print("="*60)
        print("\nYou can now:")
        print("  - Run commands: exec <command>")
        print("  - Check status: status")
        print("  - Interactive shell: shell")
        print()
        
        return True
    
    def interactive_shell(self):
        """Interactive remote shell"""
        print("\n" + "="*60)
        print("GRACE REMOTE SHELL (Type 'exit' to quit)")
        print("="*60)
        
        while True:
            try:
                command = input(f"\nremote@grace $ ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit']:
                    print("Exiting remote shell...")
                    break
                
                print(f"🔧 Executing: {command}")
                result = self.execute_command(command)
                
                if result:
                    if result.get('stdout'):
                        print(result['stdout'], end='')
                    if result.get('stderr'):
                        print("STDERR:", result['stderr'], end='')
                    print(f"\nExit code: {result.get('exit_code', 'unknown')}")
            
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def status(self):
        """Show status"""
        print("\n" + "="*60)
        print("REMOTE ACCESS STATUS")
        print("="*60)
        
        if self.device_id:
            print(f"Device ID: {self.device_id}")
        else:
            print("Device: Not registered")
        
        if self.session_id:
            print(f"Session ID: {self.session_id}")
        else:
            print("Session: None")
        
        if self.token:
            print(f"Token: {self.token[:40]}...")
        else:
            print("Token: None")
        
        # Get active sessions
        try:
            response = requests.get(f"{BASE_URL}/api/remote/sessions/active")
            result = response.json()
            print(f"\nActive Sessions: {result.get('count', 0)}")
        except:
            print("\nBackend not responding")
        
        print("="*60)


def main():
    client = RemoteAccessClient()
    
    if len(sys.argv) < 2:
        print("\nGRACE REMOTE ACCESS CLIENT")
        print("\nUsage:")
        print("  python remote_access_client.py setup [device_name]  - Setup device")
        print("  python remote_access_client.py shell                - Interactive shell")
        print("  python remote_access_client.py exec <command>       - Execute command")
        print("  python remote_access_client.py status               - Show status")
        print()
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        device_name = sys.argv[2] if len(sys.argv) > 2 else "my_computer"
        client.setup(device_name)
    
    elif command == "shell":
        client.interactive_shell()
    
    elif command == "exec":
        if len(sys.argv) < 3:
            print("Usage: python remote_access_client.py exec <command>")
            return
        
        cmd = " ".join(sys.argv[2:])
        print(f"\n🔧 Executing: {cmd}")
        result = client.execute_command(cmd)
        
        if result:
            if result.get('stdout'):
                print(result['stdout'])
            if result.get('stderr'):
                print("STDERR:", result['stderr'])
            print(f"Exit code: {result.get('exit_code')}")
    
    elif command == "status":
        client.status()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
