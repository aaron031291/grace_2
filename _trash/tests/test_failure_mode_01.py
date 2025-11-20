"""
Tests for Failure Mode #1: Database Connection Lost
Self-Healing System Tests
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from backend.guardian.failure_detectors.db_connection_detector import DatabaseConnectionDetector
from backend.guardian.playbooks.database_recovery import DatabaseRecoveryPlaybook


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test.db"
    
    # Create valid database
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)")
    conn.execute("INSERT INTO test_table (data) VALUES ('test data')")
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def detector(temp_db):
    """Create detector instance"""
    return DatabaseConnectionDetector(db_path=str(temp_db))


@pytest.fixture
def playbook(temp_db):
    """Create playbook instance"""
    return DatabaseRecoveryPlaybook(db_path=str(temp_db))


class TestDatabaseConnectionDetector:
    """Test database connection failure detection"""
    
    @pytest.mark.asyncio
    async def test_detector_healthy_database(self, detector, temp_db):
        """Test detector with healthy database"""
        failure = await detector.detect()
        assert failure is None, "Should not detect failure on healthy database"
    
    @pytest.mark.asyncio
    async def test_detector_missing_database(self, detector, temp_db):
        """Test detector when database file is missing"""
        temp_db.unlink()  # Delete database
        
        failure = await detector.detect()
        assert failure is not None, "Should detect missing database"
        assert failure['type'] == 'db_file_missing'
        assert failure['severity'] == 'critical'
    
    @pytest.mark.asyncio
    async def test_detector_corrupted_database(self, detector, temp_db):
        """Test detector with corrupted database"""
        # Corrupt the database by overwriting header
        with open(temp_db, 'r+b') as f:
            f.seek(0)
            f.write(b'CORRUPTED' * 10)  # Overwrite SQLite header
        
        failure = await detector.detect()
        assert failure is not None, "Should detect corrupted database"
        assert failure['type'] in ['db_corrupted', 'db_integrity_failed', 'db_connection_failed', 'db_query_failed', 'db_integrity_check_failed']
    
    def test_detector_stats(self, detector):
        """Test detector statistics"""
        stats = detector.get_stats()
        assert stats['detector'] == 'DatabaseConnection'
        assert stats['failure_mode'] == 'FM-001'
        assert 'db_path' in stats
        assert 'total_failures' in stats


class TestDatabaseRecoveryPlaybook:
    """Test database recovery remediation"""
    
    @pytest.mark.asyncio
    async def test_playbook_retry_connection(self, playbook, temp_db):
        """Test connection retry remediation"""
        failure = {
            'type': 'db_connection_failed',
            'severity': 'high',
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert 'success' in result
        assert 'mttr_seconds' in result
        assert result['mttr_seconds'] < 60, "Should complete within 60 seconds"
    
    @pytest.mark.asyncio
    async def test_playbook_checkpoint_wal(self, playbook, temp_db):
        """Test WAL checkpoint remediation"""
        # Enable WAL mode
        conn = sqlite3.connect(str(temp_db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("INSERT INTO test_table (data) VALUES ('more data')")
        conn.commit()
        conn.close()
        
        failure = {
            'type': 'wal_file_too_large',
            'severity': 'medium',
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert result['success'] is True
        assert 'mttr_seconds' in result
        assert result['mttr_seconds'] < 30, "WAL checkpoint should be fast"
    
    @pytest.mark.asyncio
    async def test_playbook_restore_missing_db(self, playbook, temp_db):
        """Test restore when database is missing"""
        # Delete database
        temp_db.unlink()
        
        failure = {
            'type': 'db_file_missing',
            'severity': 'critical',
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        result = await playbook.remediate(failure)
        assert result['success'] is True, "Should create fresh database"
        assert temp_db.exists(), "Database should be recreated"
        assert 'mttr_seconds' in result
        assert result['mttr_seconds'] < 60
    
    @pytest.mark.asyncio
    async def test_playbook_backup_creation(self, playbook, temp_db):
        """Test backup creation"""
        backup_path = await playbook.create_backup()
        
        assert backup_path is not None, "Backup should be created"
        assert backup_path.exists(), "Backup file should exist"
        assert backup_path.stat().st_size > 0, "Backup should not be empty"


class TestEndToEndRecovery:
    """Test complete detection → remediation flow"""
    
    @pytest.mark.asyncio
    async def test_detect_and_remediate_missing_db(self, temp_db):
        """Test full flow: detect missing DB → remediate → verify"""
        detector = DatabaseConnectionDetector(db_path=str(temp_db))
        playbook = DatabaseRecoveryPlaybook(db_path=str(temp_db))
        
        # Step 1: Delete database
        temp_db.unlink()
        
        # Step 2: Detect failure
        failure = await detector.detect()
        assert failure is not None
        assert failure['type'] == 'db_file_missing'
        
        # Step 3: Remediate
        result = await playbook.remediate(failure)
        assert result['success'] is True
        
        # Step 4: Verify recovery
        recovery_check = await detector.detect()
        assert recovery_check is None, "Should be healthy after remediation"
        
        # Step 5: Verify MTTR target met
        assert result['mttr_seconds'] < 60, f"MTTR target is 60s, got {result['mttr_seconds']:.2f}s"
    
    @pytest.mark.asyncio
    async def test_mttr_under_target(self, temp_db):
        """Verify MTTR is under 60 second target"""
        detector = DatabaseConnectionDetector(db_path=str(temp_db))
        playbook = DatabaseRecoveryPlaybook(db_path=str(temp_db))
        
        # Simulate failure and remediation
        temp_db.unlink()
        
        start = datetime.utcnow()
        failure = await detector.detect()
        result = await playbook.remediate(failure)
        end = datetime.utcnow()
        
        total_time = (end - start).total_seconds()
        
        assert total_time < 60, f"Total detection + remediation time: {total_time:.2f}s exceeds 60s target"
        assert result['mttr_seconds'] < 60, f"MTTR: {result['mttr_seconds']:.2f}s exceeds 60s target"
        
        print(f"\nMTTR achieved: {result['mttr_seconds']:.2f}s (target: <60s)")


class TestRecoveryMetrics:
    """Test metrics and reporting"""
    
    @pytest.mark.asyncio
    async def test_remediation_includes_steps(self, playbook, temp_db):
        """Verify remediation result includes detailed steps"""
        temp_db.unlink()
        
        failure = {'type': 'db_file_missing', 'severity': 'critical'}
        result = await playbook.remediate(failure)
        
        assert 'steps' in result
        assert len(result['steps']) > 0, "Should include remediation steps"
        assert 'mttr_seconds' in result
        assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_consecutive_failure_tracking(self, detector):
        """Test tracking of consecutive failures"""
        initial_count = detector.consecutive_failures
        
        # Simulate failure
        detector.db_path.unlink()
        await detector.detect()
        
        assert detector.consecutive_failures == initial_count + 1
        assert detector.failure_count >= 1


def test_playbook_import():
    """Test that playbook can be imported"""
    from backend.guardian.playbooks.database_recovery import db_recovery_playbook
    assert db_recovery_playbook is not None


def test_detector_import():
    """Test that detector can be imported"""
    from backend.guardian.failure_detectors.db_connection_detector import db_connection_detector
    assert db_connection_detector is not None
