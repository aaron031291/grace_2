# -*- coding: utf-8 -*-
"""
Component Manifest - Clarity Framework Class 4
Component registration and lifecycle tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from .base_component import BaseComponent, ComponentStatus


class TrustLevel(Enum):
    """Component trust levels"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4


@dataclass
class ComponentRegistration:
    """Registration record for a component"""
    component_id: str
    component_type: str
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    active: bool = False
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = None
    role_tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "trust_level": self.trust_level.value,
            "active": self.active,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "role_tags": self.role_tags,
            "metadata": self.metadata
        }


class GraceComponentManifest:
    """
    Central registry for all Grace components.
    Tracks activation state, trust levels, and roles.
    """
    
    def __init__(self):
        self._registry: Dict[str, ComponentRegistration] = {}
    
    def register(
        self,
        component: BaseComponent,
        trust_level: TrustLevel = TrustLevel.UNTRUSTED,
        role_tags: Optional[List[str]] = None
    ) -> ComponentRegistration:
        """Register a component"""
        registration = ComponentRegistration(
            component_id=component.component_id,
            component_type=component.component_type,
            trust_level=trust_level,
            active=component.status == ComponentStatus.ACTIVE,
            role_tags=role_tags or []
        )
        self._registry[component.component_id] = registration
        return registration
    
    def unregister(self, component_id: str):
        """Unregister a component"""
        if component_id in self._registry:
            del self._registry[component_id]
    
    def update_status(self, component_id: str, active: bool):
        """Update component active status"""
        if component_id in self._registry:
            self._registry[component_id].active = active
            self._registry[component_id].last_heartbeat = datetime.utcnow()
    
    def update_trust(self, component_id: str, trust_level: TrustLevel):
        """Update component trust level"""
        if component_id in self._registry:
            self._registry[component_id].trust_level = trust_level
    
    def get_registration(self, component_id: str) -> Optional[ComponentRegistration]:
        """Get component registration"""
        return self._registry.get(component_id)
    
    def get_active_components(self) -> List[ComponentRegistration]:
        """Get all active components"""
        return [reg for reg in self._registry.values() if reg.active]
    
    def get_components_by_role(self, role_tag: str) -> List[ComponentRegistration]:
        """Get components by role tag"""
        return [reg for reg in self._registry.values() if role_tag in reg.role_tags]
    
    def get_components_by_trust(self, min_trust: TrustLevel) -> List[ComponentRegistration]:
        """Get components meeting minimum trust level"""
        return [reg for reg in self._registry.values() if reg.trust_level.value >= min_trust.value]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manifest statistics"""
        return {
            "total_components": len(self._registry),
            "active_components": len(self.get_active_components()),
            "trust_distribution": {
                level.name: len([r for r in self._registry.values() if r.trust_level == level])
                for level in TrustLevel
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire manifest"""
        return {
            "components": [reg.to_dict() for reg in self._registry.values()],
            "stats": self.get_stats()
        }


# Global manifest instance
_manifest = GraceComponentManifest()


def get_manifest() -> GraceComponentManifest:
    """Get the global component manifest"""
    return _manifest
