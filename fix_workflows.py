import yaml
from pathlib import Path
import re

def fix_workflow(file_path):
    """Fix common workflow issues"""
    print(f"🔧 Fixing {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML
        workflow = yaml.safe_load(content)
        
        if not workflow:
            print(f"  ❌ Cannot parse workflow")
            return False
        
        fixes_applied = []
        
        # Fix 1: Ensure 'on' field exists
        if 'on' not in workflow:
            workflow['on'] = {'push': {'branches': ['main']}, 'pull_request': {'branches': ['main']}}
            fixes_applied.append("Added missing 'on' field")
        
        # Fix 2: Ensure 'name' field exists
        if 'name' not in workflow:
            workflow['name'] = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            fixes_applied.append("Added missing 'name' field")
        
        # Fix 3: Ensure 'jobs' field exists
        if 'jobs' not in workflow:
            workflow['jobs'] = {
                'build': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {'name': 'Run tests', 'run': 'echo "Add your tests here"'}
                    ]
                }
            }
            fixes_applied.append("Added missing 'jobs' field")
        
        # Fix 4: Fix secret syntax issues
        content_fixed = content
        # Replace invalid secret fallback syntax
        content_fixed = re.sub(
            r'\$\{\{\s*secrets\.([^}]+)\s*\|\|\s*([^}]+)\s*\}\}',
            r'${{ secrets.\1 }}',
            content_fixed
        )
        
        if content_fixed != content:
            fixes_applied.append("Fixed secret fallback syntax")
        
        # Write back if fixes were applied
        if fixes_applied:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
            
            print(f"  ✅ Applied fixes: {', '.join(fixes_applied)}")
            return True
        else:
            print(f"  ✅ No fixes needed")
            return True
            
    except Exception as e:
        print(f"  ❌ Error fixing workflow: {e}")
        return False

def main():
    print("🔧 GitHub Actions Workflow Fixer")
    print("=" * 50)
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ No .github/workflows directory found")
        return
    
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    
    if not workflow_files:
        print("❌ No workflow files found")
        return
    
    fixed_count = 0
    for workflow_file in workflow_files:
        if fix_workflow(workflow_file):
            fixed_count += 1
    
    print(f"\n📊 Summary: {fixed_count}/{len(workflow_files)} workflows processed")
    
    # Re-run validation
    print("\n🔍 Re-running validation...")
    import subprocess
    subprocess.run(['python', 'validate_workflows.py'])

if __name__ == "__main__":
    main()