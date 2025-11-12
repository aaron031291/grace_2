import yaml
from pathlib import Path

def validate_workflow(file_path):
    """Validate a GitHub Actions workflow file"""
    print(f"🔍 Validating {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse YAML
        workflow = yaml.safe_load(content)
        
        if workflow is None:
            print(f"  ❌ Failed to parse YAML")
            return False
        
        issues = []
        
        # Check required fields - use correct key names
        if 'name' not in workflow:
            issues.append("Missing 'name' field")
        
        # GitHub Actions uses 'on' (not 'trigger')
        if 'on' not in workflow:
            issues.append("Missing 'on' field")
        
        if 'jobs' not in workflow:
            issues.append("Missing 'jobs' field")
        
        # Check for problematic secret syntax patterns
        if '${{ secrets.' in content and ' || ' in content:
            # Look for patterns like: ${{ secrets.KEY || 'fallback' }}
            import re
            if re.search(r'\$\{\{\s*secrets\.[^}]+\s*\|\|\s*[^}]+\}\}', content):
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
        print(f"  ❌ Error reading file: {e}")
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
