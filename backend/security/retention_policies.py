"""
Per-Domain Retention Policies
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)

class RetentionPolicyManager:
    """Manage per-domain retention policies"""
    
    def __init__(self):
        self.policies = {}
        self.cleanup_stats = {
            "artifacts_cleaned": 0,
            "bytes_freed": 0,
            "policies_enforced": 0,
            "last_cleanup": None
        }
        self._load_policies()
    
    def _load_policies(self):
        """Load retention policies from config"""
        self.policies = {
            "knowledge": {
                "vector_embeddings": timedelta(days=365),  # 1 year
                "raw_documents": timedelta(days=180),      # 6 months
                "processed_chunks": timedelta(days=365),   # 1 year
                "search_queries": timedelta(days=90),      # 3 months
                "user_interactions": timedelta(days=30)    # 1 month
            },
            "security": {
                "audit_logs": timedelta(days=2555),        # 7 years (compliance)
                "access_logs": timedelta(days=365),        # 1 year
                "encryption_keys": timedelta(days=1095),   # 3 years
                "security_events": timedelta(days=730)     # 2 years
            },
            "operations": {
                "system_metrics": timedelta(days=90),      # 3 months
                "performance_logs": timedelta(days=30),    # 1 month
                "error_logs": timedelta(days=180),         # 6 months
                "deployment_artifacts": timedelta(days=365) # 1 year
            },
            "ml_training": {
                "training_data": timedelta(days=730),      # 2 years
                "model_artifacts": timedelta(days=365),    # 1 year
                "experiment_logs": timedelta(days=90),     # 3 months
                "evaluation_results": timedelta(days=180)  # 6 months
            },
            "governance": {
                "approval_records": timedelta(days=2555),  # 7 years
                "policy_changes": timedelta(days=1095),    # 3 years
                "compliance_reports": timedelta(days=2555), # 7 years
                "verification_logs": timedelta(days=365)   # 1 year
            }
        }
    
    def get_retention_period(self, domain: str, artifact_type: str) -> Optional[timedelta]:
        """Get retention period for domain/artifact type"""
        domain_policies = self.policies.get(domain, {})
        return domain_policies.get(artifact_type)
    
    def is_expired(self, artifact: Dict[str, Any], domain: str, artifact_type: str) -> bool:
        """Check if artifact has expired based on retention policy"""
        retention_period = self.get_retention_period(domain, artifact_type)
        if not retention_period:
            return False  # No policy = keep forever
        
        created_at = artifact.get("created_at") or artifact.get("encrypted_at")
        if not created_at:
            return False  # No timestamp = keep
        
        try:
            if isinstance(created_at, str):
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_date = created_at
            
            expiry_date = created_date + retention_period
            return datetime.utcnow() > expiry_date.replace(tzinfo=None)
            
        except Exception as e:
            logger.error(f"Error checking expiry for artifact: {e}")
            return False
    
    async def enforce_retention_policies(self, dry_run: bool = False) -> Dict[str, Any]:
        """Enforce retention policies across all domains"""
        logger.info(f"🧹 Starting retention policy enforcement (dry_run={dry_run})")
        
        cleanup_results = {
            "start_time": datetime.utcnow().isoformat(),
            "dry_run": dry_run,
            "domains_processed": 0,
            "artifacts_expired": 0,
            "artifacts_cleaned": 0,
            "bytes_freed": 0,
            "errors": []
        }
        
        # Process each domain
        for domain in self.policies.keys():
            try:
                domain_result = await self._enforce_domain_policies(domain, dry_run)
                cleanup_results["domains_processed"] += 1
                cleanup_results["artifacts_expired"] += domain_result["expired_count"]
                cleanup_results["artifacts_cleaned"] += domain_result["cleaned_count"]
                cleanup_results["bytes_freed"] += domain_result["bytes_freed"]
                
            except Exception as e:
                error_msg = f"Failed to process domain {domain}: {e}"
                logger.error(error_msg)
                cleanup_results["errors"].append(error_msg)
        
        # Update stats
        if not dry_run:
            self.cleanup_stats["artifacts_cleaned"] += cleanup_results["artifacts_cleaned"]
            self.cleanup_stats["bytes_freed"] += cleanup_results["bytes_freed"]
            self.cleanup_stats["policies_enforced"] += 1
            self.cleanup_stats["last_cleanup"] = datetime.utcnow().isoformat()
        
        # Log enforcement
        await immutable_log.append(
            actor="retention_policy_manager",
            action="policies_enforced",
            resource="all_domains",
            outcome="success" if not cleanup_results["errors"] else "partial_success",
            payload=cleanup_results
        )
        
        cleanup_results["end_time"] = datetime.utcnow().isoformat()
        logger.info(f"✅ Retention enforcement complete: {cleanup_results['artifacts_cleaned']} artifacts cleaned")
        
        return cleanup_results
    
    async def _enforce_domain_policies(self, domain: str, dry_run: bool) -> Dict[str, Any]:
        """Enforce retention policies for specific domain"""
        domain_result = {
            "domain": domain,
            "expired_count": 0,
            "cleaned_count": 0,
            "bytes_freed": 0
        }
        
        # Get domain artifacts (would query actual storage in production)
        artifacts = await self._get_domain_artifacts(domain)
        
        for artifact_type, artifact_list in artifacts.items():
            retention_period = self.get_retention_period(domain, artifact_type)
            if not retention_period:
                continue  # No policy for this type
            
            for artifact in artifact_list:
                if self.is_expired(artifact, domain, artifact_type):
                    domain_result["expired_count"] += 1
                    
                    if not dry_run:
                        # Actually delete the artifact
                        bytes_freed = await self._delete_artifact(artifact, domain, artifact_type)
                        domain_result["cleaned_count"] += 1
                        domain_result["bytes_freed"] += bytes_freed
        
        return domain_result
    
    async def _get_domain_artifacts(self, domain: str) -> Dict[str, List[Dict]]:
        """Get artifacts for domain (mock implementation)"""
        # In production, this would query the actual storage system
        # For demo, return mock data
        mock_artifacts = {
            "vector_embeddings": [
                {
                    "id": "embed_001",
                    "created_at": (datetime.utcnow() - timedelta(days=400)).isoformat(),
                    "size_bytes": 1024
                },
                {
                    "id": "embed_002", 
                    "created_at": datetime.utcnow().isoformat(),
                    "size_bytes": 2048
                }
            ],
            "search_queries": [
                {
                    "id": "query_001",
                    "created_at": (datetime.utcnow() - timedelta(days=100)).isoformat(),
                    "size_bytes": 256
                }
            ]
        }
        
        return mock_artifacts.get(domain, {})
    
    async def _delete_artifact(self, artifact: Dict, domain: str, artifact_type: str) -> int:
        """Delete expired artifact"""
        # In production, this would delete from actual storage
        size_bytes = artifact.get("size_bytes", 0)
        
        # Log deletion
        await immutable_log.append(
            actor="retention_policy_manager",
            action="artifact_deleted",
            resource=f"{domain}/{artifact_type}/{artifact.get('id', 'unknown')}",
            outcome="success",
            payload={
                "domain": domain,
                "artifact_type": artifact_type,
                "artifact_id": artifact.get("id"),
                "size_bytes": size_bytes,
                "reason": "retention_policy_expired"
            }
        )
        
        return size_bytes
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics"""
        return self.cleanup_stats.copy()
    
    async def generate_retention_report(self) -> Dict[str, Any]:
        """Generate retention policy compliance report"""
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "policies": {},
            "compliance_status": "compliant",
            "recommendations": []
        }
        
        for domain, policies in self.policies.items():
            domain_report = {
                "domain": domain,
                "artifact_types": len(policies),
                "policies": {}
            }
            
            for artifact_type, retention_period in policies.items():
                domain_report["policies"][artifact_type] = {
                    "retention_days": retention_period.days,
                    "retention_period": str(retention_period)
                }
            
            report["policies"][domain] = domain_report
        
        # Add recommendations
        if self.cleanup_stats["last_cleanup"]:
            last_cleanup = datetime.fromisoformat(self.cleanup_stats["last_cleanup"])
            days_since_cleanup = (datetime.utcnow() - last_cleanup).days
            
            if days_since_cleanup > 7:
                report["recommendations"].append(
                    f"Last cleanup was {days_since_cleanup} days ago. Consider running retention enforcement."
                )
        else:
            report["recommendations"].append("No cleanup has been run yet. Schedule retention enforcement.")
        
        return report

# Global instance
retention_policy_manager = RetentionPolicyManager()
