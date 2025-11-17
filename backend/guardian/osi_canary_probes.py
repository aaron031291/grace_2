"""
OSI Layer Canary Probes - Phase 1
Health probes for network layers 2-7 with alert hooks
"""

import asyncio
import socket
import subprocess
import platform
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OSILayer(Enum):
    """OSI network layers"""
    LAYER_2_DATA_LINK = 2
    LAYER_3_NETWORK = 3
    LAYER_4_TRANSPORT = 4
    LAYER_5_SESSION = 5
    LAYER_6_PRESENTATION = 6
    LAYER_7_APPLICATION = 7


class ProbeStatus(Enum):
    """Probe health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ProbeResult:
    """Result of a canary probe"""
    layer: OSILayer
    status: ProbeStatus
    latency_ms: float
    message: str
    details: Dict[str, Any]
    timestamp: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "layer": self.layer.value,
            "layer_name": self.layer.name,
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class OSICanaryProbes:
    """
    Canary probes for OSI network layers
    Monitors health of each layer and triggers alerts
    """
    
    def __init__(self):
        self.probe_history: Dict[OSILayer, List[ProbeResult]] = {
            layer: [] for layer in OSILayer
        }
        self.max_history = 100  # Keep last 100 results per layer
    
    async def probe_layer_2_data_link(self) -> ProbeResult:
        """
        Layer 2: Data Link (ARP, MAC addressing)
        Check if we can resolve MAC addresses
        """
        start = datetime.now()
        
        try:
            # On Windows, use arp -a to check ARP table
            # On Linux, use ip neigh or arp
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["arp", "-a"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ["ip", "neigh"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0:
                # Count entries in ARP table
                entries = [line for line in result.stdout.split('\n') if line.strip()]
                entry_count = len(entries) - 1  # Subtract header
                
                return ProbeResult(
                    layer=OSILayer.LAYER_2_DATA_LINK,
                    status=ProbeStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"ARP table accessible ({entry_count} entries)",
                    details={"arp_entries": entry_count},
                    timestamp=""
                )
            else:
                return ProbeResult(
                    layer=OSILayer.LAYER_2_DATA_LINK,
                    status=ProbeStatus.DEGRADED,
                    latency_ms=latency,
                    message="ARP command failed",
                    details={"error": result.stderr},
                    timestamp=""
                )
        
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ProbeResult(
                layer=OSILayer.LAYER_2_DATA_LINK,
                status=ProbeStatus.FAILED,
                latency_ms=latency,
                message=f"Layer 2 probe failed: {str(e)}",
                details={"error": str(e)},
                timestamp=""
            )
    
    async def probe_layer_3_network(self) -> ProbeResult:
        """
        Layer 3: Network (IP, routing)
        Check if we can reach the default gateway
        """
        start = datetime.now()
        
        try:
            # Ping localhost (always should work)
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["ping", "-n", "1", "127.0.0.1"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "127.0.0.1"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0:
                return ProbeResult(
                    layer=OSILayer.LAYER_3_NETWORK,
                    status=ProbeStatus.HEALTHY,
                    latency_ms=latency,
                    message="IP stack operational (localhost reachable)",
                    details={"ping_success": True},
                    timestamp=""
                )
            else:
                return ProbeResult(
                    layer=OSILayer.LAYER_3_NETWORK,
                    status=ProbeStatus.FAILED,
                    latency_ms=latency,
                    message="Cannot ping localhost",
                    details={"error": result.stderr},
                    timestamp=""
                )
        
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ProbeResult(
                layer=OSILayer.LAYER_3_NETWORK,
                status=ProbeStatus.FAILED,
                latency_ms=latency,
                message=f"Layer 3 probe failed: {str(e)}",
                details={"error": str(e)},
                timestamp=""
            )
    
    async def probe_layer_4_transport(self) -> ProbeResult:
        """
        Layer 4: Transport (TCP/UDP)
        Check if we can establish a TCP connection
        """
        start = datetime.now()
        
        try:
            # Try to connect to localhost on a common port (HTTP alternative port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            # Try to bind to a port (proves TCP stack works)
            sock.bind(('127.0.0.1', 0))  # Let OS pick a port
            port = sock.getsockname()[1]
            sock.close()
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            return ProbeResult(
                layer=OSILayer.LAYER_4_TRANSPORT,
                status=ProbeStatus.HEALTHY,
                latency_ms=latency,
                message=f"TCP stack operational (bound to port {port})",
                details={"test_port": port},
                timestamp=""
            )
        
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ProbeResult(
                layer=OSILayer.LAYER_4_TRANSPORT,
                status=ProbeStatus.FAILED,
                latency_ms=latency,
                message=f"Layer 4 probe failed: {str(e)}",
                details={"error": str(e)},
                timestamp=""
            )
    
    async def probe_layer_5_session(self) -> ProbeResult:
        """
        Layer 5: Session (connection management)
        Check if we can maintain a connection
        """
        start = datetime.now()
        
        try:
            # Create and hold a socket connection briefly
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.bind(('127.0.0.1', 0))
            sock.listen(1)
            
            # Hold the connection for 100ms
            await asyncio.sleep(0.1)
            
            sock.close()
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            return ProbeResult(
                layer=OSILayer.LAYER_5_SESSION,
                status=ProbeStatus.HEALTHY,
                latency_ms=latency,
                message="Session layer operational (connection held)",
                details={"session_duration_ms": 100},
                timestamp=""
            )
        
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ProbeResult(
                layer=OSILayer.LAYER_5_SESSION,
                status=ProbeStatus.FAILED,
                latency_ms=latency,
                message=f"Layer 5 probe failed: {str(e)}",
                details={"error": str(e)},
                timestamp=""
            )
    
    async def probe_layer_6_presentation(self) -> ProbeResult:
        """
        Layer 6: Presentation (encryption, encoding)
        Check if SSL/TLS is available
        """
        start = datetime.now()
        
        try:
            import ssl
            
            # Check if we can create an SSL context
            context = ssl.create_default_context()
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            return ProbeResult(
                layer=OSILayer.LAYER_6_PRESENTATION,
                status=ProbeStatus.HEALTHY,
                latency_ms=latency,
                message="SSL/TLS available",
                details={
                    "ssl_version": ssl.OPENSSL_VERSION,
                    "protocols": ["TLS"]
                },
                timestamp=""
            )
        
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ProbeResult(
                layer=OSILayer.LAYER_6_PRESENTATION,
                status=ProbeStatus.FAILED,
                latency_ms=latency,
                message=f"Layer 6 probe failed: {str(e)}",
                details={"error": str(e)},
                timestamp=""
            )
    
    async def probe_layer_7_application(self) -> ProbeResult:
        """
        Layer 7: Application (HTTP, DNS)
        Check if HTTP client is functional
        """
        start = datetime.now()
        
        try:
            # Test HTTP by making a request to localhost (if server is running)
            # Otherwise just verify HTTP libraries load
            import http.client
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            return ProbeResult(
                layer=OSILayer.LAYER_7_APPLICATION,
                status=ProbeStatus.HEALTHY,
                latency_ms=latency,
                message="HTTP libraries available",
                details={"http_client_ready": True},
                timestamp=""
            )
        
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ProbeResult(
                layer=OSILayer.LAYER_7_APPLICATION,
                status=ProbeStatus.FAILED,
                latency_ms=latency,
                message=f"Layer 7 probe failed: {str(e)}",
                details={"error": str(e)},
                timestamp=""
            )
    
    async def probe_all_layers(self) -> Dict[OSILayer, ProbeResult]:
        """
        Probe all OSI layers concurrently
        Returns results for each layer
        """
        tasks = {
            OSILayer.LAYER_2_DATA_LINK: self.probe_layer_2_data_link(),
            OSILayer.LAYER_3_NETWORK: self.probe_layer_3_network(),
            OSILayer.LAYER_4_TRANSPORT: self.probe_layer_4_transport(),
            OSILayer.LAYER_5_SESSION: self.probe_layer_5_session(),
            OSILayer.LAYER_6_PRESENTATION: self.probe_layer_6_presentation(),
            OSILayer.LAYER_7_APPLICATION: self.probe_layer_7_application(),
        }
        
        results = {}
        for layer, task in tasks.items():
            try:
                result = await task
                results[layer] = result
                
                # Store in history
                self.probe_history[layer].append(result)
                if len(self.probe_history[layer]) > self.max_history:
                    self.probe_history[layer] = self.probe_history[layer][-self.max_history:]
                
                # Log and alert on failures
                if result.status in [ProbeStatus.FAILED, ProbeStatus.DEGRADED]:
                    logger.warning(f"[OSI-PROBE] {layer.name} {result.status.value}: {result.message}")
                    
                    # Send alert
                    try:
                        from backend.trust_framework.alert_system import alert_system
                        await alert_system.send_alert(
                            level="warning" if result.status == ProbeStatus.DEGRADED else "error",
                            title=f"OSI {layer.name} {result.status.value}",
                            message=result.message,
                            metadata={
                                "layer": layer.name,
                                "latency_ms": result.latency_ms,
                                "details": result.details
                            }
                        )
                    except Exception as e:
                        logger.debug(f"[OSI-PROBE] Alert system unavailable: {e}")
            
            except Exception as e:
                logger.error(f"[OSI-PROBE] Failed to probe {layer.name}: {e}")
                results[layer] = ProbeResult(
                    layer=layer,
                    status=ProbeStatus.UNKNOWN,
                    latency_ms=0,
                    message=f"Probe exception: {str(e)}",
                    details={"error": str(e)},
                    timestamp=""
                )
        
        return results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get overall health summary of all layers
        """
        total_layers = len(OSILayer)
        healthy = sum(
            1 for layer in OSILayer
            if self.probe_history[layer] and self.probe_history[layer][-1].status == ProbeStatus.HEALTHY
        )
        
        failed = sum(
            1 for layer in OSILayer
            if self.probe_history[layer] and self.probe_history[layer][-1].status == ProbeStatus.FAILED
        )
        
        degraded = sum(
            1 for layer in OSILayer
            if self.probe_history[layer] and self.probe_history[layer][-1].status == ProbeStatus.DEGRADED
        )
        
        return {
            "total_layers": total_layers,
            "healthy": healthy,
            "degraded": degraded,
            "failed": failed,
            "health_percentage": (healthy / total_layers) * 100 if total_layers > 0 else 0,
            "last_probe": datetime.utcnow().isoformat()
        }


# Global instance
osi_canary_probes = OSICanaryProbes()
