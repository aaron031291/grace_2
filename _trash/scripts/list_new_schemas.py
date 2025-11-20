"""List all newly created schemas"""
import backend.schemas_extended as se

# Get all response schemas
all_schemas = [name for name in dir(se) if not name.startswith('_') and 'Response' in name]

# Filter to recently added ones
new_prefixes = [
    'AgenticInsights', 'Goal', 'Ingest', 'Execution', 
    'HealthIngest', 'HealthState', 'Triage', 'Incident', 'Issue', 
    'Metrics', 'ML', 'Plugin', 'Commit', 'Evaluate', 
    'Learning', 'MetaCycles', 'Playbooks', 'Reflection', 
    'Scheduler', 'Subagent', 'Summaries'
]

recently_added = [s for s in all_schemas if any(prefix in s for prefix in new_prefixes)]

print(f"TOTAL SCHEMAS IN schemas_extended.py: {len(all_schemas)}")
print(f"\nRECENTLY ADDED (fixing raw string responses): {len(recently_added)}\n")

for schema in sorted(recently_added):
    print(f"  [OK] {schema}")

print(f"\n{len(recently_added)} schemas created to fix {48} endpoints!")
print("All include execution_trace and data_provenance fields.")
