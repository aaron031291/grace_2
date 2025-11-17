"""
Hunter Bridge - Active Security & Discovery

Scans and validates external integrations:
- Risk assessment
- TLS/security checks
- Credential validation
- Integrity verification
- CVE scanning
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import hashlib
import json
import sqlite3
import logging
import ssl
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DB_PATH = "databases/grace.db"


class ScanType(Enum):
    """Types of security scans"""
    TLS_CHECK = "tls_check"
    PORT_SCAN = "port_scan"
    CVE_SCAN = "cve_scan"
    CREDENTIAL_VALIDATION = "credential_validation"
    DATA_INTEGRITY = "data_integrity"
    RISK_ASSESSMENT = "risk_assessment"


class HunterBridge:
    """
    Security scanning and validation for external integrations
    
    Acts as gatekeeper between Grace and external world.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.scan_results = []
    
    async def scan_integration(
        self,
        integration_name: str,
        api_endpoint: str,
        auth_method: str,
        scopes: List[str]
    ) -> Dict[str, Any]:
        """
        Complete security scan of integration
        
        Returns:
            Scan results with pass/fail and risk score
        """
        
        scan_id = hashlib.sha256(
            f"{integration_name}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        results = {
            'scan_id': scan_id,
            'integration': integration_name,
            'timestamp': datetime.now().isoformat(),
            'passed': True,
            'risk_score': 0.0,
            'findings': [],
            'recommendations': []
        }
        
        # Scan 1: TLS/HTTPS check
        tls_result = await self._check_tls(api_endpoint)
        results['findings'].append(tls_result)
        if not tls_result['passed']:
            results['passed'] = False
            results['risk_score'] += 0.3
        
        # Scan 2: Credential safety
        cred_result = await self._validate_credentials(auth_method)
        results['findings'].append(cred_result)
        if not cred_result['passed']:
            results['passed'] = False
            results['risk_score'] += 0.2
        
        # Scan 3: Scope analysis
        scope_result = await self._analyze_scopes(scopes)
        results['findings'].append(scope_result)
        results['risk_score'] += scope_result['risk_score']
        
        # Scan 4: Known vulnerabilities
        cve_result = await self._check_cves(integration_name, api_endpoint)
        results['findings'].append(cve_result)
        if cve_result['critical_cves'] > 0:
            results['passed'] = False
            results['risk_score'] += 0.4
        
        # Store scan results
        await self._store_scan(results)
        
        # Generate recommendations
        if results['risk_score'] > 0.5:
            results['recommendations'].append("High risk score - requires manual approval")
        
        if not tls_result['passed']:
            results['recommendations'].append("Enforce HTTPS/TLS before activation")
        
        logger.info(f"[HUNTER] Scan complete: {integration_name} - Risk: {results['risk_score']:.2f}")
        
        return results
    
    async def _check_tls(self, endpoint: str) -> Dict[str, Any]:
        """Check TLS/HTTPS configuration"""
        
        result = {
            'scan_type': 'tls_check',
            'passed': True,
            'details': {}
        }
        
        try:
            parsed = urlparse(endpoint)
            
            # Must be HTTPS
            if parsed.scheme != 'https':
                result['passed'] = False
                result['details']['error'] = "Endpoint must use HTTPS"
                return result
            
            # Try TLS handshake
            hostname = parsed.netloc.split(':')[0]
            port = parsed.port or 443
            
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    result['details']['tls_version'] = ssock.version()
                    result['details']['cipher'] = ssock.cipher()[0]
                    result['details']['cert_valid'] = True
            
            result['passed'] = True
            
        except Exception as e:
            result['passed'] = False
            result['details']['error'] = str(e)
        
        return result
    
    async def _validate_credentials(self, auth_method: str) -> Dict[str, Any]:
        """Validate credential security"""
        
        result = {
            'scan_type': 'credential_validation',
            'passed': True,
            'details': {}
        }
        
        # Check auth method is secure
        secure_methods = ['oauth2', 'api_key', 'jwt', 'vault_secret']
        
        if auth_method.lower() not in secure_methods:
            result['passed'] = False
            result['details']['error'] = f"Unsupported auth method: {auth_method}"
            result['details']['allowed'] = secure_methods
        
        # Don't allow plaintext passwords
        if 'password' in auth_method.lower() and 'encrypted' not in auth_method.lower():
            result['passed'] = False
            result['details']['error'] = "Plaintext passwords not allowed"
        
        return result
    
    async def _analyze_scopes(self, scopes: List[str]) -> Dict[str, Any]:
        """Analyze requested scopes for risk"""
        
        result = {
            'scan_type': 'scope_analysis',
            'passed': True,
            'risk_score': 0.0,
            'details': {}
        }
        
        high_risk_scopes = ['write', 'delete', 'admin', 'full_access', 'sudo']
        medium_risk_scopes = ['create', 'update', 'modify']
        
        high_count = sum(1 for scope in scopes if any(hr in scope.lower() for hr in high_risk_scopes))
        medium_count = sum(1 for scope in scopes if any(mr in scope.lower() for mr in medium_risk_scopes))
        
        # Calculate risk score
        result['risk_score'] = (high_count * 0.3) + (medium_count * 0.1)
        result['details']['high_risk_scopes'] = high_count
        result['details']['medium_risk_scopes'] = medium_count
        result['details']['total_scopes'] = len(scopes)
        
        if high_count > 2:
            result['passed'] = False
            result['details']['warning'] = "Too many high-risk scopes requested"
        
        return result
    
    async def _check_cves(self, integration_name: str, endpoint: str) -> Dict[str, Any]:
        """Check for known vulnerabilities"""
        
        result = {
            'scan_type': 'cve_scan',
            'passed': True,
            'critical_cves': 0,
            'details': {}
        }
        
        # In production, query CVE databases
        # For now, simple heuristics
        
        suspicious_patterns = ['v0.', 'alpha', 'beta', 'dev', 'test']
        
        for pattern in suspicious_patterns:
            if pattern in endpoint.lower() or pattern in integration_name.lower():
                result['details']['warning'] = f"Suspicious pattern: {pattern}"
                result['risk_score'] = 0.2
        
        return result
    
    async def _store_scan(self, scan_results: Dict[str, Any]):
        """Store scan results in database"""
        
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            INSERT INTO memory_hunter_scans
            (scan_id, integration_id, scan_type, scan_timestamp, passed,
             findings, risk_score, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_results['scan_id'],
            scan_results['integration'],
            'composite',
            scan_results['timestamp'],
            scan_results['passed'],
            json.dumps(scan_results['findings']),
            scan_results['risk_score'],
            json.dumps(scan_results.get('recommendations', []))
        ))
        
        conn.commit()
        conn.close()
    
    async def verify_data_integrity(
        self,
        data: bytes,
        expected_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify data integrity using hash"""
        
        actual_hash = hashlib.sha256(data).hexdigest()
        
        if expected_hash:
            passed = actual_hash == expected_hash
        else:
            passed = True  # No expected hash to compare
        
        return {
            'passed': passed,
            'actual_hash': actual_hash,
            'expected_hash': expected_hash,
            'verified_at': datetime.now().isoformat()
        }
    
    def get_scan_history(self, integration_name: str) -> List[Dict]:
        """Get scan history for an integration"""
        
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT scan_id, scan_timestamp, passed, risk_score, findings
            FROM memory_hunter_scans
            WHERE integration_id = ?
            ORDER BY scan_timestamp DESC
            LIMIT 10
        """, (integration_name,))
        
        scans = []
        for row in cursor.fetchall():
            scans.append({
                'scan_id': row[0],
                'timestamp': row[1],
                'passed': bool(row[2]),
                'risk_score': row[3],
                'findings': json.loads(row[4]) if row[4] else []
            })
        
        conn.close()
        return scans


# Singleton
_hunter = None

def get_hunter_bridge() -> HunterBridge:
    global _hunter
    if _hunter is None:
        _hunter = HunterBridge()
    return _hunter
