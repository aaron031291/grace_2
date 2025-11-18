"""
OSI Layer Canary Probes - Phase 1
Per-layer health monitoring
"""
import asyncio
from typing import Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class OSILayer(Enum):
    PHYSICAL = 1
    DATA_LINK = 2
    NETWORK = 3
    TRANSPORT = 4
    SESSION = 5
    PRESENTATION = 6
    APPLICATION = 7

class ProbeStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class ProbeResult:
    status: ProbeStatus
    latency_ms: float
    details: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class OSICanaryProbes:
    def __init__(self):
        self.layer_probes = {
            OSILayer.PHYSICAL: "Physical Layer Check",
            OSILayer.DATA_LINK: "Data Link Check", 
            OSILayer.NETWORK: "Network Layer Check",
            OSILayer.TRANSPORT: "Transport Layer Check",
            OSILayer.SESSION: "Session Layer Check",
            OSILayer.PRESENTATION: "Presentation Layer Check",
            OSILayer.APPLICATION: "Application Layer Check"
        }
        self._last_results = {}
    
    async def probe_all_layers(self) -> Dict[OSILayer, ProbeResult]:
        """Run canary probes for all OSI layers"""
        results = {}
        
        for layer in OSILayer:
            result = await self._probe_layer(layer)
            results[layer] = result
            self._last_results[layer] = result
        
        return results
    
    async def _probe_layer(self, layer: OSILayer) -> ProbeResult:
        """Probe specific OSI layer"""
        # Simulate layer-specific checks
        await asyncio.sleep(0.01)  # Simulate probe time
        
        return ProbeResult(
            status=ProbeStatus.HEALTHY,
            latency_ms=5.2,
            details=f"Layer {layer.value} responding normally",
            timestamp=datetime.utcnow()
        )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary of all layers"""
        if not self._last_results:
            return {
                "healthy": 0,
                "degraded": 0,
                "failed": 0,
                "unknown": 7,
                "health_percentage": 0.0
            }
        
        status_counts = {
            "healthy": 0,
            "degraded": 0,
            "failed": 0,
            "unknown": 0
        }
        
        for result in self._last_results.values():
            status_counts[result.status.value] += 1
        
        total = len(self._last_results)
        health_percentage = (status_counts["healthy"] / total * 100) if total > 0 else 0
        
        return {
            **status_counts,
            "health_percentage": health_percentage
        }

# Global instance
osi_canary_probes = OSICanaryProbes()

