"""
Grace Memory Agent - Autonomous Memory Management
Allows Grace to create, organize, and manage her own knowledge repository
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import hashlib

from backend.clarity import BaseComponent, ComponentStatus, get_event_bus, Event, TrustLevel, get_manifest
from backend.core.unified_event_publisher import publish_event_obj
from backend.memory_file_service import get_memory_service
from backend.memory_fusion_service import get_memory_fusion_service


class PermissionLevel:
    """Permission levels for Grace's memory operations"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    RESTRICTED = "restricted"  # No access


class GraceMemoryAgent(BaseComponent):
    """
    Autonomous agent for Grace to manage her own memory
    Tracks all actions, organizes by category, syncs to Memory Fusion
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "grace_memory_agent"
        self.event_bus = get_event_bus()
        self.action_log: List[Dict] = []
        
        # Define category structure with permissions
        self.categories = {
            "research": {
                "path": "research",
                "description": "Research papers, studies, findings",
                "permission": PermissionLevel.ADMIN,
                "subcategories": ["papers", "notes", "datasets", "experiments"]
            },
            "learning": {
                "path": "learning",
                "description": "Training data, embeddings, model artifacts",
                "permission": PermissionLevel.ADMIN,
                "subcategories": ["training_data", "embeddings", "models", "fine_tuning"]
            },
            "code": {
                "path": "code",
                "description": "Source code, scripts, notebooks",
                "permission": PermissionLevel.WRITE,
                "subcategories": ["python", "javascript", "sql", "notebooks"]
            },
            "documentation": {
                "path": "documentation",
                "description": "Guides, manuals, API docs",
                "permission": PermissionLevel.WRITE,
                "subcategories": ["guides", "api", "tutorials", "references"]
            },
            "conversations": {
                "path": "conversations",
                "description": "Chat logs, insights, user interactions",
                "permission": PermissionLevel.ADMIN,
                "subcategories": ["chats", "insights", "feedback", "questions"]
            },
            "domain_knowledge": {
                "path": "domain_knowledge",
                "description": "Specialized knowledge by domain",
                "permission": PermissionLevel.ADMIN,
                "subcategories": ["engineering", "science", "business", "security", "ml"]
            },
            "configuration": {
                "path": "configuration",
                "description": "Config files, settings, environment",
                "permission": PermissionLevel.RESTRICTED,  # Special handling
                "subcategories": ["configs", "secrets", "env", "keys"]
            },
            "immutable_logs": {
                "path": "immutable_logs",
                "description": "Append-only logs, audit trails",
                "permission": PermissionLevel.WRITE,  # Write-only, no delete
                "subcategories": ["actions", "events", "decisions", "errors"]
            },
            "crypto": {
                "path": "crypto",
                "description": "Cryptographic keys, signatures, certificates",
                "permission": PermissionLevel.RESTRICTED,
                "subcategories": ["keys", "signatures", "certs", "vault"]
            },
            "insights": {
                "path": "insights",
                "description": "Grace's self-generated insights and observations",
                "permission": PermissionLevel.ADMIN,
                "subcategories": ["observations", "patterns", "contradictions", "hypotheses"]
            }
        }
    
    async def activate(self) -> bool:
        """Activate Grace's memory agent"""
        self.set_status(ComponentStatus.ACTIVATING)
        
        # Ensure all category folders exist
        await self._initialize_category_structure()
        
        # Register with Clarity manifest
        manifest = get_manifest()
        manifest.register(
            self,
            trust_level=TrustLevel.VERIFIED,
            role_tags=["memory", "autonomous", "learning"]
        )
        
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        await publish_event_obj(Event(
            event_type="grace.memory.agent.activated",
            source=self.component_id,
            payload={
                "categories": list(self.categories.keys()),
                "permissions": {k: v["permission"] for k, v in self.categories.items()}
            }
        ))
        
        return True
    
    async def _initialize_category_structure(self):
        """Create all category folders and subcategories"""
        memory_service = await get_memory_service()
        
        for category_id, config in self.categories.items():
            # Create main category folder
            category_path = config["path"]
            try:
                await memory_service.create_folder(category_path)
            except:
                pass  # May already exist
            
            # Create subcategories
            for subcat in config.get("subcategories", []):
                subcat_path = f"{category_path}/{subcat}"
                try:
                    await memory_service.create_folder(subcat_path)
                except:
                    pass
            
            # Create README in each category
            readme_path = f"{category_path}/README.md"
            readme_content = f"""# {category_id.replace('_', ' ').title()}

{config['description']}

**Permission Level:** {config['permission']}

## Subcategories
{chr(10).join(f'- `{sc}/` - {sc.replace("_", " ").title()}' for sc in config.get('subcategories', []))}

---
*Auto-generated by Grace Memory Agent*
*Last updated: {datetime.utcnow().isoformat()}*
"""
            try:
                await memory_service.save_file(readme_path, readme_content)
            except:
                pass
    
    async def check_permission(
        self, 
        category: str, 
        operation: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if Grace has permission for an operation
        Returns: (allowed, reason)
        """
        if category not in self.categories:
            return False, f"Unknown category: {category}"
        
        cat_config = self.categories[category]
        perm_level = cat_config["permission"]
        
        # Check operation against permission level
        if perm_level == PermissionLevel.RESTRICTED:
            # Restricted categories need special approval
            if operation == "read":
                return True, None  # Can read
            return False, f"Category '{category}' is restricted. Special approval required."
        
        elif perm_level == PermissionLevel.READ:
            if operation in ["read"]:
                return True, None
            return False, f"Only read access allowed for '{category}'"
        
        elif perm_level == PermissionLevel.WRITE:
            if operation in ["read", "write", "create"]:
                return True, None
            if operation == "delete" and category == "immutable_logs":
                return False, "Cannot delete from immutable logs"
            return False, f"Delete not allowed for '{category}'"
        
        elif perm_level == PermissionLevel.ADMIN:
            return True, None  # Full access
        
        return False, "Unknown permission level"
    
    async def create_file(
        self,
        category: str,
        subcategory: Optional[str],
        filename: str,
        content: str,
        metadata: Optional[Dict] = None,
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """
        Grace creates a new file in her memory
        """
        # Check permission
        allowed, reason = await self.check_permission(category, "create")
        if not allowed:
            return {"success": False, "error": reason}
        
        # Build path
        if subcategory:
            file_path = f"{self.categories[category]['path']}/{subcategory}/{filename}"
        else:
            file_path = f"{self.categories[category]['path']}/{filename}"
        
        # Save file
        memory_service = await get_memory_service()
        result = await memory_service.save_file(file_path, content, metadata)
        
        # Log action
        action = {
            "action": "create_file",
            "category": category,
            "subcategory": subcategory,
            "file": file_path,
            "timestamp": datetime.utcnow().isoformat(),
            "size": len(content),
            "auto_sync": auto_sync
        }
        await self._log_action(action)
        
        # Sync to Memory Fusion if requested
        if auto_sync:
            await self._sync_to_fusion(file_path, content, metadata)
        
        # Publish event
        await publish_event_obj(Event(
            event_type="grace.memory.file.created",
            source=self.component_id,
            payload={
                "category": category,
                "path": file_path,
                "size": len(content)
            }
        ))
        
        return {
            "success": True,
            "path": file_path,
            "size": result.get("size"),
            "synced": auto_sync
        }
    
    async def save_research(
        self,
        title: str,
        content: str,
        domain: str = "general",
        tags: List[str] = None,
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """Convenience method for Grace to save research"""
        
        filename = f"{title.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}.md"
        
        # Format as markdown
        formatted_content = f"""# {title}

**Domain:** {domain}
**Tags:** {', '.join(tags or [])}
**Created:** {datetime.utcnow().isoformat()}

---

{content}

---
*Saved by Grace Memory Agent*
"""
        
        metadata = {
            "type": "research",
            "domain": domain,
            "tags": tags or [],
            "created_by": "grace",
            "trust_level": "verified"
        }
        
        return await self.create_file(
            category="research",
            subcategory="notes",
            filename=filename,
            content=formatted_content,
            metadata=metadata,
            auto_sync=auto_sync
        )
    
    async def save_insight(
        self,
        insight: str,
        category_type: str = "observations",
        confidence: float = 0.8,
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """Grace saves her own insights and observations"""
        
        filename = f"insight_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        insight_data = {
            "insight": insight,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "category": category_type,
            "source": "autonomous_observation"
        }
        
        return await self.create_file(
            category="insights",
            subcategory=category_type,
            filename=filename,
            content=json.dumps(insight_data, indent=2),
            metadata={"type": "insight", "confidence": confidence},
            auto_sync=auto_sync
        )
    
    async def save_conversation(
        self,
        conversation_id: str,
        messages: List[Dict],
        metadata: Optional[Dict] = None,
        auto_sync: bool = False  # Don't auto-sync conversations
    ) -> Dict[str, Any]:
        """Save conversation for learning"""
        
        filename = f"conversation_{conversation_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        conv_data = {
            "conversation_id": conversation_id,
            "messages": messages,
            "message_count": len(messages),
            "saved_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        return await self.create_file(
            category="conversations",
            subcategory="chats",
            filename=filename,
            content=json.dumps(conv_data, indent=2),
            metadata={"type": "conversation", "message_count": len(messages)},
            auto_sync=auto_sync
        )
    
    async def save_training_data(
        self,
        dataset_name: str,
        data: Any,
        data_type: str = "embeddings",
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """Save training data for ML/DL"""
        
        filename = f"{dataset_name}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        if isinstance(data, (dict, list)):
            content = json.dumps(data, indent=2)
        else:
            content = str(data)
        
        return await self.create_file(
            category="learning",
            subcategory=data_type,
            filename=filename,
            content=content,
            metadata={"type": data_type, "dataset": dataset_name},
            auto_sync=auto_sync
        )
    
    async def log_immutable_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log immutable event (append-only)"""
        
        filename = f"{event_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        event_record = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": event_data,
            "hash": hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        }
        
        return await self.create_file(
            category="immutable_logs",
            subcategory="events",
            filename=filename,
            content=json.dumps(event_record, indent=2),
            metadata={"type": "immutable_log", "event": event_type},
            auto_sync=True  # Always sync immutable logs
        )
    
    async def update_file(
        self,
        file_path: str,
        new_content: str,
        reason: str = "",
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """Update existing file with audit trail"""
        
        # Determine category from path
        category = file_path.split('/')[0]
        
        # Check permission
        allowed, perm_reason = await self.check_permission(category, "write")
        if not allowed:
            return {"success": False, "error": perm_reason}
        
        # Update file
        memory_service = await get_memory_service()
        await memory_service.save_file(file_path, new_content)
        
        # Log action
        action = {
            "action": "update_file",
            "file": file_path,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "size": len(new_content)
        }
        await self._log_action(action)
        
        # Sync if requested
        if auto_sync:
            await self._sync_to_fusion(file_path, new_content)
        
        return {"success": True, "path": file_path, "synced": auto_sync}
    
    async def delete_file(
        self,
        file_path: str,
        reason: str = "",
        force: bool = False
    ) -> Dict[str, Any]:
        """Delete file with permission check"""
        
        category = file_path.split('/')[0]
        
        # Check permission
        allowed, perm_reason = await self.check_permission(category, "delete")
        if not allowed and not force:
            return {"success": False, "error": perm_reason}
        
        # Cannot delete from immutable logs
        if category == "immutable_logs" and not force:
            return {"success": False, "error": "Cannot delete immutable logs"}
        
        # Delete file
        memory_service = await get_memory_service()
        await memory_service.delete_file(file_path, recursive=False)
        
        # Log action
        action = {
            "action": "delete_file",
            "file": file_path,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self._log_action(action)
        
        return {"success": True, "path": file_path}
    
    async def organize_file(
        self,
        file_path: str,
        suggested_category: str,
        suggested_subcategory: str,
        auto_move: bool = False
    ) -> Dict[str, Any]:
        """
        Grace suggests organization for a file
        Can auto-move if auto_move=True
        """
        
        suggestion = {
            "current_path": file_path,
            "suggested_category": suggested_category,
            "suggested_subcategory": suggested_subcategory,
            "new_path": f"{self.categories[suggested_category]['path']}/{suggested_subcategory}/{Path(file_path).name}",
            "confidence": 0.85,  # Could be ML-based
            "reason": "Auto-categorized by Grace"
        }
        
        if auto_move:
            # Move the file
            memory_service = await get_memory_service()
            await memory_service.rename_file(file_path, suggestion["new_path"])
            suggestion["moved"] = True
        
        return suggestion
    
    async def _log_action(self, action: Dict[str, Any]):
        """Log Grace's action to action log"""
        self.action_log.append(action)
        
        # Also save to immutable logs
        await self.log_immutable_event("grace_action", action)
    
    async def _sync_to_fusion(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Sync file to Memory Fusion with governance checks"""
        
        try:
            # Get Memory Fusion service
            fusion_service = await get_memory_fusion_service()
            
            # Prepare for sync
            sync_data = {
                "path": file_path,
                "content": content,
                "metadata": metadata or {},
                "trust_level": "verified",
                "source": "grace_memory_agent",
                "synced_at": datetime.utcnow().isoformat()
            }
            
            # Sync to fusion
            result = await fusion_service.sync_memory(file_path, sync_data)
            
            # Publish event
            await publish_event_obj(Event(
                event_type="grace.memory.synced.fusion",
                source=self.component_id,
                payload={
                    "path": file_path,
                    "fusion_result": result
                }
            ))
            
        except Exception as e:
            print(f"Fusion sync failed for {file_path}: {e}")
    
    def get_action_log(
        self,
        limit: int = 100,
        action_type: Optional[str] = None
    ) -> List[Dict]:
        """Get Grace's action history"""
        
        logs = self.action_log[-limit:]
        
        if action_type:
            logs = [l for l in logs if l.get("action") == action_type]
        
        return logs
    
    def get_category_info(self, category: str) -> Optional[Dict]:
        """Get info about a category"""
        return self.categories.get(category)
    
    def list_categories(self) -> Dict[str, Dict]:
        """List all categories Grace can use"""
        return self.categories


# Global instance
_grace_memory_agent: Optional[GraceMemoryAgent] = None


async def get_grace_memory_agent() -> GraceMemoryAgent:
    """Get or create global Grace memory agent"""
    global _grace_memory_agent
    if _grace_memory_agent is None:
        _grace_memory_agent = GraceMemoryAgent()
        await _grace_memory_agent.activate()
    return _grace_memory_agent
