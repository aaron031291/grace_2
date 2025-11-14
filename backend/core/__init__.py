"""
Grace's Unbreakable Core - Layer 1
Direct, hardened communication between critical kernels only

Components:
- Message Bus (kernel-to-kernel communication)
- Control Plane (kernel orchestration)
- Immutable Log (audit trail)
- Boot Pipeline (structured startup)
- Clarity Framework (transparent decisions)
- Verification Framework (continuous validation)
- Secret Manager (credentials)
- Governance Engine (policy enforcement)

This layer runs ALWAYS, even if FastAPI crashes
All communication is direct, authenticated, and hardened
"""

from .message_bus import message_bus
from .control_plane import control_plane
from .immutable_log import immutable_log
from .boot_pipeline import boot_pipeline
from .clarity_framework import clarity_framework
from .verification_framework import verification_framework
from .clarity_kernel import clarity_kernel
from .unified_logic_integration import unified_logic_core
from .kernel_sdk import KernelSDK, create_kernel
from .boot_layer import boot_layer

__all__ = [
    'message_bus',
    'control_plane',
    'immutable_log',
    'boot_pipeline',
    'clarity_framework',
    'verification_framework',
    'clarity_kernel',
    'unified_logic_core',
    'KernelSDK',
    'create_kernel',
    'boot_layer'
]
