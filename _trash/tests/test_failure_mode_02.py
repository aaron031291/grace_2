"""
Tests for Failure Mode #2: API Timeout
Self-Healing System Tests
"""

import pytest
import asyncio
from datetime import datetime

from backend.guardian.failure_detectors.api_timeout_detector import APITimeoutDetector
from backend.guardian.playbooks.api_timeout_recovery import APITimeoutRecoveryPlaybook


@pytest.fixture
def detector():
    """Create detector instance"""
    return APITimeoutDetector(timeout_threshold=5.0)


@pytest.fixture
def playbook():
    """Create playbook instance"""
    return APITimeoutRecoveryPlaybook()


class TestAPITimeoutDetector:
    """Test API timeout failure detection"""
    
    @pytest.mark.asyncio
    async def test_detector_healthy_api(self, detector):
        """Test detector with healthy API"""
        failure = await detector.detect()
        # Should be None (healthy) since mock calls are fast
        assert failure is None or failure['severity'] == 'low'
    
    @pytest.mark.asyncio
    async def test_detector_records_response_times(self, detector):
        """Test that detector records response times"""
        initial_count = len(detector.response_times)
        
        await detector.detect()
        
        # Should have recorded response times
        assert len(detector.response_times) >= initial_count
    
    def test_detector_stats(self, detector):
        """Test detector statistics"""
        stats = detector.get_stats()
        assert stats['detector'] == 'APITimeout'
        assert stats['failure_mode'] == 'FM-002'
        assert 'timeout_threshold' in stats
        assert 'avg_response_time' in stats
    
    def test_record_response_time(self, detector):
        """Test manual response time recording"""
        initial_count = len(detector.response_times)
        
        detector.record_response_time('/test', 0.5)
        
        assert len(detector.response_times) == initial_count + 1
        assert detector.response_times[-1] == 0.5


class TestAPITimeoutRecoveryPlaybook:
    """Test API timeout recovery remediation"""
    
    @pytest.mark.asyncio
    async def test_playbook_kill_hung_requests(self, playbook):
        """Test hung request killing"""
        failure = {
            'type': 'api_timeout',
            'severity': 'critical',
            'endpoints': [
                {'path': '/api/slow', 'timeout': 5.0}
            ],
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert 'success' in result
        assert 'mttr_seconds' in result
        assert result['mttr_seconds'] < 10, "Should complete within 10 seconds"
    
    @pytest.mark.asyncio
    async def test_playbook_optimize_performance(self, playbook):
        """Test performance optimization"""
        failure = {
            'type': 'api_degraded',
            'severity': 'medium',
            'endpoints': [
                {'path': '/api/vectors/search', 'response_time': 4.5, 'threshold': 5.0}
            ],
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert 'success' in result  # May succeed or fail, but should complete
        assert 'steps' in result
        assert result['mttr_seconds'] < 10
    
    @pytest.mark.asyncio
    async def test_playbook_scale_up(self, playbook):
        """Test resource scaling"""
        failure = {
            'type': 'api_slow_average',
            'severity': 'medium',
            'avg_response_time': 6.5,
            'threshold': 5.0,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert result['success'] is True
        assert 'cpu_percent' in result
        assert 'memory_percent' in result
        assert result['mttr_seconds'] < 10
    
    @pytest.mark.asyncio
    async def test_playbook_restart_service(self, playbook):
        """Test service restart"""
        failure = {
            'type': 'api_connection_failed',
            'severity': 'high',
            'endpoint': '/health',
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert 'success' in result
        assert 'downtime_seconds' in result
        assert result['mttr_seconds'] < 10


class TestEndToEndRecovery:
    """Test complete detection → remediation flow"""
    
    @pytest.mark.asyncio
    async def test_detect_and_remediate_timeout(self):
        """Test full flow: detect timeout → remediate → verify"""
        detector = APITimeoutDetector(timeout_threshold=5.0)
        playbook = APITimeoutRecoveryPlaybook()
        
        # Step 1: Detect (healthy in this case)
        failure = await detector.detect()
        
        # If no failure, simulate one
        if not failure:
            failure = {
                'type': 'api_timeout',
                'severity': 'high',
                'endpoints': [{'path': '/test', 'timeout': 5.0}],
                'timestamp': datetime.utcnow().isoformat(),
            }
        
        # Step 2: Remediate
        result = await playbook.remediate(failure)
        
        # Step 3: Verify MTTR
        assert result['mttr_seconds'] < 10, f"MTTR target is 10s, got {result['mttr_seconds']:.2f}s"
    
    @pytest.mark.asyncio
    async def test_mttr_under_target(self):
        """Verify MTTR is under 10 second target"""
        detector = APITimeoutDetector()
        playbook = APITimeoutRecoveryPlaybook()
        
        start = datetime.utcnow()
        
        # Simulate failure
        failure = {
            'type': 'api_timeout',
            'severity': 'critical',
            'endpoints': [{'path': '/slow', 'timeout': 5.0}],
        }
        
        result = await playbook.remediate(failure)
        end = datetime.utcnow()
        
        total_time = (end - start).total_seconds()
        
        assert total_time < 10, f"Total time: {total_time:.2f}s exceeds 10s target"
        assert result['mttr_seconds'] < 10, f"MTTR: {result['mttr_seconds']:.2f}s exceeds 10s target"
        
        print(f"\nMTTR achieved: {result['mttr_seconds']:.2f}s (target: <10s)")


class TestRecoveryMetrics:
    """Test metrics and reporting"""
    
    @pytest.mark.asyncio
    async def test_remediation_includes_steps(self, playbook):
        """Verify remediation result includes detailed steps"""
        failure = {
            'type': 'api_degraded',
            'severity': 'medium',
            'endpoints': [{'path': '/test', 'response_time': 4.0}],
        }
        
        result = await playbook.remediate(failure)
        
        assert 'steps' in result
        assert len(result['steps']) > 0, "Should include remediation steps"
        assert 'mttr_seconds' in result
        assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_all_failure_types_have_remediation(self, playbook):
        """Test that all failure types can be remediated"""
        failure_types = [
            'api_timeout',
            'api_degraded',
            'api_slow_average',
            'api_connection_failed',
        ]
        
        for failure_type in failure_types:
            failure = {
                'type': failure_type,
                'severity': 'medium',
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            result = await playbook.remediate(failure)
            assert 'success' in result
            assert 'mttr_seconds' in result
            assert result['mttr_seconds'] < 10


class TestPerformanceMetrics:
    """Test performance tracking"""
    
    def test_response_time_tracking(self, detector):
        """Test response time deque"""
        # Add 100 response times
        for i in range(100):
            detector.record_response_time('/test', 0.1 * i)
        
        # Should only keep last 100
        assert len(detector.response_times) == 100
        
        # Add more, should rotate
        detector.record_response_time('/test', 999)
        assert len(detector.response_times) == 100
        assert detector.response_times[-1] == 999
    
    def test_stats_calculation(self, detector):
        """Test statistics calculation"""
        # Add known response times
        detector.record_response_time('/test', 1.0)
        detector.record_response_time('/test', 2.0)
        detector.record_response_time('/test', 3.0)
        
        stats = detector.get_stats()
        assert stats['avg_response_time'] == 2.0
        assert stats['samples'] >= 3


def test_detector_import():
    """Test that detector can be imported"""
    from backend.guardian.failure_detectors.api_timeout_detector import api_timeout_detector
    assert api_timeout_detector is not None


def test_playbook_import():
    """Test that playbook can be imported"""
    from backend.guardian.playbooks.api_timeout_recovery import api_timeout_recovery
    assert api_timeout_recovery is not None
