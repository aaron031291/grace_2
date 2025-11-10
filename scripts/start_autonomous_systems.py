"""
Start All Autonomous Systems
Convenience script to initialize Grace's autonomous capabilities
"""

import asyncio
import logging
from backend.proactive_improvement_engine import proactive_improvement
from backend.performance_optimizer import performance_optimizer
from backend.autonomous_goal_setting import autonomous_goal_setting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_all_systems():
    """Start all autonomous systems"""
    
    logger.info("🚀 Starting Grace's Autonomous Systems...")
    
    try:
        # Start proactive improvement
        await proactive_improvement.start()
        logger.info("✅ Proactive Improvement Engine started")
        
        # Start performance optimizer
        await performance_optimizer.start()
        logger.info("✅ Performance Optimizer started")
        
        # Start autonomous goal-setting
        await autonomous_goal_setting.start()
        logger.info("✅ Autonomous Goal-Setting started")
        
        logger.info("\n🎯 All autonomous systems running!")
        logger.info("=" * 50)
        
        # Display status
        improvement_status = await proactive_improvement.get_status()
        logger.info(f"\n📊 Proactive Improvement:")
        logger.info(f"  - Cycle: {improvement_status['cycle_interval_hours']}h")
        logger.info(f"  - Proposed: {improvement_status['improvements_proposed']}")
        logger.info(f"  - Implemented: {improvement_status['improvements_implemented']}")
        
        optimizer_status = await performance_optimizer.get_status()
        logger.info(f"\n⚡ Performance Optimizer:")
        logger.info(f"  - Running: {optimizer_status['running']}")
        logger.info(f"  - Optimizations: {optimizer_status['optimizations_made']}")
        
        goal_status = await autonomous_goal_setting.get_status()
        logger.info(f"\n🎯 Autonomous Goals:")
        logger.info(f"  - Active: {goal_status['active_goals']}")
        logger.info(f"  - Completed: {goal_status['completed_goals']}")
        logger.info(f"  - Autonomous: {goal_status['autonomous_goals']}")
        
        logger.info("\n" + "=" * 50)
        logger.info("Press Ctrl+C to stop all systems")
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Stopping all systems...")
        await stop_all_systems()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await stop_all_systems()


async def stop_all_systems():
    """Stop all autonomous systems"""
    await proactive_improvement.stop()
    logger.info("✅ Proactive Improvement stopped")
    
    await performance_optimizer.stop()
    logger.info("✅ Performance Optimizer stopped")
    
    await autonomous_goal_setting.stop()
    logger.info("✅ Autonomous Goal-Setting stopped")
    
    logger.info("👋 All systems stopped cleanly")


if __name__ == "__main__":
    asyncio.run(start_all_systems())
