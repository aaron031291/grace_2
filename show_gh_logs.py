# -*- coding: utf-8 -*-
import subprocess
import sys
import json

def run_gh_command(cmd):
    """Run a GitHub CLI command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    print("🔍 Fetching GitHub Actions logs...")
    print("=" * 60)
    
    # Check if gh CLI is available
    code, stdout, stderr = run_gh_command("gh --version")
    if code != 0:
        print("❌ GitHub CLI not found. Install with:")
        print("   winget install GitHub.cli")
        return
    
    # Get latest runs with JSON output for reliable parsing
    print("📋 Latest workflow runs:")
    code, stdout, stderr = run_gh_command("gh run list --limit 10 --json databaseId,name,status,conclusion,createdAt,headBranch")
    
    if code != 0:
        print(f"❌ Failed to get runs: {stderr}")
        return
    
    try:
        runs = json.loads(stdout)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON response: {stdout}")
        return
    
    if not runs:
        print("⚠️ No workflow runs found")
        return
    
    # Display runs in a nice format
    for i, run in enumerate(runs, 1):
        status_icon = "✅" if run["conclusion"] == "success" else "❌" if run["conclusion"] == "failure" else "⏳"
        print(f"{status_icon} [{i}] {run['name']} - {run['status']} ({run['conclusion'] or 'running'})")
        print(f"    Branch: {run['headBranch']} | Created: {run['createdAt'][:19]}")
    
    print("\n" + "=" * 60)
    
    # Get the most recent run
    first_run = runs[0]
    run_id = first_run["databaseId"]
    workflow_name = first_run["name"]
    status = first_run["status"]
    conclusion = first_run["conclusion"]
    
    print(f"📝 Showing logs for: {workflow_name} ({status} - {conclusion})")
    print(f"🆔 Run ID: {run_id}")
    print("=" * 60)
    
    # Get detailed logs
    code, stdout, stderr = run_gh_command(f"gh run view {run_id} --log")
    
    if code == 0:
        print(stdout)
    else:
        print(f"❌ Failed to get detailed logs: {stderr}")
        print("\n🔄 Trying summary view instead...")
        
        # Try summary view
        code, stdout, stderr = run_gh_command(f"gh run view {run_id}")
        if code == 0:
            print(stdout)
        else:
            print(f"❌ Also failed: {stderr}")

if __name__ == "__main__":
    main()
