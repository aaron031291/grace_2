"""
ML API Integrator for Transcendence
Bridges discovered ML/AI APIs with Grace's Transcendence layer

NOTE: Grace uses her OWN internal LLM for reasoning/generation
External APIs are ONLY for:
- Research papers (Papers With Code, arXiv)
- Datasets (Kaggle, Hugging Face Datasets)
- Pre-trained models (TensorFlow Hub, Model Zoo)
- NOT for LLM generation (Grace does that herself)
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..models import async_session
from ..memory_verification_matrix import MemoryVerificationMatrix
from ..unified_logger import unified_logger
from .llm_provider_router import llm_router, grace_llm

logger = logging.getLogger(__name__)


class MLAPIIntegrator:
    """
    Integrates approved ML/AI APIs into Transcendence layer
    Uses Grace's INTERNAL LLM for generation
    External APIs for research/datasets only
    """
    
    def __init__(self):
        self.active_integrations = {}
        self.api_cache = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Initialize integrator"""
        
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        # Load approved integrations
        await self.load_approved_integrations()
        
        logger.info("[ML-API-INTEGRATOR] Started")
    
    async def stop(self):
        """Shutdown integrator"""
        
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("[ML-API-INTEGRATOR] Stopped")
    
    async def load_approved_integrations(self):
        """Load approved integrations from verification matrix"""
        
        try:
            async with async_session() as session:
                matrix = MemoryVerificationMatrix(session)
                approved = matrix.get_all_integrations(status='approved')
                
                for integration in approved:
                    self.active_integrations[integration['name']] = {
                        'url': integration['url'],
                        'auth_type': integration['auth_type'],
                        'capabilities': integration['capabilities'],
                        'use_cases': integration['use_cases'],
                        'health_status': integration['health_status']
                    }
                
                logger.info(f"[ML-API-INTEGRATOR] Loaded {len(approved)} approved integrations")
        
        except Exception as e:
            # If matrix not initialized, that's OK - use default empty list
            logger.warning(f"[ML-API-INTEGRATOR] Could not load from matrix: {e}")
            logger.info("[ML-API-INTEGRATOR] Starting with no pre-approved integrations")
    
    async def call_llm(
        self,
        prompt: str,
        context: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        allow_external: bool = False
    ) -> Dict[str, Any]:
        """
        Call LLM - uses GRACE'S INTERNAL LLM, not external APIs
        
        Args:
            prompt: The prompt
            context: Optional context
            max_tokens: Max response tokens
            temperature: Sampling temperature
            allow_external: Allow external fallback (default: False)
        
        Returns:
            LLM response from Grace's internal reasoning
        """
        
        logger.info("[ML-API-INTEGRATOR] Routing to Grace's internal LLM")
        
        # Use Grace's internal LLM via router
        result = await llm_router.generate(
            prompt=prompt,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
            allow_external_fallback=allow_external
        )
        
        return result
    
    async def get_grace_llm_info(self) -> Dict[str, Any]:
        """Get Grace's internal LLM capabilities"""
        
        stats = llm_router.get_stats()
        
        return {
            'provider': 'Grace Internal LLM',
            'capabilities': grace_llm.capabilities,
            'knowledge_sources': [
                'Ingested Books (Business Intelligence library)',
                'GitHub mined repositories',
                'Research papers (arXiv)',
                'Past learning sessions',
                'Constitutional reasoning framework',
                'Causal RL decision-making'
            ],
            'external_dependency': False,
            'stats': stats,
            'model': 'grace_reasoning_engine'
        }
    
    async def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search research papers via Papers With Code API / arXiv"""
        
        provider = 'Papers With Code API'
        integration = self.active_integrations.get(provider)
        
        if not integration:
            logger.warning(f"[ML-API-INTEGRATOR] {provider} not active, using arXiv directly")
        
        try:
            # ArXiv API (public, free)
            url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}'
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    xml = await response.text()
                    
                    # Simple XML parsing
                    papers = []
                    entries = xml.split('<entry>')
                    
                    for entry in entries[1:]:  # Skip first (before first entry)
                        title_start = entry.find('<title>') + 7
                        title_end = entry.find('</title>')
                        
                        summary_start = entry.find('<summary>') + 9
                        summary_end = entry.find('</summary>')
                        
                        id_start = entry.find('<id>') + 4
                        id_end = entry.find('</id>')
                        
                        if title_start > 6 and title_end > title_start:
                            title = entry[title_start:title_end].strip()
                            summary = entry[summary_start:summary_end].strip() if summary_start > 8 else ''
                            paper_id = entry[id_start:id_end].strip() if id_start > 3 else ''
                            
                            papers.append({
                                'title': title,
                                'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                                'url': paper_id,
                                'source': 'arXiv',
                                'query': query
                            })
                    
                    logger.info(f"[ML-API-INTEGRATOR] Found {len(papers)} papers for '{query}'")
                    
                    # Log to unified logger
                    await unified_logger.log_agentic_spine_decision(
                        decision_type='paper_search',
                        decision_context={'query': query, 'results': len(papers)},
                        chosen_action='search_arxiv',
                        rationale=f'Searching research papers for learning',
                        actor='ml_api_integrator',
                        confidence=0.8,
                        risk_score=0.1,
                        status='success'
                    )
                    
                    return papers
        
        except Exception as e:
            logger.error(f"[ML-API-INTEGRATOR] Paper search failed: {e}")
        
        return []
    
    async def get_datasets(self, topic: str) -> List[Dict[str, Any]]:
        """Get available datasets for topic"""
        
        provider = 'Kaggle API'
        integration = self.active_integrations.get(provider)
        
        # Known public datasets
        all_datasets = [
            {
                'name': 'ImageNet',
                'topic': 'computer_vision',
                'size': '150GB',
                'samples': '14M images',
                'url': 'https://www.image-net.org',
                'description': 'Large-scale image database for object recognition'
            },
            {
                'name': 'GLUE Benchmark',
                'topic': 'nlp',
                'size': '1GB',
                'samples': '9 tasks',
                'url': 'https://gluebenchmark.com',
                'description': 'Natural language understanding benchmark'
            },
            {
                'name': 'MNIST',
                'topic': 'computer_vision',
                'size': '50MB',
                'samples': '70K images',
                'url': 'http://yann.lecun.com/exdb/mnist/',
                'description': 'Handwritten digit classification dataset'
            },
            {
                'name': 'CIFAR-10',
                'topic': 'computer_vision',
                'size': '170MB',
                'samples': '60K images',
                'url': 'https://www.cs.toronto.edu/~kriz/cifar.html',
                'description': '10-class image classification dataset'
            },
            {
                'name': 'SQuAD',
                'topic': 'nlp',
                'size': '35MB',
                'samples': '100K questions',
                'url': 'https://rajpurkar.github.io/SQuAD-explorer/',
                'description': 'Question answering dataset'
            },
            {
                'name': 'Common Crawl',
                'topic': 'nlp',
                'size': 'Petabytes',
                'samples': 'Billions of web pages',
                'url': 'https://commoncrawl.org',
                'description': 'Web crawl data for NLP training'
            }
        ]
        
        # Filter by topic
        topic_lower = topic.lower()
        filtered = [d for d in all_datasets if topic_lower in d['topic'] or topic_lower in d['name'].lower()]
        
        logger.info(f"[ML-API-INTEGRATOR] Found {len(filtered)} datasets for topic '{topic}'")
        
        return filtered
    
    async def get_pretrained_models(self, framework: str = None) -> List[Dict[str, Any]]:
        """Get available pre-trained models"""
        
        models = [
            {
                'name': 'ResNet-50',
                'framework': 'tensorflow',
                'task': 'image_classification',
                'parameters': '25M',
                'url': 'https://tfhub.dev/google/imagenet/resnet_v2_50/classification'
            },
            {
                'name': 'BERT Base',
                'framework': 'tensorflow',
                'task': 'nlp',
                'parameters': '110M',
                'url': 'https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12'
            },
            {
                'name': 'MobileNet V2',
                'framework': 'tensorflow',
                'task': 'image_classification',
                'parameters': '3.5M',
                'url': 'https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification'
            },
            {
                'name': 'GPT-2',
                'framework': 'huggingface',
                'task': 'text_generation',
                'parameters': '117M',
                'url': 'https://huggingface.co/gpt2'
            },
            {
                'name': 'DistilBERT',
                'framework': 'huggingface',
                'task': 'nlp',
                'parameters': '66M',
                'url': 'https://huggingface.co/distilbert-base-uncased'
            }
        ]
        
        if framework:
            models = [m for m in models if m['framework'] == framework.lower()]
        
        logger.info(f"[ML-API-INTEGRATOR] Found {len(models)} pre-trained models")
        
        return models
    
    async def get_active_providers(self) -> List[str]:
        """Get list of active providers"""
        return list(self.active_integrations.keys())
    
    async def get_provider_capabilities(self, provider: str) -> List[str]:
        """Get capabilities of a provider"""
        
        integration = self.active_integrations.get(provider)
        
        if not integration:
            return []
        
        return integration.get('capabilities', [])


# Global instance
ml_api_integrator = MLAPIIntegrator()
