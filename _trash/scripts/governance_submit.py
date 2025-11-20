#!/usr/bin/env python3
"""
Governance Submission
Submit integration for Unified Logic approval
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from backend.models import async_session
from backend.memory_verification_matrix import MemoryVerificationMatrix


async def submit_for_approval(integration_name: str, artifact_path: str, risk: str, kpi_requirements: str):
    """Submit integration for governance approval"""
    
    print("=" * 70)
    print("GOVERNANCE SUBMISSION")
    print("=" * 70)
    
    async with async_session() as session:
        matrix = MemoryVerificationMatrix(session)
        
        # Load integration
        integrations = matrix.get_all_integrations()
        integration = next((i for i in integrations if i['name'] == integration_name), None)
        
        if not integration:
            print(f"\n[ERROR] Integration '{integration_name}' not found")
            return
        
        print(f"\n[INTEGRATION] {integration['name']}")
        print(f"  URL: {integration['url']}")
        print(f"  Auth: {integration['auth_type']}")
        print(f"  Current Status: {integration['status']}")
        print(f"  Risk Level: {integration['risk_level']}")
        print(f"  Hunter Scan: {integration['hunter_scan_status']}")
        
        # Load artifact
        artifact_file = Path(artifact_path)
        if artifact_file.exists():
            with open(artifact_file, 'r', encoding='utf-8') as f:
                artifact_data = json.load(f)
            print(f"\n[ARTIFACT] Loaded: {artifact_file.name}")
        else:
            artifact_data = {}
            print(f"\n[WARNING] Artifact not found: {artifact_path}")
        
        # Parse KPI requirements
        kpi_dict = {}
        if kpi_requirements:
            for req in kpi_requirements.split(','):
                key, value = req.split('<')
                kpi_dict[key.strip()] = value.strip()
        
        # Create submission package
        submission = {
            'integration_name': integration_name,
            'submitted_at': datetime.utcnow().isoformat(),
            'submitted_by': 'grace_system',
            'risk_assessment': risk,
            'kpi_requirements': kpi_dict,
            'hunter_scan_status': integration['hunter_scan_status'],
            'artifact_reference': str(artifact_file),
            'status': 'pending_unified_logic_review',
            'reverse_funnel_stage': 'approval_queue'
        }
        
        # Save submission
        submission_dir = Path(__file__).parent.parent / 'reports' / 'governance_submissions'
        submission_dir.mkdir(parents=True, exist_ok=True)
        
        submission_file = submission_dir / f"{integration_name.replace(' ', '_')}_submission.json"
        with open(submission_file, 'w', encoding='utf-8') as f:
            json.dump(submission, f, indent=2)
        
        print(f"\n[SUBMITTED] Governance package created")
        print(f"  File: {submission_file}")
        print(f"  Status: {submission['status']}")
        
        # Auto-approve if low risk and Hunter passed
        if (integration['risk_level'] == 'low' and 
            integration['hunter_scan_status'] == 'passed'):
            
            print(f"\n[AUTO-APPROVAL] Low risk + Hunter passed = Auto-approved")
            
            matrix.approve_integration(
                integration_name,
                approved_by='unified_logic_auto',
                notes='Auto-approved: low risk, passed Hunter scan'
            )
            
            print(f"\n[STATUS] Integration approved for staging deployment")
            print(f"\n[NEXT STEP] Deploy to staging:")
            print(f"  python scripts/deploy_integration.py --integration \"{integration_name}\" --env staging")
        
        else:
            print(f"\n[QUEUED] Awaiting Unified Logic manual review")
            print(f"  Risk Level: {integration['risk_level']}")
            print(f"  Approval Required: Yes")
            print(f"\n[REVIEW] Check pending approvals:")
            print(f"  python scripts/review_pending_apis.py")


async def main():
    """Main submission handler"""
    
    parser = argparse.ArgumentParser(description='Submit integration for governance approval')
    parser.add_argument('--integration', required=True, help='Integration name')
    parser.add_argument('--artifact', default='grace_training/api_discovery/ml_apis_discovered.json', help='Artifact path')
    parser.add_argument('--risk', default='medium', choices=['low', 'medium', 'high', 'critical'], help='Risk level')
    parser.add_argument('--kpi', default='latency<400ms,error_rate<1%', help='KPI requirements')
    args = parser.parse_args()
    
    await submit_for_approval(args.integration, args.artifact, args.risk, args.kpi)


if __name__ == '__main__':
    asyncio.run(main())
