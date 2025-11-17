"""
Domain Whitelists - Per-Domain Learning Control
Manages per-domain whitelists, provides management UI, and validates domain access
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


@dataclass
class DomainRule:
    """Domain-specific learning rules"""
    domain: str
    allowed: bool = True
    content_types: List[str] = field(default_factory=lambda: ["documentation", "tutorials", "research"])
    max_daily_requests: int = 50
    request_count_today: int = 0
    last_request_date: Optional[str] = None
    trust_score: float = 0.7  # 0-1 scale
    risk_level: str = "low"  # low, medium, high
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def can_make_request(self) -> Tuple[bool, str]:
        """Check if domain can accept another request today"""
        today = datetime.utcnow().date().isoformat()

        # Reset counter if it's a new day
        if self.last_request_date != today:
            self.request_count_today = 0
            self.last_request_date = today

        if self.request_count_today >= self.max_daily_requests:
            return False, f"Daily limit ({self.max_daily_requests}) exceeded for {self.domain}"

        return True, ""

    def record_request(self):
        """Record a request to this domain"""
        today = datetime.utcnow().date().isoformat()

        if self.last_request_date != today:
            self.request_count_today = 0
            self.last_request_date = today

        self.request_count_today += 1
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "allowed": self.allowed,
            "content_types": self.content_types,
            "max_daily_requests": self.max_daily_requests,
            "request_count_today": self.request_count_today,
            "last_request_date": self.last_request_date,
            "trust_score": self.trust_score,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class DomainWhitelistManager:
    """
    Manages domain whitelists with per-domain rules and validation
    Provides comprehensive domain access control for learning
    """

    def __init__(self, whitelist_file: str = "./config/domain_whitelist.json"):
        self.whitelist_file = Path(whitelist_file)
        self.whitelist_file.parent.mkdir(parents=True, exist_ok=True)

        self.domains: Dict[str, DomainRule] = {}
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

        # Initialize with default trusted domains
        self._initialize_default_domains()

        # Load existing whitelist
        self._load_whitelist()

        self.access_stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "approval_required": 0,
            "daily_limits_hit": 0
        }

    def _initialize_default_domains(self):
        """Initialize with default trusted domains"""
        default_domains = [
            ("github.com", True, ["documentation", "code", "tutorials"], 100, "low", False),
            ("stackoverflow.com", True, ["qa", "code", "tutorials"], 50, "low", False),
            ("docs.python.org", True, ["documentation"], 200, "low", False),
            ("realpython.com", True, ["tutorials", "documentation"], 75, "low", False),
            ("arxiv.org", True, ["research", "papers"], 30, "low", False),
            ("wikipedia.org", True, ["reference", "general"], 150, "low", False),
            ("developer.mozilla.org", True, ["documentation"], 100, "low", False),
            ("kubernetes.io", True, ["documentation"], 80, "low", False),
            ("aws.amazon.com", False, [], 0, "high", True),  # Requires approval
            ("cloud.google.com", False, [], 0, "high", True),  # Requires approval
            ("reddit.com", False, [], 0, "medium", True),  # Requires approval
        ]

        for domain, allowed, content_types, max_requests, risk_level, requires_approval in default_domains:
            rule = DomainRule(
                domain=domain,
                allowed=allowed,
                content_types=content_types,
                max_daily_requests=max_requests,
                trust_score=0.9 if risk_level == "low" else 0.6 if risk_level == "medium" else 0.3,
                risk_level=risk_level,
                requires_approval=requires_approval
            )
            self.domains[domain] = rule

    def _load_whitelist(self):
        """Load whitelist from file"""
        if self.whitelist_file.exists():
            try:
                with open(self.whitelist_file, 'r') as f:
                    data = json.load(f)

                for domain_data in data.get("domains", []):
                    rule = DomainRule(**domain_data)
                    self.domains[rule.domain] = rule

                logger.info(f"[DOMAIN-WHITELIST] Loaded {len(self.domains)} domain rules")

            except Exception as e:
                logger.error(f"[DOMAIN-WHITELIST] Failed to load whitelist: {e}")

    def _save_whitelist(self):
        """Save whitelist to file"""
        try:
            data = {
                "domains": [rule.to_dict() for rule in self.domains.values()],
                "last_updated": datetime.utcnow().isoformat()
            }

            with open(self.whitelist_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"[DOMAIN-WHITELIST] Failed to save whitelist: {e}")

    def check_domain_access(self, url: str, content_type: str = "general") -> Dict[str, Any]:
        """
        Check if domain access is allowed

        Args:
            url: URL to check
            content_type: Type of content being requested

        Returns:
            Access decision with details
        """
        self.access_stats["total_requests"] += 1

        result = {
            "allowed": False,
            "reason": "",
            "domain": "",
            "requires_approval": False,
            "approval_request_id": None,
            "trust_score": 0.0,
            "risk_level": "unknown"
        }

        try:
            domain = self._extract_domain(url)
            result["domain"] = domain

        except ValueError as e:
            result["reason"] = str(e)
            self.access_stats["blocked_requests"] += 1
            return result

        rule = self.domains.get(domain)

        if not rule:
            # Unknown domain - requires approval
            result["requires_approval"] = True
            result["reason"] = f"Domain {domain} not in whitelist"
            self.access_stats["approval_required"] += 1

            # Auto-create approval request
            request_id = self.request_domain_approval(domain, "system", f"Auto-request for unknown domain: {url}")
            result["approval_request_id"] = request_id
            return result

        result["trust_score"] = rule.trust_score
        result["risk_level"] = rule.risk_level

        if not rule.allowed:
            result["reason"] = f"Domain {domain} is blocked"
            self.access_stats["blocked_requests"] += 1
            return result

        if rule.requires_approval:
            result["requires_approval"] = True
            result["reason"] = f"Domain {domain} requires approval"
            self.access_stats["approval_required"] += 1
            return result

        # Check content type
        if content_type not in rule.content_types and rule.content_types:
            result["reason"] = f"Content type '{content_type}' not allowed for {domain}"
            self.access_stats["blocked_requests"] += 1
            return result

        # Check daily limit
        can_request, limit_reason = rule.can_make_request()
        if not can_request:
            result["reason"] = limit_reason
            self.access_stats["daily_limits_hit"] += 1
            return result

        # All checks passed
        result["allowed"] = True
        result["reason"] = "Access granted"
        self.access_stats["allowed_requests"] += 1

        # Record the request
        rule.record_request()
        self._save_whitelist()

        return result

    def request_domain_approval(self, domain: str, requester: str, reason: str) -> str:
        """
        Request approval for a domain

        Returns:
            Request ID
        """
        request_id = f"domain_approval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(domain + requester) % 10000}"

        self.pending_approvals[request_id] = {
            "domain": domain,
            "requester": requester,
            "reason": reason,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "risk_assessment": self._assess_domain_risk(domain)
        }

        # Log approval request
        asyncio.create_task(immutable_log.append(
            actor=requester,
            action="domain_approval_requested",
            resource=request_id,
            outcome="pending",
            payload=self.pending_approvals[request_id]
        ))

        return request_id

    def approve_domain_request(self, request_id: str, approver: str,
                             max_requests: int = 50, risk_level: str = "medium") -> bool:
        """Approve a domain approval request"""
        if request_id not in self.pending_approvals:
            return False

        request = self.pending_approvals[request_id]
        domain = request["domain"]

        # Create domain rule
        rule = DomainRule(
            domain=domain,
            allowed=True,
            max_daily_requests=max_requests,
            trust_score=0.7 if risk_level == "low" else 0.5 if risk_level == "medium" else 0.3,
            risk_level=risk_level,
            requires_approval=False,
            approved_by=approver,
            approved_at=datetime.utcnow().isoformat()
        )

        self.domains[domain] = rule
        self._save_whitelist()

        # Update request
        request["status"] = "approved"
        request["approved_by"] = approver
        request["approved_at"] = datetime.utcnow().isoformat()

        # Log approval
        asyncio.create_task(immutable_log.append(
            actor=approver,
            action="domain_approved",
            resource=request_id,
            outcome="approved",
            payload={"domain": domain, "max_requests": max_requests, "risk_level": risk_level}
        ))

        return True

    def reject_domain_request(self, request_id: str, approver: str, reason: str) -> bool:
        """Reject a domain approval request"""
        if request_id not in self.pending_approvals:
            return False

        request = self.pending_approvals[request_id]
        request["status"] = "rejected"
        request["rejected_by"] = approver
        request["rejected_at"] = datetime.utcnow().isoformat()
        request["rejection_reason"] = reason

        # Log rejection
        asyncio.create_task(immutable_log.append(
            actor=approver,
            action="domain_rejected",
            resource=request_id,
            outcome="rejected",
            payload={"domain": request["domain"], "reason": reason}
        ))

        return True

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        # Remove protocol
        domain_part = url.replace('http://', '').replace('https://', '')

        # Extract domain (handle subdomains)
        domain = domain_part.split('/')[0].split(':')[0]  # Remove port if present

        # Basic validation
        if '.' not in domain or len(domain) < 4:
            raise ValueError("Invalid domain format")

        return domain.lower()

    def _assess_domain_risk(self, domain: str) -> Dict[str, Any]:
        """Assess risk level of a domain"""
        # Simple risk assessment - can be enhanced
        risk_indicators = {
            "high_risk": ["gambling", "dating", "pharma", "crypto-trading"],
            "medium_risk": ["news", "social", "shopping", "entertainment"],
            "low_risk": ["edu", "gov", "org", "docs", "github", "stackoverflow"]
        }

        assessment = {
            "risk_level": "medium",
            "confidence": 0.5,
            "indicators": []
        }

        domain_lower = domain.lower()

        for risk_level, indicators in risk_indicators.items():
            for indicator in indicators:
                if indicator in domain_lower:
                    assessment["risk_level"] = risk_level.split('_')[0]  # Remove "_risk"
                    assessment["confidence"] = 0.8
                    assessment["indicators"].append(indicator)
                    break

        return assessment

    def get_domain_stats(self) -> Dict[str, Any]:
        """Get domain whitelist statistics"""
        total_domains = len(self.domains)
        allowed = len([d for d in self.domains.values() if d.allowed])
        blocked = len([d for d in self.domains.values() if not d.allowed])
        requires_approval = len([d for d in self.domains.values() if d.requires_approval])

        return {
            "total_domains": total_domains,
            "allowed_domains": allowed,
            "blocked_domains": blocked,
            "requires_approval": requires_approval,
            "pending_approvals": len(self.pending_approvals),
            "access_stats": self.access_stats
        }

    def get_domain_rule(self, domain: str) -> Optional[DomainRule]:
        """Get domain rule by domain name"""
        return self.domains.get(domain)

    def update_domain_rule(self, domain: str, updates: Dict[str, Any]) -> bool:
        """Update domain rule"""
        if domain not in self.domains:
            return False

        rule = self.domains[domain]

        # Update allowed fields
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        rule.updated_at = datetime.utcnow().isoformat()
        self._save_whitelist()

        # Log update
        asyncio.create_task(immutable_log.append(
            actor="domain_whitelist_manager",
            action="domain_rule_updated",
            resource=domain,
            outcome="updated",
            payload=updates
        ))

        return True


class WhitelistManagementUI:
    """
    Management UI for domain whitelists
    Provides interface for managing domains, approvals, and monitoring
    """

    def __init__(self, whitelist_manager: DomainWhitelistManager):
        self.whitelist_manager = whitelist_manager

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for whitelist management"""
        stats = self.whitelist_manager.get_domain_stats()

        # Get recent approvals/rejections
        recent_approvals = []
        for request_id, request in list(self.whitelist_manager.pending_approvals.items())[-10:]:
            recent_approvals.append({
                "request_id": request_id,
                "domain": request["domain"],
                "requester": request["requester"],
                "status": request["status"],
                "requested_at": request["requested_at"]
            })

        # Get domain usage data
        domain_usage = []
        for domain, rule in self.whitelist_manager.domains.items():
            domain_usage.append({
                "domain": domain,
                "requests_today": rule.request_count_today,
                "max_requests": rule.max_daily_requests,
                "trust_score": rule.trust_score,
                "risk_level": rule.risk_level,
                "last_access": rule.last_request_date
            })

        domain_usage.sort(key=lambda x: x["requests_today"], reverse=True)

        return {
            "stats": stats,
            "recent_approvals": recent_approvals,
            "domain_usage": domain_usage[:20],  # Top 20 most active
            "risk_distribution": self._get_risk_distribution(),
            "generated_at": datetime.utcnow().isoformat()
        }

    def _get_risk_distribution(self) -> Dict[str, int]:
        """Get risk level distribution"""
        distribution = {"low": 0, "medium": 0, "high": 0, "unknown": 0}

        for rule in self.whitelist_manager.domains.values():
            risk = rule.risk_level
            if risk in distribution:
                distribution[risk] += 1
            else:
                distribution["unknown"] += 1

        return distribution

    def approve_request_ui(self, request_id: str, approver: str,
                          max_requests: int = 50, risk_level: str = "medium") -> Dict[str, Any]:
        """UI wrapper for approving domain requests"""
        success = self.whitelist_manager.approve_domain_request(
            request_id, approver, max_requests, risk_level
        )

        return {
            "success": success,
            "request_id": request_id,
            "action": "approved" if success else "failed"
        }

    def reject_request_ui(self, request_id: str, approver: str, reason: str) -> Dict[str, Any]:
        """UI wrapper for rejecting domain requests"""
        success = self.whitelist_manager.reject_domain_request(request_id, approver, reason)

        return {
            "success": success,
            "request_id": request_id,
            "action": "rejected" if success else "failed"
        }

    def add_domain_ui(self, domain: str, config: Dict[str, Any], added_by: str) -> Dict[str, Any]:
        """UI wrapper for adding new domains"""
        rule = DomainRule(
            domain=domain,
            allowed=config.get("allowed", True),
            content_types=config.get("content_types", ["documentation"]),
            max_daily_requests=config.get("max_daily_requests", 50),
            trust_score=config.get("trust_score", 0.7),
            risk_level=config.get("risk_level", "medium"),
            requires_approval=config.get("requires_approval", False),
            approved_by=added_by
        )

        self.whitelist_manager.domains[domain] = rule
        self.whitelist_manager._save_whitelist()

        # Log addition
        asyncio.create_task(immutable_log.append(
            actor=added_by,
            action="domain_added",
            resource=domain,
            outcome="added",
            payload=config
        ))

        return {
            "success": True,
            "domain": domain,
            "action": "added"
        }


# Global instances
domain_whitelist_manager = DomainWhitelistManager()
whitelist_management_ui = WhitelistManagementUI(domain_whitelist_manager)