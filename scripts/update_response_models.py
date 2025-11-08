"""
Systematically add response_model to API route files based on audit report
"""

import re
from pathlib import Path

# Complete mapping of files to their endpoint response models
FILE_CONFIGS = {
    "parliament_api.py": {
        "imports": ["ParliamentMemberResponse", "ParliamentMembersListResponse", 
                   "ParliamentSessionResponse", "ParliamentSessionsListResponse",
                   "ParliamentVoteResponse", "ParliamentSessionStatusResponse",
                   "ParliamentCommitteeResponse", "ParliamentCommitteesListResponse",
                   "ParliamentStatsResponse", "ParliamentMemberStatsResponse"],
        "endpoints": [
            (r'@router\.post\("/members"\)', "ParliamentMemberResponse"),
            (r'@router\.get\("/members"\)', "ParliamentMembersListResponse"),
            (r'@router\.get\("/members/\{member_id\}"\)', "ParliamentMemberResponse"),
            (r'@router\.post\("/sessions"\)', "ParliamentSessionResponse"),
            (r'@router\.get\("/sessions"\)', "ParliamentSessionsListResponse"),
            (r'@router\.get\("/sessions/\{session_id\}"\)', "ParliamentSessionResponse"),
            (r'@router\.post\("/sessions/\{session_id\}/vote"\)', "ParliamentVoteResponse"),
            (r'@router\.get\("/sessions/\{session_id\}/status"\)', "ParliamentSessionStatusResponse"),
            (r'@router\.post\("/committees"\)', "ParliamentCommitteeResponse"),
            (r'@router\.get\("/committees"\)', "ParliamentCommitteesListResponse"),
            (r'@router\.get\("/committees/\{committee_name\}"\)', "ParliamentCommitteeResponse"),
            (r'@router\.get\("/stats"\)', "ParliamentStatsResponse"),
            (r'@router\.get\("/stats/member/\{member_id\}"\)', "ParliamentMemberStatsResponse"),
        ]
    },
    "constitutional_api.py": {
        "imports": ["ConstitutionalPrinciplesResponse", "ConstitutionalPrincipleResponse",
                   "ConstitutionalViolationsResponse", "ConstitutionalViolationStatsResponse",
                   "ConstitutionalComplianceResponse", "ConstitutionalCheckResponse",
                   "ConstitutionalReportResponse", "ConstitutionalClarificationsResponse",
                   "ConstitutionalClarificationResponse", "ConstitutionalStatsResponse",
                   "ConstitutionalTenetsResponse", "SuccessResponse"],
        "endpoints": [
            (r'@router\.get\("/principles"\)', "ConstitutionalPrinciplesResponse"),
            (r'@router\.get\("/principles/\{principle_id\}"\)', "ConstitutionalPrincipleResponse"),
            (r'@router\.get\("/violations"\)', "ConstitutionalViolationsResponse"),
            (r'@router\.get\("/violations/stats"\)', "ConstitutionalViolationStatsResponse"),
            (r'@router\.get\("/compliance/\{action_id\}"\)', "ConstitutionalComplianceResponse"),
            (r'@router\.post\("/compliance/check"\)', "ConstitutionalCheckResponse"),
            (r'@router\.get\("/compliance/report"\)', "ConstitutionalReportResponse"),
            (r'@router\.get\("/clarifications/pending"\)', "ConstitutionalClarificationsResponse"),
            (r'@router\.post\("/clarifications/answer"\)', "SuccessResponse"),
            (r'@router\.get\("/clarifications/\{request_id\}"\)', "ConstitutionalClarificationResponse"),
            (r'@router\.get\("/stats"\)', "ConstitutionalStatsResponse"),
            (r'@router\.get\("/tenets"\)', "ConstitutionalTenetsResponse"),
        ]
    },
    "causal_graph_api.py": {
        "imports": ["CausalGraphBuildResponse", "CausalCausesResponse", "CausalEffectsResponse",
                   "CausalPathResponse", "CausalInfluenceResponse", "CausalCyclesResponse",
                   "CausalVisualizeResponse", "CausalAnalysisResponse"],
        "endpoints": [
            (r'@router\.post\("/build-graph"\)', "CausalGraphBuildResponse"),
            (r'@router\.get\("/causes/\{event_id\}"\)', "CausalCausesResponse"),
            (r'@router\.get\("/effects/\{event_id\}"\)', "CausalEffectsResponse"),
            (r'@router\.post\("/path"\)', "CausalPathResponse"),
            (r'@router\.get\("/influence"\)', "CausalInfluenceResponse"),
            (r'@router\.get\("/cycles"\)', "CausalCyclesResponse"),
            (r'@router\.get\("/visualize"\)', "CausalVisualizeResponse"),
            (r'@router\.get\("/analyze/task-completion"\)', "CausalAnalysisResponse"),
            (r'@router\.get\("/analyze/error-chains"\)', "CausalAnalysisResponse"),
            (r'@router\.get\("/analyze/optimization"\)', "CausalAnalysisResponse"),
            (r'@router\.get\("/analyze/feedback-loops"\)', "CausalAnalysisResponse"),
        ]
    },
    "speech_api.py": {
        "imports": ["SpeechUploadResponse", "SpeechMessageResponse", "SpeechListResponse",
                   "SpeechReviewResponse", "SpeechDeleteResponse", "TTSGenerateResponse"],
        "endpoints": [
            (r'@router\.post\("/upload"\)', "SpeechUploadResponse"),
            (r'@router\.get\("/\{speech_id\}"\)', "SpeechMessageResponse"),
            (r'@router\.get\("/list"\)', "SpeechListResponse"),
            (r'@router\.post\("/\{speech_id\}/review"\)', "SpeechReviewResponse"),
            (r'@router\.delete\("/\{speech_id\}"\)', "SpeechDeleteResponse"),
            (r'@router\.post\("/tts/generate"\)', "TTSGenerateResponse"),
        ]
    },
    "concurrent_api.py": {
        "imports": ["ConcurrentTaskSubmitResponse", "ConcurrentBatchResponse",
                   "ConcurrentTaskStatusResponse", "ConcurrentQueueStatusResponse",
                   "ConcurrentDomainsResponse", "ConcurrentDomainMetricsResponse",
                   "ConcurrentAllMetricsResponse"],
        "endpoints": [
            (r'@router\.post\("/tasks/submit"\)', "ConcurrentTaskSubmitResponse"),
            (r'@router\.post\("/tasks/batch"\)', "ConcurrentBatchResponse"),
            (r'@router\.get\("/tasks/\{task_id\}"\)', "ConcurrentTaskStatusResponse"),
            (r'@router\.get\("/queue/status"\)', "ConcurrentQueueStatusResponse"),
            (r'@router\.get\("/domains"\)', "ConcurrentDomainsResponse"),
            (r'@router\.get\("/domains/\{domain\}/metrics"\)', "ConcurrentDomainMetricsResponse"),
            (r'@router\.get\("/domains/metrics/all"\)', "ConcurrentAllMetricsResponse"),
        ]
    },
    "grace_architect_api.py": {
        "imports": ["GraceArchitectLearnResponse", "GraceArchitectExtendResponse",
                   "GraceArchitectPatternsResponse", "GraceArchitectExtensionsListResponse",
                   "GraceArchitectExtensionResponse", "GraceArchitectDeployResponse",
                   "GraceArchitectKnowledgeResponse"],
        "endpoints": [
            (r'@router\.post\("/learn"\)', "GraceArchitectLearnResponse"),
            (r'@router\.post\("/extend"\)', "GraceArchitectExtendResponse"),
            (r'@router\.get\("/patterns"\)', "GraceArchitectPatternsResponse"),
            (r'@router\.get\("/extensions"\)', "GraceArchitectExtensionsListResponse"),
            (r'@router\.get\("/extensions/\{request_id\}"\)', "GraceArchitectExtensionResponse"),
            (r'@router\.post\("/deploy"\)', "GraceArchitectDeployResponse"),
            (r'@router\.get\("/knowledge"\)', "GraceArchitectKnowledgeResponse"),
        ]
    },
    "sandbox.py": {
        "imports": ["SandboxFilesListResponse", "SandboxFileReadResponse",
                   "SandboxFileWriteResponse", "SandboxRunResponse", "SandboxResetResponse"],
        "endpoints": [
            (r'@router\.get\("/files"\)', "SandboxFilesListResponse"),
            (r'@router\.get\("/file"\)', "SandboxFileReadResponse"),
            (r'@router\.post\("/write"\)', "SandboxFileWriteResponse"),
            (r'@router\.post\("/run"\)', "SandboxRunResponse"),
            (r'@router\.post\("/reset"\)', "SandboxResetResponse"),
        ]
    },
    "trust_api.py": {
        "imports": ["TrustedSourcesListResponse", "TrustedSourceResponse",
                   "TrustSourceUpdateResponse", "TrustSourceDeleteResponse", "TrustScoreResponse"],
        "endpoints": [
            (r'@router\.get\("/sources"\)', "TrustedSourcesListResponse"),
            (r'@router\.post\("/sources"\)', "TrustedSourceResponse"),
            (r'@router\.patch\("/sources/\{source_id\}"\)', "TrustSourceUpdateResponse"),
            (r'@router\.delete\("/sources/\{source_id\}"\)', "TrustSourceDeleteResponse"),
            (r'@router\.get\("/score"\)', "TrustScoreResponse"),
        ]
    },
}

