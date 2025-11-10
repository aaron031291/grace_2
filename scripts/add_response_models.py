"""
Script to add response_model declarations to all API routes
Based on the audit report at reports/api_audit_report.txt
"""

import re
from pathlib import Path

# Map of endpoint patterns to their response schemas
RESPONSE_MODEL_MAP = {
    # Parliament API
    "parliament_api.py": {
        "POST /members": "ParliamentMemberResponse",
        "GET /members": "ParliamentMembersListResponse",
        "GET /members/{member_id}": "ParliamentMemberResponse",
        "POST /sessions": "ParliamentSessionResponse",
        "GET /sessions": "ParliamentSessionsListResponse",
        "GET /sessions/{session_id}": "ParliamentSessionResponse",
        "POST /sessions/{session_id}/vote": "ParliamentVoteResponse",
        "GET /sessions/{session_id}/status": "ParliamentSessionStatusResponse",
        "POST /committees": "ParliamentCommitteeResponse",
        "GET /committees": "ParliamentCommitteesListResponse",
        "GET /committees/{committee_name}": "ParliamentCommitteeResponse",
        "GET /stats": "ParliamentStatsResponse",
        "GET /stats/member/{member_id}": "ParliamentMemberStatsResponse",
    },
    # Constitutional API
    "constitutional_api.py": {
        "GET /principles": "ConstitutionalPrinciplesResponse",
        "GET /principles/{principle_id}": "ConstitutionalPrincipleResponse",
        "GET /violations": "ConstitutionalViolationsResponse",
        "GET /violations/stats": "ConstitutionalViolationStatsResponse",
        "GET /compliance/{action_id}": "ConstitutionalComplianceResponse",
        "POST /compliance/check": "ConstitutionalCheckResponse",
        "GET /compliance/report": "ConstitutionalReportResponse",
        "GET /clarifications/pending": "ConstitutionalClarificationsResponse",
        "POST /clarifications/answer": "SuccessResponse",
        "GET /clarifications/{request_id}": "ConstitutionalClarificationResponse",
        "GET /stats": "ConstitutionalStatsResponse",
        "GET /tenets": "ConstitutionalTenetsResponse",
    },
    # Causal Graph API
    "causal_graph_api.py": {
        "POST /build-graph": "CausalGraphBuildResponse",
        "GET /causes/{event_id}": "CausalCausesResponse",
        "GET /effects/{event_id}": "CausalEffectsResponse",
        "POST /path": "CausalPathResponse",
        "GET /influence": "CausalInfluenceResponse",
        "GET /cycles": "CausalCyclesResponse",
        "GET /visualize": "CausalVisualizeResponse",
        "GET /analyze/task-completion": "CausalAnalysisResponse",
        "GET /analyze/error-chains": "CausalAnalysisResponse",
        "GET /analyze/optimization": "CausalAnalysisResponse",
        "GET /analyze/feedback-loops": "CausalAnalysisResponse",
    },
    # Speech API
    "speech_api.py": {
        "POST /upload": "SpeechUploadResponse",
        "GET /{speech_id}": "SpeechMessageResponse",
        "GET /{speech_id}/file": None,  # FileResponse - no model needed
        "GET /list": "SpeechListResponse",
        "POST /{speech_id}/review": "SpeechReviewResponse",
        "DELETE /{speech_id}": "SpeechDeleteResponse",
        "POST /tts/generate": "TTSGenerateResponse",
        "GET /tts/{tts_id}/file": None,  # FileResponse - no model needed
    },
    # Concurrent API
    "concurrent_api.py": {
        "POST /tasks/submit": "ConcurrentTaskSubmitResponse",
        "POST /tasks/batch": "ConcurrentBatchResponse",
        "GET /tasks/{task_id}": "ConcurrentTaskStatusResponse",
        "GET /queue/status": "ConcurrentQueueStatusResponse",
        "GET /domains": "ConcurrentDomainsResponse",
        "GET /domains/{domain}/metrics": "ConcurrentDomainMetricsResponse",
        "GET /domains/metrics/all": "ConcurrentAllMetricsResponse",
    },
    # Grace Architect API
    "grace_architect_api.py": {
        "POST /learn": "GraceArchitectLearnResponse",
        "POST /extend": "GraceArchitectExtendResponse",
        "GET /patterns": "GraceArchitectPatternsResponse",
        "GET /extensions": "GraceArchitectExtensionsListResponse",
        "GET /extensions/{request_id}": "GraceArchitectExtensionResponse",
        "POST /deploy": "GraceArchitectDeployResponse",
        "GET /knowledge": "GraceArchitectKnowledgeResponse",
    },
    # Sandbox API
    "sandbox.py": {
        "GET /files": "SandboxFilesListResponse",
        "GET /file": "SandboxFileReadResponse",
        "POST /write": "SandboxFileWriteResponse",
        "POST /run": "SandboxRunResponse",
        "POST /reset": "SandboxResetResponse",
    },
    # Trust API
    "trust_api.py": {
        "GET /sources": "TrustedSourcesListResponse",
        "POST /sources": "TrustedSourceResponse",
        "PATCH /sources/{source_id}": "TrustSourceUpdateResponse",
        "DELETE /sources/{source_id}": "TrustSourceDeleteResponse",
        "GET /score": "TrustScoreResponse",
    },
}

