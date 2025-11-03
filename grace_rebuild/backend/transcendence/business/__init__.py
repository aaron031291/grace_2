"""Business Automation Module - AI Consulting Engine"""

from .models import Client, Lead, Project, Interaction, Invoice
from .ai_consulting_engine import AIConsultingEngine
from .client_pipeline import ClientPipeline
from .revenue_tracker import revenue_tracker

__all__ = [
    'Client', 'Lead', 'Project', 'Interaction', 'Invoice',
    'AIConsultingEngine', 'ClientPipeline', 'revenue_tracker'
]
