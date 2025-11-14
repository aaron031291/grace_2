"""
Kernel Registry - Central Hub for All Grace Kernels
Integrates both domain kernels and clarity framework kernels
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# Import all working kernels
from .core_kernel import core_kernel
from .governance_kernel import governance_kernel
from .memory_kernel import memory_kernel
from .code_kernel import code_kernel
from .intelligence_kernel import intelligence_kernel
from .infrastructure_kernel import infrastructure_kernel
from .federation_kernel import federation_kernel
from .verification_kernel import verification_kernel
from .self_healing_kernel import self_healing_kernel
from .librarian_kernel import librarian_kernel
from .librarian_kernel_enhanced import enhanced_librarian_kernel

# Import clarity framework kernels
from .all_kernels_clarity import (
    ClarityMemoryKernel,
    ClarityCoreKernel,
    ClarityCodeKernel,
    ClarityGovernanceKernel,
    ClarityVerificationKernel,
    ClarityIntelligenceKernel,
    ClarityInfrastructureKernel,
    ClarityFederationKernel,
    ClarityMLKernel
)


class KernelRegistry:
    """
    Central registry for all Grace kernels with Clarity integration
    
    Features:
    - Dual-mode operation: Domain kernels + Clarity kernels
    - Automatic routing based on request type
    - Health monitoring across all kernels
    - Unified interface for kernel communication
    """
    
    def __init__(self):
        self.domain_kernels: Dict[str, Any] = {}
        self.clarity_kernels: Dict[str, Any] = {}
        self.kernel_health: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all kernels in the registry"""
        if self._initialized:
            return
        
        # Register domain kernels
        self.domain_kernels = {
            "core": core_kernel,
            "governance": governance_kernel,
            "memory": memory_kernel,
            "code": code_kernel,
            "intelligence": intelligence_kernel,
            "infrastructure": infrastructure_kernel,
            "federation": federation_kernel,
            "verification": verification_kernel,
            "self_healing": self_healing_kernel,
            "librarian": librarian_kernel,
            "librarian_enhanced": enhanced_librarian_kernel
        }
        
        # Initialize clarity kernels
        self.clarity_kernels = {
            "clarity_memory": ClarityMemoryKernel(),
            "clarity_core": ClarityCoreKernel(),
            "clarity_code": ClarityCodeKernel(),
            "clarity_governance": ClarityGovernanceKernel(),
            "clarity_verification": ClarityVerificationKernel(),
            "clarity_intelligence": ClarityIntelligenceKernel(),
            "clarity_infrastructure": ClarityInfrastructureKernel(),
            "clarity_federation": ClarityFederationKernel(),
            "clarity_ml": ClarityMLKernel()
        }
        
        # Initialize clarity kernels
        for name, kernel in self.clarity_kernels.items():
            try:
                await kernel.start()
                self.kernel_health[name] = {
                    "status": "running",
                    "started_at": datetime.utcnow().isoformat(),
                    "framework": "clarity"
                }
            except Exception as e:
                self.kernel_health[name] = {
                    "status": "error",
                    "error": str(e),
                    "framework": "clarity"
                }
        
        # Track domain kernels
        for name, kernel in self.domain_kernels.items():
            self.kernel_health[name] = {
                "status": "available",
                "framework": "domain"
            }
        
        self._initialized = True
        print(f"[OK] Kernel Registry initialized: {len(self.domain_kernels)} domain + {len(self.clarity_kernels)} clarity kernels")
    
    async def route_request(
        self,
        intent: str,
        context: Dict[str, Any],
        prefer_clarity: bool = True
    ) -> Dict[str, Any]:
        """
        Route request to appropriate kernel
        
        Args:
            intent: User intent/request
            context: Request context
            prefer_clarity: Whether to prefer clarity kernels over domain kernels
            
        Returns:
            Processed response from kernel
        """
        # Determine domain from intent
        domain = self._classify_domain(intent)
        
        if prefer_clarity and f"clarity_{domain}" in self.clarity_kernels:
            # Use clarity framework kernel
            kernel = self.clarity_kernels[f"clarity_{domain}"]
            result = await kernel.process_request(intent, context)
            result["kernel_used"] = f"clarity_{domain}"
            result["framework"] = "clarity"
            return result
        elif domain in self.domain_kernels:
            # Use domain kernel
            kernel = self.domain_kernels[domain]
            # Domain kernels have different interface - adapt it
            result = {
                "kernel_used": domain,
                "framework": "domain",
                "data": {"intent": intent, "context": context}
            }
            return result
        else:
            return {
                "error": "No kernel found for domain",
                "domain": domain,
                "intent": intent
            }
    
    def _classify_domain(self, intent: str) -> str:
        """Classify intent into domain"""
        intent_lower = intent.lower()
        
        if any(kw in intent_lower for kw in ["memory", "knowledge", "remember", "store", "retrieve"]):
            return "memory"
        elif any(kw in intent_lower for kw in ["code", "generate", "debug", "refactor", "github"]):
            return "code"
        elif any(kw in intent_lower for kw in ["policy", "govern", "approve", "constitutional", "trust"]):
            return "governance"
        elif any(kw in intent_lower for kw in ["verify", "validate", "check", "audit"]):
            return "verification"
        elif any(kw in intent_lower for kw in ["intelligence", "learn", "train", "ml", "ai"]):
            return "intelligence"
        elif any(kw in intent_lower for kw in ["infrastructure", "system", "resource", "host"]):
            return "infrastructure"
        elif any(kw in intent_lower for kw in ["federation", "multi-agent", "coordinate"]):
            return "federation"
        else:
            return "core"
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all kernels"""
        return {
            "initialized": self._initialized,
            "total_kernels": len(self.domain_kernels) + len(self.clarity_kernels),
            "domain_kernels": len(self.domain_kernels),
            "clarity_kernels": len(self.clarity_kernels),
            "health": self.kernel_health,
            "domains": list(self.domain_kernels.keys()),
            "clarity_domains": list(self.clarity_kernels.keys())
        }
    
    def get_kernel(self, name: str) -> Optional[Any]:
        """Get kernel by name"""
        if name in self.domain_kernels:
            return self.domain_kernels[name]
        elif name in self.clarity_kernels:
            return self.clarity_kernels[name]
        return None


# Global registry instance
kernel_registry = KernelRegistry()
