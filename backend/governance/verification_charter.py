"""
Verification Charter - Governance for External Integrations

Policy-based approval system for:
- API installations (Stripe, Shopify, OpenAI, etc.)
- Blockchain connections (Ethereum, Solana, etc.)
- ML/AI platforms (Hugging Face, Replicate, etc.)
- Cloud infrastructure (AWS, Azure, GCP)

All require verification + approval before activation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_PATH = "databases/grace.db"


class RiskLevel(Enum):
    """Integration risk levels"""
    LOW = "low"              # Read-only, public data
    MEDIUM = "medium"        # Limited scope, reversible
    HIGH = "high"            # Write access, financial
    CRITICAL = "critical"    # Infrastructure, crypto


class ApprovalStatus(Enum):
    """Approval workflow states"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"
    LIVE = "live"


@dataclass
class IntegrationRequest:
    """Request to install an external integration"""
    request_id: str
    integration_name: str
    vendor: str
    purpose: str
    api_endpoint: str
    auth_method: str
    scopes_requested: List[str]
    risk_level: RiskLevel
    requested_by: str
    requested_at: datetime
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    notes: str = ""


class VerificationCharter:
    """
    Governance module for external integrations
    
    Maintains:
    - Whitelist of approved integrations
    - Risk assessment policies
    - Approval workflows
    - Audit trails
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_tables()
        self._load_policies()
    
    def _initialize_tables(self):
        """Create governance tables"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verification Matrix
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_verification_matrix (
                integration_id TEXT PRIMARY KEY,
                integration_name TEXT NOT NULL,
                vendor TEXT NOT NULL,
                api_endpoint TEXT,
                auth_method TEXT,
                risk_level TEXT NOT NULL,
                approval_status TEXT NOT NULL,
                scopes TEXT,
                approved_by TEXT,
                approved_at DATETIME,
                last_audit DATETIME,
                last_health_check DATETIME,
                health_status TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Integration Requests (approval queue)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_integration_requests (
                request_id TEXT PRIMARY KEY,
                integration_name TEXT NOT NULL,
                vendor TEXT NOT NULL,
                purpose TEXT,
                api_endpoint TEXT,
                auth_method TEXT,
                scopes TEXT,
                risk_level TEXT NOT NULL,
                requested_by TEXT,
                requested_at DATETIME,
                approval_status TEXT NOT NULL,
                approved_by TEXT,
                approved_at DATETIME,
                rejection_reason TEXT,
                hunter_scan_results TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Hunter Scan Results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_hunter_scans (
                scan_id TEXT PRIMARY KEY,
                integration_id TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                scan_timestamp DATETIME NOT NULL,
                passed BOOLEAN NOT NULL,
                findings TEXT,
                risk_score REAL,
                recommendations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_policies(self):
        """Load pre-approved integration policies"""
        
        # Pre-approved low-risk integrations
        self.auto_approve_list = {
            "public_apis": ["coinmarketcap", "github_public", "wikipedia"],
            "read_only": ["google_analytics_read", "hubspot_read"]
        }
        
        # Blocked/high-risk patterns
        self.block_patterns = [
            "admin", "root", "delete_all", "drop_table",
            "full_access", "wildcard_permissions"
        ]
    
    async def request_integration(
        self,
        integration_name: str,
        vendor: str,
        purpose: str,
        api_endpoint: str,
        auth_method: str,
        scopes: List[str],
        risk_level: RiskLevel,
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Request approval for new integration
        
        Returns:
            Request result with approval status
        """
        
        # Generate request ID
        request_id = hashlib.sha256(
            f"{integration_name}_{vendor}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Check block patterns
        for scope in scopes:
            for pattern in self.block_patterns:
                if pattern in scope.lower():
                    logger.warning(f"[CHARTER] Blocked pattern detected: {pattern} in {scope}")
                    return {
                        "success": False,
                        "status": "rejected",
                        "reason": f"Blocked pattern: {pattern}",
                        "request_id": request_id
                    }
        
        # Store request
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            INSERT INTO memory_integration_requests
            (request_id, integration_name, vendor, purpose, api_endpoint,
             auth_method, scopes, risk_level, requested_by, requested_at,
             approval_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id,
            integration_name,
            vendor,
            purpose,
            api_endpoint,
            auth_method,
            json.dumps(scopes),
            risk_level.value,
            requested_by,
            datetime.now().isoformat(),
            ApprovalStatus.PENDING.value
        ))
        
        conn.commit()
        conn.close()
        
        # Auto-approve low-risk
        if risk_level == RiskLevel.LOW and integration_name in self.auto_approve_list.get("public_apis", []):
            await self.approve_integration(request_id, "auto_approval_policy")
            return {
                "success": True,
                "status": "auto_approved",
                "request_id": request_id,
                "message": "Low-risk integration auto-approved"
            }
        
        # Queue for Unified Logic approval
        logger.info(f"[CHARTER] Integration request queued: {integration_name} ({risk_level.value})")
        
        return {
            "success": True,
            "status": "pending_approval",
            "request_id": request_id,
            "risk_level": risk_level.value,
            "message": f"Request submitted to Unified Logic for {risk_level.value} risk approval"
        }
    
    async def approve_integration(
        self,
        request_id: str,
        approved_by: str,
        notes: str = ""
    ) -> bool:
        """Approve integration request"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Update request
        conn.execute("""
            UPDATE memory_integration_requests
            SET approval_status = ?,
                approved_by = ?,
                approved_at = ?,
                notes = ?
            WHERE request_id = ?
        """, (
            ApprovalStatus.APPROVED.value,
            approved_by,
            datetime.now().isoformat(),
            notes,
            request_id
        ))
        
        # Get request details
        cursor = conn.execute("""
            SELECT integration_name, vendor, api_endpoint, auth_method, scopes, risk_level
            FROM memory_integration_requests
            WHERE request_id = ?
        """, (request_id,))
        
        result = cursor.fetchone()
        
        if result:
            # Add to verification matrix (approved integrations)
            integration_id = hashlib.md5(f"{result[0]}_{result[1]}".encode()).hexdigest()[:16]
            
            conn.execute("""
                INSERT OR REPLACE INTO memory_verification_matrix
                (integration_id, integration_name, vendor, api_endpoint,
                 auth_method, risk_level, approval_status, scopes, 
                 approved_by, approved_at, last_audit, health_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                integration_id,
                result[0],
                result[1],
                result[2],
                result[3],
                result[5],
                ApprovalStatus.APPROVED.value,
                result[4],
                approved_by,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "pending_activation"
            ))
            
            logger.info(f"[CHARTER] Integration approved: {result[0]} by {approved_by}")
        
        conn.commit()
        conn.close()
        
        return True
    
    async def reject_integration(
        self,
        request_id: str,
        rejected_by: str,
        reason: str
    ) -> bool:
        """Reject integration request"""
        
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            UPDATE memory_integration_requests
            SET approval_status = ?,
                approved_by = ?,
                approved_at = ?,
                rejection_reason = ?
            WHERE request_id = ?
        """, (
            ApprovalStatus.REJECTED.value,
            rejected_by,
            datetime.now().isoformat(),
            reason,
            request_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.warning(f"[CHARTER] Integration rejected: {request_id} - {reason}")
        return True
    
    def get_approved_integrations(self) -> List[Dict]:
        """Get all approved integrations"""
        
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT integration_id, integration_name, vendor, api_endpoint,
                   risk_level, approval_status, health_status, last_health_check
            FROM memory_verification_matrix
            WHERE approval_status IN ('approved', 'live')
            ORDER BY risk_level DESC, integration_name
        """)
        
        integrations = []
        for row in cursor.fetchall():
            integrations.append({
                'integration_id': row[0],
                'name': row[1],
                'vendor': row[2],
                'endpoint': row[3],
                'risk_level': row[4],
                'status': row[5],
                'health': row[6],
                'last_check': row[7]
            })
        
        conn.close()
        return integrations
    
    def get_pending_requests(self) -> List[Dict]:
        """Get pending approval requests"""
        
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT request_id, integration_name, vendor, purpose, risk_level,
                   requested_by, requested_at
            FROM memory_integration_requests
            WHERE approval_status = 'pending'
            ORDER BY requested_at DESC
        """)
        
        requests = []
        for row in cursor.fetchall():
            requests.append({
                'request_id': row[0],
                'name': row[1],
                'vendor': row[2],
                'purpose': row[3],
                'risk_level': row[4],
                'requested_by': row[5],
                'requested_at': row[6]
            })
        
        conn.close()
        return requests


# Singleton
_charter = None

def get_verification_charter() -> VerificationCharter:
    global _charter
    if _charter is None:
        _charter = VerificationCharter()
    return _charter
