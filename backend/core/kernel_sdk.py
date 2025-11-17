"""
Kernel SDK
Lightweight interface for kernels to communicate with core

Provides simple methods that wrap message bus complexity
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .message_bus import message_bus, MessagePriority


class KernelSDK:
    """
    SDK for kernels to interact with core
    
    Usage in a kernel:
    ```python
    sdk = KernelSDK('my_kernel')
    
    # Register
    await sdk.register_component(
        capabilities=['ingest', 'summarize'],
        contracts={'latency_ms': {'max': 500}}
    )
    
    # Report status
    await sdk.report_status(
        health='healthy',
        metrics={'latency_ms': 350, 'items_processed': 100}
    )
    
    # Send heartbeat
    await sdk.heartbeat()
    ```
    """
    
    def __init__(self, kernel_name: str):
        self.kernel_name = kernel_name
        self.component_id = f"{kernel_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    async def register_component(
        self,
        capabilities: List[str],
        contracts: Dict[str, Any],
        component_type: str = 'kernel'
    ) -> str:
        """
        Register component with Clarity Kernel
        
        Args:
            capabilities: What this component can do
            contracts: What it promises (KPIs, etc.)
            component_type: Type of component
        
        Returns:
            Component ID
        """
        
        # Create registration message
        await message_bus.publish(
            source=self.kernel_name,
            topic='kernel.register',
            payload={
                'component_id': self.component_id,
                'component_name': self.kernel_name,
                'component_type': component_type,
                'capabilities': capabilities,
                'contracts': contracts
            },
            priority=MessagePriority.HIGH
        )
        
        return self.component_id
    
    async def report_status(
        self,
        health: str,
        metrics: Dict[str, Any]
    ):
        """
        Report status to Clarity Kernel
        
        Args:
            health: Health state (healthy, degraded, unhealthy)
            metrics: Performance metrics
        """
        
        await message_bus.publish(
            source=self.kernel_name,
            topic='kernel.status',
            payload={
                'component_id': self.component_id,
                'kernel_name': self.kernel_name,
                'health': health,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.NORMAL
        )
    
    async def heartbeat(self):
        """Send heartbeat to Clarity Kernel"""
        
        await message_bus.publish(
            source=self.kernel_name,
            topic='kernel.heartbeat',
            payload={
                'component_id': self.component_id,
                'kernel_name': self.kernel_name,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.LOW
        )
    
    async def subscribe_to_manifests(self) -> asyncio.Queue:
        """
        Subscribe to manifest updates
        
        Returns:
            Queue of manifest update messages
        """
        
        return await message_bus.subscribe(
            subscriber=self.kernel_name,
            topic='kernel.manifest.updated'
        )
    
    async def subscribe_to_trust_updates(self) -> asyncio.Queue:
        """
        Subscribe to trust score updates
        
        Returns:
            Queue of trust update messages
        """
        
        return await message_bus.subscribe(
            subscriber=self.kernel_name,
            topic='trust.score.updated'
        )
    
    async def get_my_manifest(self) -> Optional[Dict[str, Any]]:
        """
        Get this kernel's current manifest
        
        Returns:
            Manifest data or None
        """
        
        # Request manifest from Clarity Kernel
        await message_bus.publish(
            source=self.kernel_name,
            topic='kernel.manifest.request',
            payload={'component_id': self.component_id},
            priority=MessagePriority.NORMAL
        )
        
        # In production, would wait for response
        # For now, return None
        return None


# Helper function for easy kernel creation
async def create_kernel(
    name: str,
    capabilities: List[str],
    contracts: Dict[str, Any]
) -> KernelSDK:
    """
    Create and register a kernel
    
    Args:
        name: Kernel name
        capabilities: What it can do
        contracts: What it promises
    
    Returns:
        Configured SDK instance
    """
    
    sdk = KernelSDK(name)
    await sdk.register_component(capabilities, contracts)
    return sdk
