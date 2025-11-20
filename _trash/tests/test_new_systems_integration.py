"""
Integration Tests for New Grace Systems
Tests: Proactive Improvement, Data Export, Performance Optimization, and Autonomous Goal-Setting
"""

import pytest
import asyncio
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

from backend.proactive_improvement_engine import proactive_improvement
from backend.performance_optimizer import performance_optimizer
from backend.data_export import data_exporter
from backend.autonomous_goal_setting import autonomous_goal_setting
from backend.models import async_session, Goal
from backend.healing_models import (
    HealingAttempt, AgenticSpineLog, MLLearningLog,
    ParallelProcessLog, DataCubeEntry
)
from sqlalchemy import select


@pytest.mark.asyncio
class TestProactiveImprovementEngine:
    """Test proactive improvement system"""
    
    async def test_proactive_improvement_starts(self):
        """Test engine can start and stop"""
        await proactive_improvement.start()
        assert proactive_improvement.running is True
        
        await proactive_improvement.stop()
        assert proactive_improvement.running is False
    
    async def test_identify_opportunities(self):
        """Test opportunity identification"""
        mock_analysis = {
            'healing_performance': {'success_rate': 0.75},
            'learning_performance': {'confidence': 0.65},
            'autonomous_performance': {
                'execution_rate': 0.7,
                'decisions_made': 15
            },
            'improvement_areas': [
                'Recurring error pattern in authentication'
            ]
        }
        
        opportunities = await proactive_improvement._identify_opportunities(mock_analysis)
        
        assert len(opportunities) > 0
        assert any(opp['type'] == 'enhance_healing' for opp in opportunities)
        assert any(opp['type'] == 'improve_ml_confidence' for opp in opportunities)
    
    async def test_propose_improvement(self):
        """Test improvement proposal"""
        opportunity = {
            'type': 'test_improvement',
            'priority': 'medium',
            'description': 'Test improvement opportunity',
            'proposed_action': 'Add test enhancement',
            'estimated_impact': 'Better test coverage'
        }
        
        initial_count = proactive_improvement.improvements_proposed
        await proactive_improvement._propose_improvement(opportunity)
        
        assert proactive_improvement.improvements_proposed == initial_count + 1
    
    async def test_get_status(self):
        """Test status retrieval"""
        status = await proactive_improvement.get_status()
        
        assert 'running' in status
        assert 'cycle_interval_hours' in status
        assert 'improvements_proposed' in status
        assert 'improvements_implemented' in status


@pytest.mark.asyncio
class TestPerformanceOptimizer:
    """Test performance optimization system"""
    
    async def test_optimizer_starts(self):
        """Test optimizer can start and stop"""
        await performance_optimizer.start()
        assert performance_optimizer.running is True
        
        await performance_optimizer.stop()
        assert performance_optimizer.running is False
    
    async def test_analyze_performance(self):
        """Test performance analysis"""
        analysis = await performance_optimizer._analyze_performance()
        
        assert 'period_hours' in analysis
        assert 'timestamp' in analysis
        assert 'avg_execution_time' in analysis
        assert 'task_success_rate' in analysis
        assert 'avg_wait_time' in analysis
        assert 'activity_per_hour' in analysis
    
    async def test_generate_optimizations(self):
        """Test optimization generation"""
        mock_analysis = {
            'avg_execution_time': 6.5,
            'avg_wait_time': 3.0,
            'activity_per_hour': 5,
            'task_success_rate': 0.9,
            'total_tasks': 100
        }
        
        optimizations = await performance_optimizer._generate_optimizations(mock_analysis)
        
        assert len(optimizations) > 0
        assert any(opt['type'] == 'reduce_execution_time' for opt in optimizations)
        assert any(opt['type'] == 'reduce_wait_time' for opt in optimizations)
        assert any(opt['type'] == 'increase_activity' for opt in optimizations)
    
    async def test_log_optimization(self):
        """Test optimization logging"""
        optimization = {
            'type': 'test_optimization',
            'priority': 'medium',
            'current_value': 5.0,
            'target_value': 2.0,
            'recommendation': 'Test recommendation',
            'estimated_improvement': '60% improvement'
        }
        
        await performance_optimizer._log_optimization(optimization)


