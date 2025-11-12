# -*- coding: utf-8 -*-
"""
Base Component - Clarity Framework Class 1
Standardized component interface for all Grace subsystems
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class ComponentStatus(Enum):
    """Standardized component status states"""
    CREATED = "created"
    ACTIVATING = "activating"
    ACTIVE = "active"
    PAUSED = "paused"
    DEACTIVATING = "deactivating"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class BaseComponent(ABC):
    """
    Base class for all Grace components.
    Enforces consistent lifecycle, configuration, and status tracking.
    
    All Grace subsystems should inherit from this class.
    """
    
    # Auto-generated identity
    component_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    component_type: str = field(default="base_component")
    
    # Lifecycle tracking
    status: ComponentStatus = field(default=ComponentStatus.CREATED)
    created_at: datetime = field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    async def activate(self) -> bool:
        """
        Activate this component.
        Returns True if activation succeeded, False otherwise.
        """
        pass
    
    @abstractmethod
    async def deactivate(self) -> bool:
        """
        Deactivate/cleanup this component.
        Returns True if deactivation succeeded, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current component status.
        Returns dict with status, health, and metrics.
        """
        pass
    
    def set_status(self, status: ComponentStatus, error_message: Optional[str] = None):
        """Update component status"""
        self.status = status
        if error_message:
            self.error_message = error_message
    
    def update_config(self, config: Dict[str, Any]):
        """Update component configuration"""
        self.config.update(config)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to component"""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dict"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "error_message": self.error_message,
            "config": self.config,
            "metadata": self.metadata
        }
