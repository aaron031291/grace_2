"""
Orchestrator Integration for Librarian Kernel
Registers Librarian as a Data Orchestrator component in the stage list
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LibrarianOrchestratorStage:
    """
    Orchestrator stage for the Librarian Data Orchestrator.
    
    Plugs into the existing orchestrator alongside other kernels,
    managing the memory/intake/sub-agent pipeline as a separate component.
    """
    
    def __init__(self, clarity_adapter):
        self.adapter = clarity_adapter
        self.stage_id = "data_orchestrator"
        self.stage_name = "Librarian Data Orchestrator"
        
        # Stage configuration
        self.config = {
            'auto_start': True,
            'critical': False,  # System can run without it
            'health_check_interval': 30,
            'restart_on_failure': True,
            'max_restart_attempts': 3
        }
        
        self.restart_attempts = 0
        self.last_health_check = None
    
    async def initialize(self) -> bool:
        """
        Initialize the Data Orchestrator stage.
        Called by orchestrator during system startup.
        """
        try:
            logger.info(f"Initializing {self.stage_name}...")
            
            # Initialize clarity adapter (which starts the kernel)
            await self.adapter.initialize()
            
            logger.info(f"{self.stage_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.stage_name}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for orchestrator monitoring.
        
        Returns health status dict compatible with orchestrator.
        """
        self.last_health_check = datetime.utcnow()
        
        try:
            # Update adapter health
            await self.adapter.update_health()
            
            # Get kernel status
            kernel_status = self.adapter.kernel.get_status()
            queue_status = self.adapter.kernel.get_queue_status()
            
            # Determine overall health
            is_healthy = (
                kernel_status['status'] in ['running', 'paused']
                and self.adapter.health_status in ['healthy', 'warning']
            )
            
            return {
                'stage_id': self.stage_id,
                'stage_name': self.stage_name,
                'healthy': is_healthy,
                'status': kernel_status['status'],
                'health_status': self.adapter.health_status,
                'details': {
                    'active_agents': kernel_status['active_agents'],
                    'queue_depths': queue_status,
                    'metrics': kernel_status['metrics'],
                    'last_heartbeat': kernel_status.get('last_heartbeat'),
                    'trust_score': self.adapter.trust_score
                },
                'timestamp': self.last_health_check.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'stage_id': self.stage_id,
                'stage_name': self.stage_name,
                'healthy': False,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def start(self) -> bool:
        """Start the Data Orchestrator stage"""
        try:
            if self.adapter.kernel.status.value != 'running':
                success = await self.adapter.kernel.start()
                if success:
                    self.restart_attempts = 0
                return success
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {self.stage_name}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the Data Orchestrator stage"""
        try:
            await self.adapter.shutdown()
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {self.stage_name}: {e}")
            return False
    
    async def pause(self) -> bool:
        """Pause the Data Orchestrator stage"""
        try:
            await self.adapter.kernel.pause()
            return True
        except Exception as e:
            logger.error(f"Failed to pause {self.stage_name}: {e}")
            return False
    
    async def resume(self) -> bool:
        """Resume the Data Orchestrator stage"""
        try:
            await self.adapter.kernel.resume()
            return True
        except Exception as e:
            logger.error(f"Failed to resume {self.stage_name}: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the Data Orchestrator stage"""
        if self.restart_attempts >= self.config['max_restart_attempts']:
            logger.error(f"Max restart attempts reached for {self.stage_name}")
            return False
        
        self.restart_attempts += 1
        
        try:
            await self.stop()
            await asyncio.sleep(2)
            return await self.start()
        except Exception as e:
            logger.error(f"Failed to restart {self.stage_name}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current stage status for orchestrator dashboard"""
        kernel_status = self.adapter.kernel.get_status()
        
        return {
            'stage_id': self.stage_id,
            'stage_name': self.stage_name,
            'component_id': self.adapter.component_id,
            'kernel_status': kernel_status['status'],
            'health': self.adapter.health_status,
            'trust_score': self.adapter.trust_score,
            'active_agents': kernel_status['active_agents'],
            'metrics': kernel_status['metrics'],
            'restart_attempts': self.restart_attempts,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None
        }


# Orchestrator registration helper
async def register_librarian_in_orchestrator(
    orchestrator,
    registry=None,
    event_mesh=None,
    unified_logic=None
):
    """
    Helper function to register Librarian in the orchestrator.
    
    Usage in orchestrator setup:
    ```python
    from backend.kernels.orchestrator_integration import register_librarian_in_orchestrator
    
    # During orchestrator initialization
    await register_librarian_in_orchestrator(
        orchestrator,
        registry=table_registry,
        event_mesh=clarity_event_mesh,
        unified_logic=unified_logic_hub
    )
    ```
    """
    from backend.kernels.librarian_kernel import LibrarianKernel
    from backend.kernels.librarian_clarity_adapter import LibrarianClarityAdapter
    
    try:
        # Create kernel
        kernel = LibrarianKernel(
            registry=registry,
            event_bus=event_mesh
        )
        
        # Create clarity adapter
        adapter = LibrarianClarityAdapter(
            librarian_kernel=kernel,
            registry=registry,
            event_mesh=event_mesh,
            unified_logic=unified_logic
        )
        
        # Create orchestrator stage
        stage = LibrarianOrchestratorStage(adapter)
        
        # Register with orchestrator
        orchestrator.add_stage(stage)
        
        logger.info("Librarian Data Orchestrator registered in orchestrator")
        
        return stage
        
    except Exception as e:
        logger.error(f"Failed to register Librarian in orchestrator: {e}")
        raise


# Example orchestrator configuration
LIBRARIAN_STAGE_CONFIG = {
    'stage_id': 'data_orchestrator',
    'stage_name': 'Librarian Data Orchestrator',
    'stage_type': 'kernel',
    'auto_start': True,
    'critical': False,
    'health_check_interval': 30,
    'restart_on_failure': True,
    'max_restart_attempts': 3,
    'dependencies': [],  # Can run independently
    'capabilities': [
        'schema_inference',
        'file_ingestion',
        'trust_auditing',
        'flashcard_generation',
        'workspace_monitoring'
    ],
    'managed_subsystems': [
        'memory_tables',
        'trusted_sources',
        'upload_manifest',
        'sub_agent_fleet'
    ]
}
