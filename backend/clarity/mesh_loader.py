# -*- coding: utf-8 -*-
"""
Trigger Mesh Loader - Load event routing from YAML configuration
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

from .event_bus import EventBus, get_event_bus


class TriggerMeshLoader:
    """Load and configure event bus from trigger_mesh.yaml"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "trigger_mesh.yaml"
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.event_bus = get_event_bus()
    
    def load(self) -> Dict[str, Any]:
        """Load the trigger mesh configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Trigger mesh config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        return self.config
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all event definitions"""
        return self.config.get('events', [])
    
    def get_routing_rules(self) -> Dict[str, Any]:
        """Get routing rules"""
        return self.config.get('routing_rules', {})
    
    def get_subscriber_groups(self) -> Dict[str, List[str]]:
        """Get subscriber groups"""
        return self.config.get('subscriber_groups', {})
    
    def get_priority_events(self) -> List[str]:
        """Get list of priority event types"""
        rules = self.get_routing_rules()
        return rules.get('priority_events', [])
    
    def get_audit_events(self) -> List[str]:
        """Get list of events that should be audited"""
        rules = self.get_routing_rules()
        return rules.get('audit_events', [])
    
    def get_alert_events(self) -> List[str]:
        """Get list of events that should trigger alerts"""
        rules = self.get_routing_rules()
        return rules.get('alert_events', [])
    
    def get_event_info(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific event type"""
        for event in self.get_events():
            if event.get('event_type') == event_type:
                return event
        return None
    
    def get_publishers_for_event(self, event_type: str) -> List[str]:
        """Get list of publishers for an event type"""
        event_info = self.get_event_info(event_type)
        if event_info:
            return event_info.get('publishers', [])
        return []
    
    def get_subscribers_for_event(self, event_type: str) -> List[str]:
        """Get list of subscribers for an event type"""
        event_info = self.get_event_info(event_type)
        if event_info:
            return event_info.get('subscribers', [])
        return []
    
    def validate_event(self, event_type: str, publisher: str) -> bool:
        """Validate that a publisher is authorized for an event type"""
        event_info = self.get_event_info(event_type)
        if not event_info:
            # Unknown event type - allow but log warning
            return True
        
        publishers = event_info.get('publishers', [])
        if 'any_component' in publishers:
            return True
        
        return publisher in publishers
    
    def get_documentation(self) -> str:
        """Generate documentation for all events"""
        docs = ["# Grace Event Mesh - Event Catalog\n"]
        
        for event in self.get_events():
            docs.append(f"\n## {event.get('event_type')}")
            docs.append(f"{event.get('description', 'No description')}")
            docs.append(f"\n**Publishers:** {', '.join(event.get('publishers', []))}")
            docs.append(f"**Subscribers:** {', '.join(event.get('subscribers', []))}\n")
        
        return "\n".join(docs)


# Global loader instance
_mesh_loader: Optional[TriggerMeshLoader] = None


def get_mesh_loader() -> TriggerMeshLoader:
    """Get the global trigger mesh loader"""
    global _mesh_loader
    if _mesh_loader is None:
        _mesh_loader = TriggerMeshLoader()
        try:
            _mesh_loader.load()
        except FileNotFoundError:
            # Config doesn't exist yet - create empty loader
            pass
    return _mesh_loader
