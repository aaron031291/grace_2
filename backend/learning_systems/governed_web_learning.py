"""
Governed Web Learning - Whitelist-Based Autonomous Learning
Implements whitelist-based web search, approval gates, sandbox testing, and learning job orchestration
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class LearningPermission(Enum):
    """Permission levels for web learning"""
    ALLOWED = "allowed"
    REQUIRES_APPROVAL = "requires_approval"
    BLOCKED = "blocked"


@dataclass
class DomainWhitelistEntry:
    """Domain whitelist entry with permissions and rules"""
    domain: str
    permission: LearningPermission
    allowed_paths: List[str] = field(default_factory=list)
    blocked_paths: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)  # docs, tutorials, research, etc.
    trust_score: float = 0.5  # 0-1 scale
    added_by: str = "system"
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_accessed: Optional[str] = None
    access_count: int = 0

    def allows_access(self, url: str) -> bool:
        """Check if URL is allowed under this whitelist entry"""
        if self.permission == LearningPermission.BLOCKED:
            return False

        # Check path restrictions
        path = url.replace(f"https://{self.domain}", "").replace(f"http://{self.domain}", "")

        # Check blocked paths
        for blocked in self.blocked_paths:
            if blocked in path:
                return False

        # If allowed paths specified, must match one
        if self.allowed_paths:
            return any(allowed in path for allowed in self.allowed_paths)

        return True


class DomainWhitelist:
    """
    Manages domain whitelists for governed web learning
    Controls which domains Grace can learn from autonomously
    """

    def __init__(self):
        self.whitelist: Dict[str, DomainWhitelistEntry] = {}
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

        # Initialize with trusted domains
        self._initialize_trusted_domains()

    def _initialize_trusted_domains(self):
        """Initialize with pre-approved trusted domains"""
        trusted_domains = [
            ("github.com", LearningPermission.ALLOWED, ["docs", "readme"], [], ["documentation", "code"]),
            ("stackoverflow.com", LearningPermission.ALLOWED, [], ["/questions/tagged/"], ["qa", "code"]),
            ("docs.python.org", LearningPermission.ALLOWED, [], [], ["documentation"]),
            ("realpython.com", LearningPermission.ALLOWED, [], [], ["tutorials", "documentation"]),
            ("arxiv.org", LearningPermission.ALLOWED, ["abs", "pdf"], [], ["research", "papers"]),
            ("wikipedia.org", LearningPermission.ALLOWED, [], [], ["reference", "general"]),
            ("developer.mozilla.org", LearningPermission.ALLOWED, [], [], ["documentation"]),
            ("kubernetes.io", LearningPermission.ALLOWED, ["docs"], [], ["documentation"]),
            ("aws.amazon.com", LearningPermission.REQUIRES_APPROVAL, [], [], ["documentation"]),
            ("cloud.google.com", LearningPermission.REQUIRES_APPROVAL, [], [], ["documentation"])
        ]

        for domain, permission, allowed_paths, blocked_paths, content_types in trusted_domains:
            entry = DomainWhitelistEntry(
                domain=domain,
                permission=permission,
                allowed_paths=allowed_paths,
                blocked_paths=blocked_paths,
                content_types=content_types,
                trust_score=0.9 if permission == LearningPermission.ALLOWED else 0.6,
                added_by="system_initialization"
            )
            self.whitelist[domain] = entry

    def check_domain_access(self, url: str) -> Tuple[bool, Optional[str], Optional[DomainWhitelistEntry]]:
        """
        Check if domain access is allowed

        Returns:
            (allowed, reason, whitelist_entry)
        """
        try:
            domain = self._extract_domain(url)
        except ValueError:
            return False, "Invalid URL format", None

        entry = self.whitelist.get(domain)

        if not entry:
            return False, f"Domain {domain} not in whitelist", None

        if entry.permission == LearningPermission.BLOCKED:
            return False, f"Domain {domain} is blocked", entry

        if entry.permission == LearningPermission.REQUIRES_APPROVAL:
            return False, f"Domain {domain} requires approval", entry

        # Check path restrictions
        if not entry.allows_access(url):
            return False, f"URL path not allowed for domain {domain}", entry

        # Update access stats
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow().isoformat()

        return True, None, entry

    def request_domain_approval(self, domain: str, requester: str, reason: str) -> str:
        """
        Request approval for a new domain

        Returns:
            Request ID
        """
        request_id = f"domain_req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(domain) % 10000}"

        self.pending_approvals[request_id] = {
            "domain": domain,
            "requester": requester,
            "reason": reason,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }

        # Log governance event
        asyncio.create_task(immutable_log.append(
            actor=requester,
            action="domain_approval_requested",
            resource=request_id,
            outcome="pending",
            payload=self.pending_approvals[request_id]
        ))

        return request_id

    def approve_domain(self, request_id: str, approver: str) -> bool:
        """Approve a domain request"""
        if request_id not in self.pending_approvals:
            return False

        request = self.pending_approvals[request_id]
        domain = request["domain"]

        # Add to whitelist
        entry = DomainWhitelistEntry(
            domain=domain,
            permission=LearningPermission.ALLOWED,
            trust_score=0.7,  # Start with moderate trust
            added_by=approver
        )
        self.whitelist[domain] = entry

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
            payload={"domain": domain, "request_id": request_id}
        ))

        return True

    def reject_domain(self, request_id: str, approver: str, reason: str) -> bool:
        """Reject a domain request"""
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

    def get_whitelist_stats(self) -> Dict[str, Any]:
        """Get whitelist statistics"""
        total_domains = len(self.whitelist)
        allowed = len([d for d in self.whitelist.values() if d.permission == LearningPermission.ALLOWED])
        requires_approval = len([d for d in self.whitelist.values() if d.permission == LearningPermission.REQUIRES_APPROVAL])
        blocked = len([d for d in self.whitelist.values() if d.permission == LearningPermission.BLOCKED])

        return {
            "total_domains": total_domains,
            "allowed": allowed,
            "requires_approval": requires_approval,
            "blocked": blocked,
            "pending_approvals": len(self.pending_approvals)
        }


@dataclass
class LearningJob:
    """Learning job for web content acquisition"""
    job_id: str
    query: str
    domain_whitelist: List[str]
    status: str = "pending"  # pending, running, completed, failed
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    approval_required: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "query": self.query,
            "domain_whitelist": self.domain_whitelist,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "results_count": len(self.results),
            "error_message": self.error_message,
            "approval_required": self.approval_required,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at
        }


class LearningJobOrchestrator:
    """
    Orchestrates learning jobs with approval gates and sandbox testing
    Manages the lifecycle of web learning tasks
    """

    def __init__(self):
        self.jobs: Dict[str, LearningJob] = {}
        self.active_jobs: Set[str] = set()
        self.max_concurrent_jobs = 3

        self.orchestrator_stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "pending_approvals": 0,
            "average_completion_time": 0.0
        }

    async def create_learning_job(self, query: str, domain_whitelist: List[str],
                                requester: str) -> str:
        """
        Create a new learning job

        Args:
            query: Learning query
            domain_whitelist: Allowed domains
            requester: Who requested the job

        Returns:
            Job ID
        """
        job_id = f"learn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(query + str(domain_whitelist)) % 10000}"

        # Check if approval is needed
        approval_needed = await self._check_approval_needed(domain_whitelist)

        job = LearningJob(
            job_id=job_id,
            query=query,
            domain_whitelist=domain_whitelist,
            approval_required=approval_needed
        )

        self.jobs[job_id] = job
        self.orchestrator_stats["total_jobs"] += 1

        if approval_needed:
            self.orchestrator_stats["pending_approvals"] += 1

        # Log job creation
        await immutable_log.append(
            actor=requester,
            action="learning_job_created",
            resource=job_id,
            outcome="created",
            payload={
                "query": query,
                "domains": domain_whitelist,
                "approval_required": approval_needed
            }
        )

        # Auto-start if no approval needed
        if not approval_needed:
            asyncio.create_task(self.start_job(job_id))

        return job_id

    async def _check_approval_needed(self, domains: List[str]) -> bool:
        """Check if approval is needed for these domains"""
        from backend.learning_systems.governed_web_learning import domain_whitelist

        for domain in domains:
            allowed, reason, entry = domain_whitelist.check_domain_access(f"https://{domain}")
            if not allowed and reason and "requires approval" in reason:
                return True

        return False

    async def approve_job(self, job_id: str, approver: str) -> bool:
        """Approve a learning job"""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        if not job.approval_required:
            return False

        job.approved_by = approver
        job.approved_at = datetime.utcnow().isoformat()
        job.approval_required = False
        self.orchestrator_stats["pending_approvals"] -= 1

        # Log approval
        await immutable_log.append(
            actor=approver,
            action="learning_job_approved",
            resource=job_id,
            outcome="approved",
            payload={"job_id": job_id}
        )

        # Start the job
        asyncio.create_task(self.start_job(job_id))
        return True

    async def start_job(self, job_id: str):
        """Start a learning job"""
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]

        # Check concurrency limit
        if len(self.active_jobs) >= self.max_concurrent_jobs:
            logger.info(f"[JOB-ORCHESTRATOR] Delaying job {job_id} due to concurrency limit")
            await asyncio.sleep(30)  # Wait and retry
            asyncio.create_task(self.start_job(job_id))
            return

        job.status = "running"
        job.started_at = datetime.utcnow().isoformat()
        self.active_jobs.add(job_id)

        try:
            # Execute learning job
            results = await self._execute_learning_job(job)

            job.status = "completed"
            job.completed_at = datetime.utcnow().isoformat()
            job.results = results
            self.orchestrator_stats["completed_jobs"] += 1

            # Update completion time average
            if job.started_at and job.completed_at:
                start_time = datetime.fromisoformat(job.started_at)
                end_time = datetime.fromisoformat(job.completed_at)
                duration = (end_time - start_time).total_seconds()

                # Rolling average
                current_avg = self.orchestrator_stats["average_completion_time"]
                total_jobs = self.orchestrator_stats["completed_jobs"]
                self.orchestrator_stats["average_completion_time"] = \
                    (current_avg * (total_jobs - 1) + duration) / total_jobs

            # Log completion
            await immutable_log.append(
                actor="learning_orchestrator",
                action="learning_job_completed",
                resource=job_id,
                outcome="success",
                payload={"results_count": len(results)}
            )

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow().isoformat()
            self.orchestrator_stats["failed_jobs"] += 1

            logger.error(f"[JOB-ORCHESTRATOR] Job {job_id} failed: {e}")

            # Log failure
            await immutable_log.append(
                actor="learning_orchestrator",
                action="learning_job_failed",
                resource=job_id,
                outcome="failed",
                payload={"error": str(e)}
            )

        finally:
            self.active_jobs.discard(job_id)

    async def _execute_learning_job(self, job: LearningJob) -> List[Dict[str, Any]]:
        """Execute the actual learning job"""
        # This would integrate with web search and content extraction
        # For now, return mock results

        results = []
        for i in range(3):  # Mock 3 results
            result = {
                "title": f"Learning Result {i+1} for '{job.query}'",
                "url": f"https://example{i+1}.com/learn/{job.query.replace(' ', '_')}",
                "snippet": f"This is a mock learning result about {job.query}...",
                "domain": f"example{i+1}.com",
                "content_type": "tutorial",
                "relevance_score": 0.8 - (i * 0.1),
                "extracted_at": datetime.utcnow().isoformat()
            }
            results.append(result)

            # Simulate processing time
            await asyncio.sleep(0.5)

        return results

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        job = self.jobs.get(job_id)
        return job.to_dict() if job else None

    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all active jobs"""
        return [job.to_dict() for job in self.jobs.values() if job.status in ["pending", "running"]]

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return self.orchestrator_stats