def process_file(filepath: Path, config: dict):
    """Process a single file with given configuration"""
    print(f"Processing {filepath.name}...")
    
    content = filepath.read_text(encoding="utf-8")
    original_content = content
    
    # Add imports
    if "from ..schemas_extended import" not in content:
        imports_str = ",\n    ".join(config["imports"])
        import_statement = f"from ..schemas_extended import (\n    {imports_str}\n)\n"
        
        # Find position after last 'from ..' import
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("from .."):
                insert_idx = i + 1
        
        if insert_idx > 0:
            lines.insert(insert_idx, import_statement)
            content = "\n".join(lines)
    
    # Add response_model to decorators
    for pattern, response_model in config["endpoints"]:
        # Find decorator and add response_model if not present
        def add_model(match):
            full_match = match.group(0)
            if "response_model" in full_match:
                return full_match  # Already has response_model
            # Add response_model parameter
            return full_match[:-1] + f", response_model={response_model})"
        
        content = re.sub(pattern, add_model, content)
    
    # Write back if changed
    if content != original_content:
        filepath.write_text(content, encoding="utf-8")
        print(f"  [OK] Updated {filepath.name}")
        return True
    else:
        print(f"  [-] No changes needed")
        return False

def main():
    routes_dir = Path(__file__).parent.parent / "backend" / "routes"
    
    if not routes_dir.exists():
        print(f"Error: Routes directory not found: {routes_dir}")
        return
    
    files_updated = 0
    total_endpoints = 0
    
    for filename, config in FILE_CONFIGS.items():
        filepath = routes_dir / filename
        if filepath.exists():
            if process_file(filepath, config):
                files_updated += 1
                total_endpoints += len(config["endpoints"])
        else:
            print(f"Warning: File not found: {filepath}")
    
    print(f"\n[DONE] Updated {files_updated} files with {total_endpoints} response_model declarations")

if __name__ == "__main__":
    main()
