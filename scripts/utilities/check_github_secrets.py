import subprocess
import sys

def run_gh_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    print("🔐 Checking GitHub repository secrets...")
    print("=" * 50)
    
    # Check if gh CLI is available
    code, stdout, stderr = run_gh_command("gh --version")
    if code != 0:
        print("❌ GitHub CLI not found. Install with:")
        print("   winget install GitHub.cli")
        return
    
    # List repository secrets
    code, stdout, stderr = run_gh_command("gh secret list")