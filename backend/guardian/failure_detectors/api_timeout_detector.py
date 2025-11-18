"""
API Timeout Failure Detector
Failure Mode #2: API Timeout/Slow Response

Detects:
- API response times >5s
- Connection timeouts
- Hung requests
- Degraded API performance
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class APITimeoutDetector:
    """
    Detects API timeout and performance degradation issues
    """
    
    def __init__(self, timeout_threshold: float = 5.0):
        self.timeout_threshold = timeout_threshold  # seconds
        self.check_interval = 60  # seconds
        self.last_check = None
        self.failure_count = 0
        self.consecutive_failures = 0
        
        # Track recent response times
        self.response_times = deque(maxlen=100)
        
        # Endpoints to monitor
        self.monitored_endpoints = [
            {'path': '/health', 'method': 'GET', 'timeout': 2.0},
            {'path': '/api/vectors/health', 'method': 'GET', 'timeout': 5.0},
            {'path': '/api/guardian/health', 'method': 'GET', 'timeout': 5.0},
            {'path': '/world-model/stats', 'method': 'GET', 'timeout': 5.0},
        ]
        
    async def detect(self) -> Optional[Dict[str, Any]]:
        """
        Detect API timeout issues
        
        Returns:
            Failure details if issue detected, None otherwise
        """
        try:
            failure = await self._check_api_health()
            
            if failure:
                self.consecutive_failures += 1
                self.failure_count += 1
                logger.warning(f"[API-DETECTOR] Failure detected: {failure['type']}")
                return failure
            else:
                self.consecutive_failures = 0
                return None
                
        except Exception as e:
            logger.error(f"[API-DETECTOR] Detector error: {e}")
            return {
                'type': 'detector_error',
                'severity': 'low',
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }
    
    async def _check_api_health(self) -> Optional[Dict[str, Any]]:
        """
        Check API endpoint health
        
        Returns:
            Failure info if unhealthy, None if healthy
        """
        
        # Check endpoints
        slow_endpoints = []
        timeout_endpoints = []
        
        for endpoint in self.monitored_endpoints:
            try:
                start_time = time.time()
                
                # Simulate API call (in production, use actual HTTP client)
                try:
                    await asyncio.wait_for(
                        self._mock_api_call(endpoint['path']),
                        timeout=endpoint['timeout']
                    )
                except asyncio.TimeoutError:
                    timeout_endpoints.append({
                        'path': endpoint['path'],
                        'timeout': endpoint['timeout'],
                    })
                    continue
                
                elapsed = time.time() - start_time
                self.response_times.append(elapsed)
                
                # Check if slow but not timeout
                if elapsed > endpoint['timeout'] * 0.8:  # 80% of timeout threshold
                    slow_endpoints.append({
                        'path': endpoint['path'],
                        'response_time': elapsed,
                        'threshold': endpoint['timeout'],
                    })
                    
            except Exception as e:
                # Connection error
                return {
                    'type': 'api_connection_failed',
                    'severity': 'high',
                    'endpoint': endpoint['path'],
                    'details': str(e),
                    'timestamp': datetime.utcnow().isoformat(),
                    'remediation': 'restart_service',
                }
        
        # Check for timeouts
        if timeout_endpoints:
            return {
                'type': 'api_timeout',
                'severity': 'critical' if len(timeout_endpoints) > 2 else 'high',
                'endpoints': timeout_endpoints,
                'count': len(timeout_endpoints),
                'timestamp': datetime.utcnow().isoformat(),
                'remediation': 'kill_hung_requests',
            }
        
        # Check for degraded performance
        if slow_endpoints:
            return {
                'type': 'api_degraded',
                'severity': 'medium',
                'endpoints': slow_endpoints,
                'count': len(slow_endpoints),
                'timestamp': datetime.utcnow().isoformat(),
                'remediation': 'optimize_or_scale',
            }
        
        # Check average response time
        if len(self.response_times) >= 10:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            
            if avg_response_time > self.timeout_threshold:
                return {
                    'type': 'api_slow_average',
                    'severity': 'medium',
                    'avg_response_time': avg_response_time,
                    'threshold': self.timeout_threshold,
                    'samples': len(self.response_times),
                    'timestamp': datetime.utcnow().isoformat(),
                    'remediation': 'scale_up',
                }
        
        # All checks passed
        self.last_check = datetime.utcnow()
        return None
    
    async def _mock_api_call(self, path: str):
        """
        Mock API call (in production, replace with actual HTTP client)
        
        In production:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://localhost:8000{path}') as response:
                return await response.json()
        """
        # Simulate fast API response
        await asyncio.sleep(0.01)
        return {'status': 'ok'}
    
    def record_response_time(self, endpoint: str, response_time: float):
        """
        Record response time for an endpoint
        
        Args:
            endpoint: API endpoint path
            response_time: Response time in seconds
        """
        self.response_times.append(response_time)
        
        if response_time > self.timeout_threshold:
            logger.warning(f"[API-DETECTOR] Slow response from {endpoint}: {response_time:.2f}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'detector': 'APITimeout',
            'failure_mode': 'FM-002',
            'timeout_threshold': self.timeout_threshold,
            'check_interval': self.check_interval,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'total_failures': self.failure_count,
            'consecutive_failures': self.consecutive_failures,
            'avg_response_time': avg_response,
            'samples': len(self.response_times),
        }


# Global instance
api_timeout_detector = APITimeoutDetector()
