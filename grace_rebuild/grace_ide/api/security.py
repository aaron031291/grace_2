"""Security scanning engine for IDE"""

import re
from typing import List, Dict
from pathlib import Path

class SecurityEngine:
    """Static analysis and security scanning"""
    
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf', 'critical', 'Dangerous file deletion command'),
        (r'DROP\s+TABLE', 'critical', 'SQL drop table command'),
        (r'eval\s*\(', 'high', 'Dangerous eval() usage'),
        (r'exec\s*\(', 'high', 'Dangerous exec() usage'),
        (r'__import__\s*\(', 'medium', 'Dynamic import'),
        (r'os\.system', 'high', 'System command execution'),
        (r'subprocess\.', 'medium', 'Subprocess usage'),
    ]
    
    SECRET_PATTERNS = [
        (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
        (r'[A-Za-z0-9]{32,}', 'Possible secret/hash'),
    ]
    
    async def scan_content(self, content: str, file_path: str = "") -> Dict:
        """Scan code content for security issues"""
        
        findings = []
        
        for pattern, severity, description in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "type": "dangerous_code",
                    "severity": severity,
                    "description": description,
                    "line": content[:match.start()].count('\n') + 1,
                    "matched": match.group()
                })
        
        for pattern, description in self.SECRET_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "type": "secret_exposure",
                    "severity": "high",
                    "description": description,
                    "line": content[:match.start()].count('\n') + 1
                })
        
        risk_score = self._calculate_risk(findings)
        
        return {
            "file": file_path,
            "findings": findings,
            "risk_score": risk_score,
            "recommendation": self._get_recommendation(risk_score)
        }
    
    def _calculate_risk(self, findings: List[Dict]) -> float:
        """Calculate overall risk score (0-10)"""
        severity_weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 2
        }
        
        total = sum(severity_weights.get(f.get("severity", "low"), 0) for f in findings)
        return min(10.0, total / 10)
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Get security recommendation based on risk"""
        if risk_score >= 8:
            return "CRITICAL: Block execution, review required"
        elif risk_score >= 5:
            return "HIGH RISK: Recommend review before execution"
        elif risk_score >= 2:
            return "MEDIUM RISK: Proceed with caution"
        else:
            return "LOW RISK: Safe to execute"

security_engine = SecurityEngine()
