import yaml
from pathlib import Path

def validate_workflow(file_path):
    """Validate a GitHub Actions workflow file"""
    print(f"🔍 Validating {file_path.name}...")
    
    try:
        with open(file_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        issues = []
        
        # Check required fields
        if 'name' not in workflow:
            issues.append("Missing 'name' field")
        
        if 'on' not in workflow:
            issues.append("Missing 'on' field")
        
        if 'jobs' not in workflow:
            issues.append("Missing 'jobs' field")
        
        # Check for invalid secret syntax
        content = file_path.read_text()
        if '${{ secrets.' in content and '||' in content:
            issues.append("Invalid secret fallback syntax found")
        
        if issues:
            print(f"  ❌ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  ✅ Valid workflow")
        
        return len(issues) == 0
        
    except yaml.YAMLError as e:
        print(f"  ❌ YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🚀 GitHub Actions Workflow Validation")
    print("=" * 50)
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ No .github/workflows directory found")
        return
    
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    
    if not workflow_files:
        print("❌ No workflow files found")
        return
    
    print(f"Found {len(workflow_files)} workflow files:")
    
    valid_count = 0
    for workflow_file in workflow_files:
        if validate_workflow(workflow_file):
            valid_count += 1
    
    print(f"\n📊 Summary: {valid_count}/{len(workflow_files)} workflows are valid")
    
    if valid_count == len(workflow_files):
        print("🎉 All workflows are valid!")
    else:
        print("⚠️ Some workflows need fixes")

if __name__ == "__main__":
    main()