class SandboxTester:
    """
    Sandbox testing for learned content before integration
    Validates content quality and safety before adding to knowledge base
    """

    def __init__(self):
        self.sandbox_stats = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "quality_score_avg": 0.0,
            "safety_violations": 0
        }

    async def test_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test content in sandbox environment

        Args:
            content: Content to test

        Returns:
            Test results
        """
        test_results = {
            "content_id": content.get("id", "unknown"),
            "passed": True,
            "quality_score": 0.0,
            "safety_check": True,
            "issues": [],
            "recommendations": [],
            "tested_at": datetime.utcnow().isoformat()
        }

        # Quality checks
        quality_issues = await self._check_content_quality(content)
        test_results["issues"].extend(quality_issues)

        # Safety checks
        safety_issues = await self._check_content_safety(content)
        test_results["issues"].extend(safety_issues)

        if safety_issues:
            test_results["safety_check"] = False
            self.sandbox_stats["safety_violations"] += 1

        # Calculate quality score
        test_results["quality_score"] = self._calculate_quality_score(content, test_results["issues"])

        # Determine pass/fail
        test_results["passed"] = len(test_results["issues"]) == 0 and test_results["safety_check"]

        # Generate recommendations
        test_results["recommendations"] = self._generate_recommendations(test_results["issues"])

        # Update stats
        self.sandbox_stats["total_tests"] += 1
        if test_results["passed"]:
            self.sandbox_stats["passed_tests"] += 1
        else:
            self.sandbox_stats["failed_tests"] += 1

        # Update quality average
        current_avg = self.sandbox_stats["quality_score_avg"]
        total_tests = self.sandbox_stats["total_tests"]
        self.sandbox_stats["quality_score_avg"] = \
            (current_avg * (total_tests - 1) + test_results["quality_score"]) / total_tests

        # Log test results
        await immutable_log.append(
            actor="sandbox_tester",
            action="content_tested",
            resource=test_results["content_id"],
            outcome="passed" if test_results["passed"] else "failed",
            payload=test_results
        )

        return test_results

    async def _check_content_quality(self, content: Dict[str, Any]) -> List[str]:
        """Check content quality"""
        issues = []

        text = content.get("text", "")
        title = content.get("title", "")

        # Length checks
        if len(text) < 100:
            issues.append("Content too short")
        if len(text) > 50000:  # 50k chars
            issues.append("Content too long")

        # Title checks
        if not title or len(title.strip()) < 5:
            issues.append("Title missing or too short")

        # Content checks
        if text.count('?') > text.count('.') * 2:
            issues.append("Too many questions relative to statements")

        # Check for code blocks if it's technical content
        if "code" in content.get("content_type", "").lower():
            if "```" not in text and "def " not in text and "class " not in text:
                issues.append("Technical content lacks code examples")

        return issues

    async def _check_content_safety(self, content: Dict[str, Any]) -> List[str]:
        """Check content safety"""
        issues = []

        text = content.get("text", "").lower()
        title = content.get("title", "").lower()

        # Check for harmful content patterns
        harmful_patterns = [
            "hack", "exploit", "malware", "virus", "trojan",
            "password crack", "sql injection", "xss",
            "illegal", "unlawful", "forbidden"
        ]

        for pattern in harmful_patterns:
            if pattern in text or pattern in title:
                issues.append(f"Potentially harmful content: '{pattern}'")

        # Check for PII patterns (basic)
        pii_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
            r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',    # SSN
        ]

        for pattern in pii_patterns:
            if re.search(pattern, text):
                issues.append("Contains potential PII")

        return issues

    def _calculate_quality_score(self, content: Dict[str, Any], issues: List[str]) -> float:
        """Calculate content quality score"""
        base_score = 0.8  # Start with good base

        # Deduct for issues
        issue_penalty = len(issues) * 0.1
        base_score -= issue_penalty

        # Bonus for good content attributes
        text = content.get("text", "")
        if len(text) > 1000:
            base_score += 0.05  # Substantial content
        if "```" in text:
            base_score += 0.05  # Has code examples
        if content.get("source_type") == "official_docs":
            base_score += 0.1  # Official documentation

        return max(0.0, min(1.0, base_score))

    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []

        for issue in issues:
            if "too short" in issue:
                recommendations.append("Expand content with more detailed explanations")
            elif "too long" in issue:
                recommendations.append("Consider splitting into multiple focused articles")
            elif "harmful" in issue:
                recommendations.append("Review content for security and ethical implications")
            elif "PII" in issue:
                recommendations.append("Remove or redact personally identifiable information")
            elif "code" in issue:
                recommendations.append("Add practical code examples and implementations")

        return recommendations

    def get_sandbox_stats(self) -> Dict[str, Any]:
        """Get sandbox testing statistics"""
        return self.sandbox_stats


# Global instances
domain_whitelist = DomainWhitelist()
learning_job_orchestrator = LearningJobOrchestrator()
sandbox_tester = SandboxTester()