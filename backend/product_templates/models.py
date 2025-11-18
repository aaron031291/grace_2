"""
Product Template Models
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TemplateCategory(str, Enum):
    """Template categories"""
    WEBSITE = "website"
    SALES = "sales"
    CRM = "crm"
    CONSULTANCY = "consultancy"
    AI_TOOLS = "ai_tools"
    TEACHING = "teaching"


class TemplateFeature(BaseModel):
    """Template feature definition"""
    name: str
    description: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class TemplateComponent(BaseModel):
    """Template component (service, database, etc.)"""
    name: str
    type: str  # "service", "database", "storage", "queue", etc.
    image: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)


class ProductTemplate(BaseModel):
    """Product template definition"""
    template_id: str
    name: str
    description: str
    category: TemplateCategory
    version: str = "1.0.0"
    
    features: List[TemplateFeature] = Field(default_factory=list)
    
    components: List[TemplateComponent] = Field(default_factory=list)
    
    tech_stack: Dict[str, str] = Field(default_factory=dict)  # {"frontend": "React", "backend": "FastAPI", ...}
    
    deployment_config: Dict[str, Any] = Field(default_factory=dict)
    
    estimated_setup_time: int = 30
    
    author: str = "Grace"
    tags: List[str] = Field(default_factory=list)
    icon: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TemplateInstanceStatus(str, Enum):
    """Template instance status"""
    CREATING = "creating"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FAILED = "failed"
    DELETED = "deleted"


class TemplateInstance(BaseModel):
    """Instantiated product from template"""
    instance_id: str
    template_id: str
    tenant_id: str
    
    name: str
    description: Optional[str] = None
    
    customizations: Dict[str, Any] = Field(default_factory=dict)
    
    status: TemplateInstanceStatus = TemplateInstanceStatus.CREATING
    deployment_url: Optional[str] = None
    admin_url: Optional[str] = None
    api_url: Optional[str] = None
    
    resources: Dict[str, Any] = Field(default_factory=dict)  # {"cpu": "2", "memory": "4GB", ...}
    
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