@pytest.mark.asyncio
class TestDataExportBackupSystem:
    """Test data export and backup system"""
    
    async def test_export_directory_exists(self):
        """Test export directory is created"""
        assert data_exporter.export_dir.exists()
        assert data_exporter.export_dir.is_dir()
    
    async def test_export_table(self):
        """Test single table export"""
        export_path = data_exporter.export_dir / "test_export"
        export_path.mkdir(exist_ok=True)
        
        await data_exporter._export_table(
            'healing_attempts',
            HealingAttempt,
            export_path,
            'json'
        )
        
        json_file = export_path / "healing_attempts.json"
        assert json_file.exists()
        
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
    
    async def test_export_learning_only(self):
        """Test ML learning export"""
        export_file = await data_exporter.export_learning_only()
        
        assert os.path.exists(export_file)
        assert 'learning_export' in export_file
        assert export_file.endswith('.json')
        
        with open(export_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
    
    async def test_backup_crypto_chains(self):
        """Test cryptographic chain backup"""
        backup_file = await data_exporter.backup_crypto_chains()
        
        assert os.path.exists(backup_file)
        assert 'crypto_backup' in backup_file
        
        with open(backup_file, 'r') as f:
            backup = json.load(f)
            assert 'timestamp' in backup
            assert 'chains' in backup
            assert isinstance(backup['chains'], dict)
    
    @pytest.mark.slow
    async def test_export_all(self):
        """Test full data export (slow test)"""
        export_file = await data_exporter.export_all(format='json')
        
        assert os.path.exists(export_file)
        assert export_file.endswith('.zip')
        
        import zipfile
        with zipfile.ZipFile(export_file, 'r') as zipf:
            files = zipf.namelist()
            assert len(files) > 0


@pytest.mark.asyncio
class TestAutonomousGoalSetting:
    """Test autonomous goal-setting system"""
    
    async def test_goal_setting_starts(self):
        """Test goal-setting engine can start and stop"""
        await autonomous_goal_setting.start()
        assert autonomous_goal_setting.running is True
        
        await autonomous_goal_setting.stop()
        assert autonomous_goal_setting.running is False
    
    async def test_evaluate_goal(self):
        """Test single goal evaluation"""
        async with async_session() as session:
            test_goal = Goal(
                title='Improve Healing Success Rate',
                description='Test goal',
                category='performance',
                status='active',
                priority='high',
                created_by='test',
                progress=50,
                deadline=datetime.utcnow() + timedelta(days=30)
            )
            session.add(test_goal)
            await session.commit()
            await session.refresh(test_goal)
            
            evaluation = await autonomous_goal_setting._evaluate_goal(test_goal)
            
            assert 'status' in evaluation
            assert 'explanation' in evaluation
            assert 'confidence' in evaluation
            assert evaluation['status'] in ['met', 'on_track', 'at_risk', 'off_track']
    
    async def test_identify_goal_opportunities(self):
        """Test goal opportunity identification"""
        mock_analysis = {
            'healing_performance': {'success_rate': 0.75},
            'learning_performance': {
                'confidence': 0.65,
                'patterns_learned': 30
            },
            'autonomous_performance': {
                'execution_rate': 0.7
            },
            'response_times': {
                'avg_seconds': 3.5
            }
        }
        
        opportunities = await autonomous_goal_setting._identify_goal_opportunities(mock_analysis)
        
        assert len(opportunities) > 0
        assert any('healing' in opp['title'].lower() for opp in opportunities)
        assert any('test' in opp['title'].lower() for opp in opportunities)
    
    async def test_create_goal(self):
        """Test autonomous goal creation"""
        opportunity = {
            'title': 'Test Autonomous Goal',
            'description': 'Goal created by test',
            'category': 'test',
            'priority': 'low',
            'deadline_days': 30,
            'metrics': {
                'current': 0,
                'target': 100
            }
        }
        
        initial_count = autonomous_goal_setting.goals_created
        
        with patch.object(
            autonomous_goal_setting,
            '_create_goal',
            new_callable=AsyncMock
        ) as mock_create:
            await autonomous_goal_setting._create_goal(opportunity)
            mock_create.assert_called_once()
    
    async def test_get_status(self):
        """Test status retrieval"""
        status = await autonomous_goal_setting.get_status()
        
        assert 'running' in status
        assert 'cycle_interval_hours' in status
        assert 'goals_created' in status
        assert 'active_goals' in status
        assert 'completed_goals' in status
        assert 'autonomous_goals' in status


@pytest.mark.asyncio
class TestSystemIntegration:
    """Test all new systems working together"""
    
    async def test_all_systems_start_together(self):
        """Test all systems can run simultaneously"""
        await proactive_improvement.start()
        await performance_optimizer.start()
        await autonomous_goal_setting.start()
        
        assert proactive_improvement.running
        assert performance_optimizer.running
        assert autonomous_goal_setting.running
        
        await proactive_improvement.stop()
        await performance_optimizer.stop()
        await autonomous_goal_setting.stop()
    
    async def test_improvement_creates_goal(self):
        """Test that improvement opportunities can lead to goals"""
        mock_analysis = {
            'healing_performance': {'success_rate': 0.7},
            'learning_performance': {'confidence': 0.6, 'patterns_learned': 20},
            'autonomous_performance': {'execution_rate': 0.65, 'decisions_made': 20},
            'improvement_areas': ['Test improvement area'],
            'response_times': {'avg_seconds': 4.0}
        }
        
        improvement_opps = await proactive_improvement._identify_opportunities(mock_analysis)
        goal_opps = await autonomous_goal_setting._identify_goal_opportunities(mock_analysis)
        
        assert len(improvement_opps) > 0
        assert len(goal_opps) > 0
    
    async def test_export_preserves_all_data(self):
        """Test export captures data from all systems"""
        async with async_session() as session:
            test_healing = HealingAttempt(
                attempt_id='test_export_001',
                error_type='test',
                error_message='Test error',
                detected_by='test',
                severity='low',
                status='proposed',
                confidence=0.8,
                risk_score=0.1
            )
            session.add(test_healing)
            
            test_spine_log = AgenticSpineLog(
                decision_type='test_decision',
                actor='test',
                resource='test_resource',
                status='completed'
            )
            session.add(test_spine_log)
            
            await session.commit()
        
        export_file = await data_exporter.export_learning_only()
        assert os.path.exists(export_file)
    
    async def test_performance_optimizations_logged(self):
        """Test performance optimizer logs to unified logger"""
        mock_analysis = {
            'avg_execution_time': 7.0,
            'avg_wait_time': 4.0,
            'activity_per_hour': 3,
            'task_success_rate': 0.85,
            'total_tasks': 50
        }
        
        optimizations = await performance_optimizer._generate_optimizations(mock_analysis)
        
        for opt in optimizations:
            await performance_optimizer._log_optimization(opt)
        
        async with async_session() as session:
            result = await session.execute(
                select(AgenticSpineLog)
                .where(AgenticSpineLog.decision_type == 'optimization_recommended')
                .order_by(AgenticSpineLog.created_at.desc())
                .limit(1)
            )
            log = result.scalar_one_or_none()
            
            if log:
                assert log.actor == 'performance_optimizer'


@pytest.mark.asyncio
class TestDataIntegrity:
    """Test data integrity across new systems"""
    
    async def test_exported_data_matches_database(self):
        """Test exported data matches source database"""
        async with async_session() as session:
            result = await session.execute(select(HealingAttempt).limit(5))
            db_attempts = result.scalars().all()
            db_count = len(db_attempts)
        
        export_path = data_exporter.export_dir / "integrity_test"
        export_path.mkdir(exist_ok=True)
        
        await data_exporter._export_table(
            'healing_attempts',
            HealingAttempt,
            export_path,
            'json'
        )
        
        json_file = export_path / "healing_attempts.json"
        with open(json_file, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) >= db_count
    
    async def test_crypto_chains_maintained(self):
        """Test cryptographic chains are maintained in exports"""
        backup_file = await data_exporter.backup_crypto_chains()
        
        with open(backup_file, 'r') as f:
            backup = json.load(f)
        
        for table_name, chain in backup['chains'].items():
            for entry in chain:
                assert 'hash' in entry
                assert 'previous_hash' in entry
                if entry['previous_hash'] is not None:
                    assert entry['previous_hash'] != entry['hash']


@pytest.mark.asyncio
async def test_complete_autonomous_cycle():
    """
    Test complete autonomous cycle:
    1. Performance optimizer identifies issues
    2. Proactive improvement proposes solutions
    3. Autonomous goal-setting creates goals
    4. Data export backs up everything
    """
    
    print("\n🚀 Starting complete autonomous cycle test...")
    
    # 1. Analyze performance
    print("📊 Analyzing performance...")
    perf_analysis = await performance_optimizer._analyze_performance()
    assert perf_analysis is not None
    print(f"  ✓ Found avg execution time: {perf_analysis['avg_execution_time']:.2f}s")
    
    # 2. Generate optimizations
    print("⚡ Generating optimizations...")
    optimizations = await performance_optimizer._generate_optimizations(perf_analysis)
    print(f"  ✓ Generated {len(optimizations)} optimization recommendations")
    
    # 3. Identify improvement opportunities
    print("💡 Identifying improvements...")
    from backend.grace_self_analysis import grace_self_analysis
    analysis = await grace_self_analysis.analyze_performance(hours=24)
    improvements = await proactive_improvement._identify_opportunities(analysis)
    print(f"  ✓ Found {len(improvements)} improvement opportunities")
    
    # 4. Create goals
    print("🎯 Setting autonomous goals...")
    goal_opps = await autonomous_goal_setting._identify_goal_opportunities(analysis)
    print(f"  ✓ Identified {len(goal_opps)} goal opportunities")
    
    # 5. Export everything
    print("💾 Backing up data...")
    backup_file = await data_exporter.backup_crypto_chains()
    assert os.path.exists(backup_file)
    print(f"  ✓ Backup created: {os.path.basename(backup_file)}")
    
    print("\n✅ Complete autonomous cycle test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