def add_response_model_to_decorator(content: str, route_pattern: str, response_model: str) -> str:
    """Add response_model to @router.METHOD decorator"""
    if response_model is None:
        return content  # Skip file responses
    
    # Extract method and path from pattern
    parts = route_pattern.split(" ", 1)
    if len(parts) != 2:
        return content
    
    method, path = parts
    method = method.lower()
    
    # Create regex pattern to find the decorator
    # Handles both with and without existing parameters
    pattern = rf'(@router\.{method}\(["\']{ re.escape(path)}["\'])(.*?\))'
    
    def replacer(match):
        decorator_start = match.group(1)
        params = match.group(2)
        
        # Check if response_model already exists
        if "response_model" in params:
            return match.group(0)  # Already has response_model
        
        # Add response_model
        if params.strip() == ")":
            # No existing parameters
            return f'{decorator_start}, response_model={response_model})'
        else:
            # Has parameters - add before closing paren
            return f'{decorator_start}{params[:-1]}, response_model={response_model})'
    
    return re.sub(pattern, replacer, content, flags=re.MULTILINE)

def get_imports_for_file(filename: str) -> set:
    """Get all response model imports needed for a file"""
    models = set()
    if filename in RESPONSE_MODEL_MAP:
        for response_model in RESPONSE_MODEL_MAP[filename].values():
            if response_model and response_model != "SuccessResponse":
                models.add(response_model)
    return models

def add_imports_to_file(content: str, imports: set) -> str:
    """Add imports from schemas_extended to file"""
    if not imports:
        return content
    
    # Check if schemas_extended import already exists
    if "from ..schemas_extended import" in content:
        # Find the import line and add to it
        import_pattern = r'(from \.\.schemas_extended import \([^)]+\))'
        if re.search(import_pattern, content):
            # Multi-line import exists
            def add_to_multiline(match):
                existing = match.group(1)
                # Add new imports before closing paren
                new_imports = ",\n    ".join(sorted(imports))
                return existing[:-1] + f',\n    {new_imports}\n)'
            content = re.sub(import_pattern, add_to_multiline, content, count=1)
        else:
            # Single line import
            pattern = r'(from \.\.schemas_extended import )([^\n]+)'
            def add_to_single(match):
                prefix = match.group(1)
                existing = match.group(2).strip()
                all_imports = set(existing.split(", "))
                all_imports.update(imports)
                return f'{prefix}{", ".join(sorted(all_imports))}'
            content = re.sub(pattern, add_to_single, content, count=1)
    else:
        # Add new import after other backend imports
        import_line = f"from ..schemas_extended import (\n    {','.join(sorted(imports))}\n)\n"
        
        # Find last 'from ..' import
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from .."):
                insert_idx = i + 1
        
        if insert_idx > 0:
            lines.insert(insert_idx, import_line)
            content = "\n".join(lines)
    
    return content

def process_file(filepath: Path):
    """Process a single route file"""
    filename = filepath.name
    if filename not in RESPONSE_MODEL_MAP:
        return False
    
    print(f"Processing {filename}...")
    
    content = filepath.read_text(encoding="utf-8")
    original_content = content
    
    # Add imports
    imports_needed = get_imports_for_file(filename)
    if imports_needed:
        content = add_imports_to_file(content, imports_needed)
    
    # Add response_model to each endpoint
    for route_pattern, response_model in RESPONSE_MODEL_MAP[filename].items():
        content = add_response_model_to_decorator(content, route_pattern, response_model)
    
    # Write back if changed
    if content != original_content:
        filepath.write_text(content, encoding="utf-8")
        print(f"  [OK] Updated {filename}")
        return True
    else:
        print(f"  [-] No changes needed for {filename}")
        return False

def main():
    routes_dir = Path(__file__).parent.parent / "backend" / "routes"
    
    if not routes_dir.exists():
        print(f"Error: Routes directory not found: {routes_dir}")
        return
    
    files_updated = 0
    for filename in RESPONSE_MODEL_MAP.keys():
        filepath = routes_dir / filename
        if filepath.exists():
            if process_file(filepath):
                files_updated += 1
        else:
            print(f"Warning: File not found: {filepath}")
    
    print(f"\n[DONE] Updated {files_updated} files")

if __name__ == "__main__":
    main()
