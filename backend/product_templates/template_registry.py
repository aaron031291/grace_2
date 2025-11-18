"""
Template Registry - Built-in product templates
"""

from typing import Dict, List
from .models import ProductTemplate, TemplateCategory, TemplateFeature, TemplateComponent


class TemplateRegistry:
    """Registry of built-in product templates"""
    
    def __init__(self):
        self.templates: Dict[str, ProductTemplate] = {}
        self._register_builtin_templates()
    
    def _register_builtin_templates(self):
        """Register all built-in templates"""
        
        self.templates["website-landing"] = ProductTemplate(
            template_id="website-landing",
            name="Website & Landing Page",
            description="Professional website with landing page, blog, and contact forms",
            category=TemplateCategory.WEBSITE,
            features=[
                TemplateFeature(name="Landing Page", description="Hero section, features, testimonials, CTA"),
                TemplateFeature(name="Blog", description="Content management system for blog posts"),
                TemplateFeature(name="Contact Forms", description="Contact and lead capture forms"),
                TemplateFeature(name="SEO Optimization", description="Meta tags, sitemaps, structured data"),
                TemplateFeature(name="Analytics", description="Google Analytics and tracking"),
            ],
            components=[
                TemplateComponent(name="frontend", type="service", image="node:20-alpine", config={"framework": "React"}),
                TemplateComponent(name="cms", type="service", image="strapi/strapi", config={"database": "postgres"}),
                TemplateComponent(name="database", type="database", image="postgres:16-alpine"),
            ],
            tech_stack={"frontend": "React + Vite", "cms": "Strapi", "database": "PostgreSQL", "hosting": "Vercel"},
            estimated_setup_time=20,
            tags=["website", "landing-page", "blog", "seo"],
        )
        
        self.templates["sales-funnel"] = ProductTemplate(
            template_id="sales-funnel",
            name="Sales Funnel",
            description="Complete sales funnel with lead capture, email automation, and conversion tracking",
            category=TemplateCategory.SALES,
            features=[
                TemplateFeature(name="Lead Capture", description="Forms and popups for lead generation"),
                TemplateFeature(name="Email Automation", description="Drip campaigns and sequences"),
                TemplateFeature(name="Payment Processing", description="Stripe integration for payments"),
                TemplateFeature(name="Conversion Tracking", description="Analytics and funnel metrics"),
                TemplateFeature(name="A/B Testing", description="Test different funnel variations"),
            ],
            components=[
                TemplateComponent(name="frontend", type="service", image="node:20-alpine"),
                TemplateComponent(name="backend", type="service", image="python:3.12-slim", config={"framework": "FastAPI"}),
                TemplateComponent(name="email-service", type="service", image="mailhog/mailhog"),
                TemplateComponent(name="database", type="database", image="postgres:16-alpine"),
                TemplateComponent(name="redis", type="cache", image="redis:7-alpine"),
            ],
            tech_stack={"frontend": "React", "backend": "FastAPI", "email": "SendGrid", "payments": "Stripe", "database": "PostgreSQL"},
            estimated_setup_time=30,
            tags=["sales", "funnel", "email", "payments", "conversion"],
        )
        
        self.templates["crm-system"] = ProductTemplate(
            template_id="crm-system",
            name="CRM System",
            description="Customer relationship management with contacts, deals, and pipeline tracking",
            category=TemplateCategory.CRM,
            features=[
                TemplateFeature(name="Contact Management", description="Store and organize customer data"),
                TemplateFeature(name="Deal Pipeline", description="Track deals through sales stages"),
                TemplateFeature(name="Activity Tracking", description="Log calls, emails, meetings"),
                TemplateFeature(name="Reporting", description="Sales reports and dashboards"),
                TemplateFeature(name="Email Integration", description="Sync with email providers"),
            ],
            components=[
                TemplateComponent(name="frontend", type="service", image="node:20-alpine"),
                TemplateComponent(name="backend", type="service", image="python:3.12-slim"),
                TemplateComponent(name="database", type="database", image="postgres:16-alpine"),
                TemplateComponent(name="redis", type="cache", image="redis:7-alpine"),
                TemplateComponent(name="worker", type="service", image="python:3.12-slim", dependencies=["backend", "redis"]),
            ],
            tech_stack={"frontend": "React + TypeScript", "backend": "FastAPI", "database": "PostgreSQL", "cache": "Redis", "queue": "Celery"},
            estimated_setup_time=35,
            tags=["crm", "sales", "contacts", "pipeline", "reporting"],
        )
        
        self.templates["consultancy-platform"] = ProductTemplate(
            template_id="consultancy-platform",
            name="Consultancy Platform",
            description="Professional services platform with booking, invoicing, and client portal",
            category=TemplateCategory.CONSULTANCY,
            features=[
                TemplateFeature(name="Booking System", description="Schedule consultations and meetings"),
                TemplateFeature(name="Client Portal", description="Secure area for clients to view projects"),
                TemplateFeature(name="Invoicing", description="Generate and send invoices"),
                TemplateFeature(name="Time Tracking", description="Track billable hours"),
                TemplateFeature(name="Document Sharing", description="Share files securely with clients"),
            ],
            components=[
                TemplateComponent(name="frontend", type="service", image="node:20-alpine"),
                TemplateComponent(name="backend", type="service", image="python:3.12-slim"),
                TemplateComponent(name="database", type="database", image="postgres:16-alpine"),
                TemplateComponent(name="storage", type="storage", config={"provider": "S3"}),
            ],
            tech_stack={"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL", "storage": "S3", "calendar": "Cal.com"},
            estimated_setup_time=30,
            tags=["consultancy", "booking", "invoicing", "client-portal", "time-tracking"],
        )
        
        self.templates["ai-dev-tools"] = ProductTemplate(
            template_id="ai-dev-tools",
            name="AI Developer Tools",
            description="AI-powered developer tools with code generation, analysis, and documentation",
            category=TemplateCategory.AI_TOOLS,
            features=[
                TemplateFeature(name="Code Generation", description="Generate code from natural language"),
                TemplateFeature(name="Code Analysis", description="Analyze code quality and security"),
                TemplateFeature(name="Documentation", description="Auto-generate documentation"),
                TemplateFeature(name="API Playground", description="Test and explore APIs"),
                TemplateFeature(name="Usage Analytics", description="Track API usage and costs"),
            ],
            components=[
                TemplateComponent(name="frontend", type="service", image="node:20-alpine"),
                TemplateComponent(name="backend", type="service", image="python:3.12-slim"),
                TemplateComponent(name="ai-service", type="service", image="python:3.12-slim", config={"models": ["gpt-4", "claude-3"]}),
                TemplateComponent(name="database", type="database", image="postgres:16-alpine"),
                TemplateComponent(name="redis", type="cache", image="redis:7-alpine"),
            ],
            tech_stack={"frontend": "React + Monaco Editor", "backend": "FastAPI", "ai": "OpenAI + Anthropic", "database": "PostgreSQL"},
            estimated_setup_time=25,
            tags=["ai", "developer-tools", "code-generation", "api", "documentation"],
        )
        
        self.templates["teaching-platform"] = ProductTemplate(
            template_id="teaching-platform",
            name="Teaching Platform",
            description="Online learning platform with courses, quizzes, and student management",
            category=TemplateCategory.TEACHING,
            features=[
                TemplateFeature(name="Course Builder", description="Create and organize course content"),
                TemplateFeature(name="Video Hosting", description="Upload and stream video lessons"),
                TemplateFeature(name="Quizzes & Assignments", description="Create assessments and grade submissions"),
                TemplateFeature(name="Student Dashboard", description="Track progress and certificates"),
                TemplateFeature(name="Discussion Forums", description="Community discussions and Q&A"),
            ],
            components=[
                TemplateComponent(name="frontend", type="service", image="node:20-alpine"),
                TemplateComponent(name="backend", type="service", image="python:3.12-slim"),
                TemplateComponent(name="database", type="database", image="postgres:16-alpine"),
                TemplateComponent(name="video-service", type="service", config={"provider": "Mux"}),
                TemplateComponent(name="storage", type="storage", config={"provider": "S3"}),
            ],
            tech_stack={"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL", "video": "Mux", "storage": "S3"},
            estimated_setup_time=35,
            tags=["teaching", "education", "courses", "video", "quizzes"],
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
    
    def search_templates(self, query: str) -> List[ProductTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []
        for template in self.templates.values():
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag for tag in template.tags)):
                results.append(template)
        return results
