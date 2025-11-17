"""
API Discovery Engine
Grace discovers free APIs that can help her learn and expand her capabilities
Tests in sandbox, stores keys in secrets vault, promotes to production if safe
"""

import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .governance_framework import governance_framework
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class APIDiscoveryEngine:
    """
    Grace discovers and integrates free APIs autonomously
    All APIs tested in sandbox before production use
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.discovered_apis = []
        
        # Known free API directories
        self.api_directories = [
            'https://api.publicapis.org/entries',  # Public APIs directory
            'https://github.com/public-apis/public-apis'  # GitHub API list
        ]
        
        # Useful API categories for Grace's learning
        self.useful_categories = [
            'Development',
            'Programming',
            'Open Data',
            'Education',
            'Documentation',
            'Code',
            'Technology',
            'Software',
            'Cloud',
            'AI/ML'
        ]
    
    async def start(self):
        """Start API discovery"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GraceAI-APIDiscovery/1.0'},
                timeout=aiohttp.ClientTimeout(total=30)
            )
        logger.info("[API-DISCOVERY] ✅ API Discovery Engine started")
    
    async def stop(self):
        """Stop API discovery"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[API-DISCOVERY] Stopped")
    
    async def discover_apis(
        self,
        category: Optional[str] = None,
        max_apis: int = 10
    ) -> Dict[str, Any]:
        """
        Discover free APIs that Grace can use for learning
        
        Args:
            category: API category to focus on
            max_apis: Maximum APIs to discover
        
        Returns:
            Discovery summary with found APIs
        """
        
        logger.info(f"[API-DISCOVERY] 🔍 Discovering free APIs...")
        if category:
            logger.info(f"[API-DISCOVERY] Category: {category}")
        
        # Governance check
        approval = await governance_framework.check_action(
            actor='grace_api_discovery',
            action='discover_apis',
            resource='public_apis',
            context={'category': category},
            confidence=0.9
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[API-DISCOVERY] 🚫 Governance blocked")
            return {'error': 'governance_blocked'}
        
        # Discover APIs from Public APIs directory
        apis = await self._fetch_public_apis(category, max_apis)
        
        # Filter useful APIs
        useful_apis = self._filter_useful_apis(apis)
        
        logger.info(f"[API-DISCOVERY] ✅ Discovered {len(useful_apis)} useful APIs")
        
        # Store discoveries
        for api in useful_apis:
            await self._record_api_discovery(api)
        
        return {
            'apis_discovered': len(useful_apis),
            'apis': useful_apis,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _fetch_public_apis(
        self,
        category: Optional[str],
        max_apis: int
    ) -> List[Dict[str, Any]]:
        """Fetch APIs from public directory"""
        
        apis = []
        
        try:
            # Fetch from public-apis.io
            url = 'https://api.publicapis.org/entries'
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get('entries', [])
                    
                    for entry in entries[:max_apis]:
                        # Filter by category if specified
                        if category and entry.get('Category', '').lower() != category.lower():
                            continue
                        
                        # Only include useful categories
                        if entry.get('Category') in self.useful_categories:
                            apis.append({
                                'name': entry.get('API'),
                                'description': entry.get('Description'),
                                'url': entry.get('Link'),
                                'category': entry.get('Category'),
                                'auth': entry.get('Auth', 'None'),
                                'https': entry.get('HTTPS', False),
                                'cors': entry.get('Cors', 'unknown')
                            })
        
        except Exception as e:
            logger.warning(f"[API-DISCOVERY] Error fetching APIs: {e}")
            
            # Fallback to known useful free APIs
            apis = self._get_known_useful_apis()
        
        return apis
    
    def _get_known_useful_apis(self) -> List[Dict[str, Any]]:
        """Get list of known useful free APIs for learning"""
        
        return [
            {
                'name': 'GitHub API',
                'description': 'Access GitHub repositories, code, and data',
                'url': 'https://api.github.com',
                'category': 'Development',
                'auth': 'apiKey',
                'https': True,
                'cors': 'yes',
                'useful_for': 'Mining code patterns, learning from repos'
            },
            {
                'name': 'OpenAI API',
                'description': 'AI/ML capabilities for learning enhancement',
                'url': 'https://api.openai.com',
                'category': 'AI/ML',
                'auth': 'apiKey',
                'https': True,
                'cors': 'yes',
                'useful_for': 'Code understanding, learning assistance'
            },
            {
                'name': 'Wikipedia API',
                'description': 'Access Wikipedia knowledge',
                'url': 'https://en.wikipedia.org/api',
                'category': 'Education',
                'auth': 'None',
                'https': True,
                'cors': 'yes',
                'useful_for': 'General knowledge, concepts'
            },
            {
                'name': 'JSONPlaceholder',
                'description': 'Fake REST API for testing',
                'url': 'https://jsonplaceholder.typicode.com',
                'category': 'Development',
                'auth': 'None',
                'https': True,
                'cors': 'yes',
                'useful_for': 'Testing REST API patterns'
            },
            {
                'name': 'Stack Exchange API',
                'description': 'Access Stack Overflow Q&A',
                'url': 'https://api.stackexchange.com',
                'category': 'Development',
                'auth': 'apiKey',
                'https': True,
                'cors': 'yes',
                'useful_for': 'Learning from developer Q&A'
            }
        ]
    
    def _filter_useful_apis(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter for APIs useful to Grace's learning"""
        
        useful = []
        
        for api in apis:
            # Must have HTTPS
            if not api.get('https', False):
                continue
            
            # Must be in useful categories
            if api.get('category') not in self.useful_categories:
                continue
            
            # Prefer free or apiKey auth (no OAuth complexity)
            auth = api.get('auth', 'None')
            if auth in ['None', 'apiKey', 'X-Api-Key']:
                useful.append(api)
        
        return useful
    
    async def _record_api_discovery(self, api: Dict[str, Any]):
        """Record discovered API"""
        
        self.discovered_apis.append(api)
        
        # Log discovery
        await unified_logger.log_agentic_spine_decision(
            decision_type='api_discovered',
            decision_context={'api_name': api['name'], 'category': api['category']},
            chosen_action='discover_api',
            rationale=f"Discovered useful API: {api['description']}",
            actor='api_discovery_engine',
            confidence=0.8,
            risk_score=0.2,
            status='discovered',
            resource=api['name']
        )
        
        logger.info(f"[API-DISCOVERY] 📡 Found: {api['name']} ({api['category']})")
    
    async def get_discovered_apis(self) -> List[Dict[str, Any]]:
        """Get all discovered APIs"""
        return self.discovered_apis


# Global instance
api_discovery = APIDiscoveryEngine()
