import yaml
from pathlib import Path

def debug_workflow(file_path):
    """Debug a workflow file to see its actual structure"""
    print(f"\n🔍 Debugging {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"  📄 File size: {len(content)} chars")
        print(f"  📝 First 200 chars: {repr(content[:200])}")
        
        # Try to parse YAML
        try:
            workflow = yaml.safe_load(content)
            if workflow:
                print(f"  🔑 Top-level keys: {list(workflow.keys())}")
                if 'on' in workflow:
                    print(f"  ✅ 'on' field found: {workflow['on']}")
                else:
                    print(f"  ❌ 'on' field missing")
            else:
                print(f"  ❌ YAML parsed as None/empty")
        except yaml.YAMLError as e:
            print(f"  ❌ YAML error: {e}")
            
    except Exception as e:
        print(f"  ❌ File error: {e}")

def main():
    print("🔧 GitHub Actions Workflow Debug")
    print("=" * 50)
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ No .github/workflows directory found")
        return
    
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    
    for workflow_file in workflow_files:
        debug_workflow(workflow_file)

if __name__ == "__main__":
    main()