"""
Grace Training Storage System
Organizes all learned knowledge into categorized folders
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class GraceTrainingStorage:
    """Manages Grace's training data in organized folders"""
    
    def __init__(self, base_path: str = "grace_training"):
        self.base_path = Path(base_path)
        self.categories = {
            "web_scraping": "Web Scraped Knowledge",
            "github": "GitHub Code & Best Practices",
            "youtube": "Video Tutorials & Guides",
            "reddit": "Community Discussions",
            "api_discovery": "API Integrations",
            "code_patterns": "Code Patterns & Solutions",
            "errors_fixed": "Self-Healing History",
            "user_feedback": "User Interactions",
            "constitutional": "Constitutional Decisions",
            "governance": "Governance Approvals"
        }
        
        # Create base structure
        self._initialize_structure()
    
    def _initialize_structure(self):
        """Create folder structure"""
        print(f"[TRAINING-STORAGE] Initializing knowledge storage at {self.base_path.absolute()}")
        
        # Create base folder
        self.base_path.mkdir(exist_ok=True)
        
        # Create category folders
        for category_key, category_name in self.categories.items():
            category_path = self.base_path / category_key
            category_path.mkdir(exist_ok=True)
            
            # Create metadata file
            metadata_file = category_path / "_metadata.json"
            if not metadata_file.exists():
                metadata = {
                    "category": category_key,
                    "name": category_name,
                    "created_at": datetime.utcnow().isoformat(),
                    "total_items": 0,
                    "last_updated": datetime.utcnow().isoformat()
                }
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
        
        print(f"[TRAINING-STORAGE] Created {len(self.categories)} category folders")
    
    async def save_knowledge(
        self,
        category: str,
        item_id: str,
        content: Dict[str, Any],
        source: str,
        tags: List[str] = None
    ) -> str:
        """
        Save knowledge item to appropriate folder
        
        Args:
            category: Category key (e.g., 'web_scraping', 'github')
            item_id: Unique identifier for this item
            content: The knowledge content
            source: Source URL or identifier
            tags: Optional tags for organization
        
        Returns:
            File path where item was saved
        """
        
        # Validate category
        if category not in self.categories:
            logger.warning(f"[TRAINING-STORAGE] Unknown category '{category}', using 'user_feedback'")
            category = "user_feedback"
        
        category_path = self.base_path / category
        
        # Create subfolder by date
        today = datetime.utcnow().strftime("%Y-%m-%d")
        date_folder = category_path / today
        date_folder.mkdir(exist_ok=True)
        
        # Create item file
        safe_id = "".join(c for c in item_id if c.isalnum() or c in ('-', '_'))[:100]
        timestamp = datetime.utcnow().strftime("%H%M%S")
        filename = f"{timestamp}_{safe_id}.json"
        file_path = date_folder / filename
        
        # Prepare item data
        item_data = {
            "id": item_id,
            "category": category,
            "source": source,
            "tags": tags or [],
            "content": content,
            "saved_at": datetime.utcnow().isoformat(),
            "provenance": {
                "verified": content.get("verified", False),
                "trust_score": content.get("trust_score", 0.0),
                "governance_approved": content.get("governance_approved", False)
            }
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item_data, f, indent=2, ensure_ascii=False)
        
        # Update category metadata
        await self._update_category_metadata(category)
        
        # Log to immutable log
        await immutable_log.append(
            actor="training_storage",
            action="knowledge_saved",
            resource=str(file_path),
            subsystem="training_storage",
            payload={
                "category": category,
                "item_id": item_id,
                "source": source,
                "tags": tags
            },
            result="success"
        )
        
        logger.info(f"[TRAINING-STORAGE] Saved to {category}/{today}/{filename}")
        print(f"[TRAINING-STORAGE] Saved: {category}/{today}/{filename}")
        
        return str(file_path)
    
    async def _update_category_metadata(self, category: str):
        """Update category metadata with item count"""
        category_path = self.base_path / category
        metadata_file = category_path / "_metadata.json"
        
        # Count total items
        total_items = sum(1 for p in category_path.rglob("*.json") if p.name != "_metadata.json")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        metadata["total_items"] = total_items
        metadata["last_updated"] = datetime.utcnow().isoformat()
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    async def create_custom_subfolder(
        self,
        category: str,
        subfolder_name: str,
        description: str = ""
    ) -> str:
        """
        Create a custom subfolder within a category
        
        Args:
            category: Parent category
            subfolder_name: Name for subfolder
            description: Optional description
        
        Returns:
            Path to created subfolder
        """
        if category not in self.categories:
            raise ValueError(f"Unknown category: {category}")
        
        category_path = self.base_path / category
        subfolder_path = category_path / subfolder_name
        subfolder_path.mkdir(exist_ok=True)
        
        # Create metadata
        metadata = {
            "name": subfolder_name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "parent_category": category
        }
        
        metadata_file = subfolder_path / "_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"[TRAINING-STORAGE] Created subfolder: {category}/{subfolder_name}")
        print(f"[TRAINING-STORAGE] Created: {category}/{subfolder_name} - {description}")
        
        return str(subfolder_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            "base_path": str(self.base_path.absolute()),
            "categories": {}
        }
        
        for category_key in self.categories.keys():
            category_path = self.base_path / category_key
            metadata_file = category_path / "_metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    stats["categories"][category_key] = metadata
        
        return stats


# Global singleton
training_storage = GraceTrainingStorage()
