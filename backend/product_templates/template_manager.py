"""
Template Manager - Instantiate and manage product templates
"""

import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any
from .models import ProductTemplate, TemplateInstance, TemplateInstanceStatus
from .template_registry import TemplateRegistry


class TemplateManager:
    """Manage template instances"""
    
    def __init__(self):
        self.registry = TemplateRegistry()
        self.instances: Dict[str, TemplateInstance] = {}
    
    def create_instance(
        self,
        template_id: str,
        tenant_id: str,
        name: str,
        description: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None,
    ) -> TemplateInstance:
        """Create a new instance from template"""
        template = self.registry.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        instance_id = f"inst_{secrets.token_urlsafe(16)}"
        
        instance = TemplateInstance(
            instance_id=instance_id,
            template_id=template_id,
            tenant_id=tenant_id,
            name=name,
            description=description or template.description,
            customizations=customizations or {},
            status=TemplateInstanceStatus.CREATING,
        )
        
        self.instances[instance_id] = instance
        
        self._deploy_instance(instance, template)
        
        return instance
    
    def _deploy_instance(self, instance: TemplateInstance, template: ProductTemplate):
        """Deploy instance (simulated)"""
        
        instance.status = TemplateInstanceStatus.ACTIVE
        instance.deployed_at = datetime.utcnow()
        instance.deployment_url = f"https://{instance.instance_id}.grace-saas.com"
        instance.admin_url = f"https://{instance.instance_id}.grace-saas.com/admin"
        instance.api_url = f"https://api.{instance.instance_id}.grace-saas.com"
        
        instance.resources = {
            "cpu": "2 cores",
            "memory": "4GB",
            "storage": "20GB",
            "bandwidth": "100GB/month",
        }
        
        instance.metrics = {
            "uptime_percent": 100.0,
            "requests_total": 0,
            "requests_per_second": 0.0,
            "error_rate": 0.0,
            "response_time_ms": 0.0,
        }
    
    def get_instance(self, instance_id: str) -> Optional[TemplateInstance]:
        """Get instance by ID"""
        return self.instances.get(instance_id)
    
    def list_instances(
        self,
        tenant_id: Optional[str] = None,
        template_id: Optional[str] = None,
        status: Optional[TemplateInstanceStatus] = None,
    ) -> List[TemplateInstance]:
        """List instances with optional filters"""
        instances = list(self.instances.values())
        
        if tenant_id:
            instances = [i for i in instances if i.tenant_id == tenant_id]
        if template_id:
            instances = [i for i in instances if i.template_id == template_id]
        if status:
            instances = [i for i in instances if i.status == status]
        
        return instances
    
    def update_instance(
        self,
        instance_id: str,
        customizations: Optional[Dict[str, Any]] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> TemplateInstance:
        """Update instance configuration"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance not found: {instance_id}")
        
        if customizations:
            instance.customizations.update(customizations)
        if resources:
            instance.resources.update(resources)
        
        instance.updated_at = datetime.utcnow()
        return instance
    
    def suspend_instance(self, instance_id: str) -> TemplateInstance:
        """Suspend instance"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance not found: {instance_id}")
        
        instance.status = TemplateInstanceStatus.SUSPENDED
        instance.updated_at = datetime.utcnow()
        return instance
    
    def activate_instance(self, instance_id: str) -> TemplateInstance:
        """Activate suspended instance"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance not found: {instance_id}")
        
        instance.status = TemplateInstanceStatus.ACTIVE
        instance.updated_at = datetime.utcnow()
        return instance
    
    def delete_instance(self, instance_id: str) -> bool:
        """Delete instance"""
        instance = self.get_instance(instance_id)
        if not instance:
            return False
        
        instance.status = TemplateInstanceStatus.DELETED
        instance.updated_at = datetime.utcnow()
        return True
    
    def get_instance_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get instance metrics"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance not found: {instance_id}")
        
        return instance.metrics
    
    def update_instance_metrics(self, instance_id: str, metrics: Dict[str, Any]):
        """Update instance metrics"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance not found: {instance_id}")
        
        instance.metrics.update(metrics)
        instance.updated_at = datetime.utcnow()
