"""
Automation Engine
Runs Grace's automation in auto mode (non-interactive)
All background tasks run on schedule without manual triggers
"""

import asyncio
import logging

from .grace_control_center import grace_control, SystemState
from .research_sweeper import research_sweeper
from .autonomous_improvement_workflow import autonomous_improvement

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Automation engine for non-interactive operation
    
    Modes:
    - manual: Requires user trigger for each action
    - auto: Runs on schedule without prompts
    
    When in auto mode:
    - PDF ingestion runs on schedule
    - Research sweeps run hourly
    - Sandbox experiments run as queued
    - Note generation runs automatically
    - Vector updates happen continuously
    """
    
    def __init__(self):
        self.mode = 'manual'  # Default to manual
        self.running = False
        self.tasks = {}
    
    async def start(self, mode: str = 'manual'):
        """
        Start automation engine
        
        Args:
            mode: 'manual' or 'auto'
        """
        
        self.mode = mode
        self.running = True
        
        logger.info(f"[AUTOMATION-ENGINE] Starting in {mode} mode...")
        
        if mode == 'auto':
            # Start all automated tasks
            await self._start_auto_mode()
        else:
            # Manual mode - tasks triggered explicitly
            await self._start_manual_mode()
        
        logger.info(f"[AUTOMATION-ENGINE] Started in {mode} mode")
    
    async def stop(self):
        """Stop automation engine"""
        
        self.running = False
        
        # Stop all tasks
        for task_name, task in self.tasks.items():
            if task and not task.done():
                task.cancel()
        
        logger.info("[AUTOMATION-ENGINE] Stopped")
    
    async def _start_auto_mode(self):
        """Start auto mode - all tasks run on schedule"""
        
        print("=" * 80)
        print("AUTO MODE ENABLED - Grace runs autonomously")
        print("=" * 80)
        print("""
Background tasks will run automatically:
- Research sweeps (hourly)
- PDF ingestion (continuous)
- Sandbox experiments (as queued)
- Note generation (automatic)
- Vector updates (continuous)
- Improvement cycles (daily)

Auto-approval enabled for:
- Low-risk changes with trust ≥ 80%
- Research library ingestion
- Self-healing patches (trust ≥ 85%)

Human review required for:
- Medium/high risk changes
- Infrastructure modifications
- New API integrations

Control:
- ESC = Emergency stop
- Pause button = Pause automation
- Daily reports available

""")
        print("=" * 80)
        
        # Start scheduled tasks
        self.tasks['research_sweeper'] = asyncio.create_task(
            self._run_scheduled_task('research_sweeper', 3600)  # Hourly
        )
        
        self.tasks['improvement_cycle'] = asyncio.create_task(
            self._run_scheduled_task('improvement_cycle', 86400)  # Daily
        )
        
        self.tasks['daily_report'] = asyncio.create_task(
            self._run_scheduled_task('daily_report', 86400)  # Daily
        )
        
        logger.info("[AUTOMATION-ENGINE] Auto mode tasks scheduled")
    
    async def _start_manual_mode(self):
        """Start manual mode - tasks triggered explicitly"""
        
        print("=" * 80)
        print("MANUAL MODE - Tasks require explicit trigger")
        print("=" * 80)
        
        logger.info("[AUTOMATION-ENGINE] Manual mode active")
    
    async def _run_scheduled_task(self, task_name: str, interval_seconds: int):
        """Run task on schedule"""
        
        while self.running:
            try:
                # Check if system is paused
                state = grace_control.get_state()
                
                if state['system_state'] != SystemState.RUNNING:
                    # System paused, wait and retry
                    await asyncio.sleep(60)
                    continue
                
                # Execute task
                logger.info(f"[AUTOMATION-ENGINE] Running scheduled task: {task_name}")
                
                if task_name == 'research_sweeper':
                    await research_sweeper.run_sweep()
                
                elif task_name == 'improvement_cycle':
                    await autonomous_improvement.run_improvement_cycle()
                
                elif task_name == 'daily_report':
                    await self._generate_daily_report()
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AUTOMATION-ENGINE] Error in {task_name}: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error
    
    async def _generate_daily_report(self):
        """Generate daily summary report"""
        
        from .daily_reporter import daily_reporter
        
        report = await daily_reporter.generate_daily_brief()
        
        logger.info(f"[AUTOMATION-ENGINE] Daily report generated: {report}")


# Global instance
automation_engine = AutomationEngine()
