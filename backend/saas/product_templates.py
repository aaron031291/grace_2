"""
SaaS Product Templates
Template system for rapid SaaS product instantiation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TemplateCategory(str, Enum):
    """Product template categories"""
    WEBSITE = "website"
    SALES_FUNNEL = "sales_funnel"
    CRM = "crm"
    CONSULTANCY = "consultancy"
    DEV_TOOLS = "dev_tools"
    TEACHING = "teaching"
    MARKETPLACE = "marketplace"

@dataclass
class ProductTemplate:
    """SaaS product template"""
    template_id: str
    name: str
    category: TemplateCategory
    description: str
    tech_stack: List[str]
    features: List[str]
    estimated_setup_minutes: int
    components: Dict[str, Any]

class ProductTemplateRegistry:
    """Registry of SaaS product templates"""
    
    def __init__(self):
        self.templates: Dict[str, ProductTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize built-in templates"""
        
        # Website/Landing Page
        self.templates["landing_page"] = ProductTemplate(
            template_id="landing_page",
            name="Landing Page Builder",
            category=TemplateCategory.WEBSITE,
            description="Modern landing page with analytics and lead capture",
            tech_stack=["FastAPI", "React", "PostgreSQL", "Stripe"],
            features=[
                "Responsive design",
                "Lead capture forms",
                "Analytics integration",
                "A/B testing",
                "Email capture",
                "Payment integration"
            ],
            estimated_setup_minutes=15,
            components={
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "auth": "JWT",
                    "endpoints": ["/leads", "/analytics", "/subscribe"]
                },
                "frontend": {
                    "framework": "React",
                    "styling": "TailwindCSS",
                    "forms": "React Hook Form"
                },
                "infrastructure": {
                    "hosting": "Docker",
                    "ci_cd": "GitHub Actions",
                    "monitoring": "Golden Signals"
                }
            }
        )
        
        # Sales Funnel
        self.templates["sales_funnel"] = ProductTemplate(
            template_id="sales_funnel",
            name="Sales Funnel System",
            category=TemplateCategory.SALES_FUNNEL,
            description="Complete sales funnel with email automation",
            tech_stack=["FastAPI", "React", "PostgreSQL", "SendGrid", "Stripe"],
            features=[
                "Multi-step funnel",
                "Email automation",
                "Payment processing",
                "Analytics dashboard",
                "A/B testing",
                "Conversion tracking"
            ],
            estimated_setup_minutes=25,
            components={
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "email": "SendGrid",
                    "payments": "Stripe",
                    "endpoints": ["/funnel", "/convert", "/track", "/webhooks"]
                },
                "frontend": {
                    "framework": "React",
                    "pages": ["landing", "pricing", "checkout", "thank-you"],
                    "analytics": "Google Analytics"
                },
                "automation": {
                    "email_sequences": 3,
                    "follow_up_triggers": 5,
                    "abandoned_cart": True
                }
            }
        )
        
        # CRM System
        self.templates["crm"] = ProductTemplate(
            template_id="crm",
            name="CRM System",
            category=TemplateCategory.CRM,
            description="Customer relationship management with pipeline tracking",
            tech_stack=["FastAPI", "React", "PostgreSQL", "Redis"],
            features=[
                "Contact management",
                "Deal pipeline",
                "Activity tracking",
                "Email integration",
                "Reporting dashboard",
                "Task management"
            ],
            estimated_setup_minutes=30,
            components={
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "endpoints": ["/contacts", "/deals", "/activities", "/reports"]
                },
                "frontend": {
                    "framework": "React",
                    "views": ["contacts", "pipeline", "calendar", "reports"],
                    "charts": "Recharts"
                }
            }
        )
        
        # AI Developer Tools
        self.templates["ai_dev_tools"] = ProductTemplate(
            template_id="ai_dev_tools",
            name="AI Developer Tools Platform",
            category=TemplateCategory.DEV_TOOLS,
            description="AI-powered development tools with API",
            tech_stack=["FastAPI", "React", "PostgreSQL", "OpenAI"],
            features=[
                "Code generation API",
                "Documentation generation",
                "Test generation",
                "Code review automation",
                "Usage analytics",
                "API key management"
            ],
            estimated_setup_minutes=20,
            components={
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "llm": "OpenAI API",
                    "endpoints": ["/generate", "/review", "/test", "/docs"]
                },
                "frontend": {
                    "framework": "React",
                    "editor": "Monaco Editor",
                    "syntax_highlighting": True
                },
                "api": {
                    "authentication": "API Keys",
                    "rate_limiting": "60 req/min",
                    "quota_management": True
                }
            }
        )
    
    def get_template(self, template_id: str) -> Optional[ProductTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[TemplateCategory] = None) -> List[ProductTemplate]:
        """List all templates, optionally filtered by category"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    async def instantiate_template(
        self,
        template_id: str,
        tenant_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Instantiate a product from template"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        instance_id = f"prod_{template_id}_{tenant_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Would actually create:
        # - Database schema
        # - API endpoints
        # - Frontend deployment
        # - CI/CD pipeline
        # - Monitoring
        
        return {
            "instance_id": instance_id,
            "template_id": template_id,
            "tenant_id": tenant_id,
            "status": "provisioning",
            "components": template.components,
            "estimated_completion_minutes": template.estimated_setup_minutes,
            "created_at": datetime.now().isoformat()
        }

# Global instance
_template_registry: Optional[ProductTemplateRegistry] = None

def get_template_registry() -> ProductTemplateRegistry:
    """Get global template registry"""
    global _template_registry
    if _template_registry is None:
        _template_registry = ProductTemplateRegistry()
    return _template_registry
