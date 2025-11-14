"""
API Integration Manager
Manages Grace's complete API lifecycle: Discovery → Testing → Integration → Usage
All APIs managed autonomously with governance
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pathlib import Path
import json

from .api_discovery_engine import api_discovery
from .api_sandbox_tester import api_sandbox_tester
from .governance_framework import governance_framework
from .unified_logger import unified_logger
from .secrets_vault import secrets_vault

logger = logging.getLogger(__name__)


class APIIntegrationManager:
    """
    Complete API lifecycle management
    Grace autonomously discovers, tests, and integrates APIs
    """
    
    def __init__(self):
        self.running = False
        self.integrated_apis = {}
        self.discovery_cycle_interval = 86400  # 24 hours
        self.cycle_task = None
    
    async def start(self):
        """Start API integration manager"""
        if self.running:
            return
        
        self.running = True
        
        # Start discovery engine
        await api_discovery.start()
        
        # Load existing integrated APIs
        await self._load_integrated_apis()
        
        # Start discovery cycle
        self.cycle_task = asyncio.create_task(self._discovery_cycle())
        
        logger.info("[API-MANAGER] ✅ API Integration Manager started")
        logger.info(f"[API-MANAGER] Integrated APIs: {len(self.integrated_apis)}")
    
    async def stop(self):
        """Stop API integration manager"""
        self.running = False
        
        if self.cycle_task:
            self.cycle_task.cancel()
        
        await api_discovery.stop()
        
        logger.info("[API-MANAGER] Stopped")
    
    async def _discovery_cycle(self):
        """Periodic API discovery cycle"""
        
        while self.running:
            try:
                await asyncio.sleep(self.discovery_cycle_interval)
                
                logger.info("[API-MANAGER] 🔍 Running API discovery cycle...")
                
                # Discover new APIs
                discovery_result = await api_discovery.discover_apis(max_apis=10)
                
                if 'error' not in discovery_result:
                    apis = discovery_result.get('apis', [])
                    logger.info(f"[API-MANAGER] Found {len(apis)} potential APIs")
                    
                    # Test promising APIs
                    for api in apis[:3]:  # Test top 3
                        await self._test_and_integrate(api)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[API-MANAGER] Error in discovery cycle: {e}", exc_info=True)
    
    async def discover_and_integrate(
        self,
        category: Optional[str] = None,
        auto_promote: bool = False
    ) -> Dict[str, Any]:
        """
        Discover and integrate new APIs
        
        Args:
            category: API category to focus on
            auto_promote: Automatically promote if tests pass
        
        Returns:
            Integration summary
        """
        
        logger.info(f"[API-MANAGER] 🔍 Discovering APIs...")
        
        # Discover APIs
        discovery = await api_discovery.discover_apis(category=category, max_apis=10)
        
        if 'error' in discovery:
            return discovery
        
        apis = discovery.get('apis', [])
        logger.info(f"[API-MANAGER] Discovered {len(apis)} APIs")
        
        # Test each API in sandbox
        tested = []
        approved = []
        
        for api in apis:
            result = await self._test_and_integrate(api, auto_promote=auto_promote)
            tested.append(result)
            
            if result.get('recommend_promotion'):
                approved.append(api)
        
        summary = {
            'category': category,
            'apis_discovered': len(apis),
            'apis_tested': len(tested),
            'apis_approved': len(approved),
            'auto_promoted': len([r for r in tested if r.get('promoted', False)]),
            'approved_apis': approved,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"[API-MANAGER] ✅ Discovery & integration complete")
        logger.info(f"  Discovered: {summary['apis_discovered']}")
        logger.info(f"  Tested: {summary['apis_tested']}")
        logger.info(f"  Approved: {summary['apis_approved']}")
        
        return summary
    
    async def _test_and_integrate(
        self,
        api: Dict[str, Any],
        api_key: Optional[str] = None,
        auto_promote: bool = False
    ) -> Dict[str, Any]:
        """Test API in sandbox and optionally promote"""
        
        logger.info(f"[API-MANAGER] 🧪 Testing: {api['name']}")
        
        # Test in sandbox
        test_result = await api_sandbox_tester.test_api(
            api_info=api,
            api_key=api_key,
            test_endpoints=None
        )
        
        # Auto-promote if tests passed and enabled
        if auto_promote and test_result.get('recommend_promotion', False):
            logger.info(f"[API-MANAGER] 🚀 Auto-promoting {api['name']}...")
            
            promotion = await api_sandbox_tester.promote_to_production(api['name'])
            
            if 'error' not in promotion:
                # Add to integrated APIs
                self.integrated_apis[api['name']] = {
                    'api': api,
                    'test_result': test_result,
                    'promoted_at': datetime.utcnow().isoformat(),
                    'status': 'active'
                }
                
                test_result['promoted'] = True
                logger.info(f"[API-MANAGER] ✅ {api['name']} is now in production!")
        
        return test_result
    
    async def add_api_with_key(
        self,
        api_name: str,
        api_url: str,
        api_key: str,
        category: str = 'Development',
        description: str = '',
        test_first: bool = True
    ) -> Dict[str, Any]:
        """
        Add an API with its key
        
        Args:
            api_name: Name of the API
            api_url: Base URL
            api_key: API key to store securely
            category: API category
            description: What the API does
            test_first: Test in sandbox before adding
        
        Returns:
            Integration result
        """
        
        logger.info(f"[API-MANAGER] 🔑 Adding API with key: {api_name}")
        
        api_info = {
            'name': api_name,
            'url': api_url,
            'category': category,
            'description': description,
            'auth': 'apiKey',
            'https': api_url.startswith('https://'),
            'added_manually': True
        }
        
        if test_first:
            # Test in sandbox first
            test_result = await self._test_and_integrate(
                api=api_info,
                api_key=api_key,
                auto_promote=True
            )
            
            return test_result
        else:
            # Store key and add directly
            secret_name = f"{api_name.upper().replace(' ', '_')}_API_KEY"
            await secrets_vault.set_secret(secret_name, api_key)
            
            self.integrated_apis[api_name] = {
                'api': api_info,
                'secret_name': secret_name,
                'added_at': datetime.utcnow().isoformat(),
                'tested': False
            }
            
            logger.info(f"[API-MANAGER] ✅ API added: {api_name}")
            
            return {'success': True, 'api_name': api_name, 'tested': False}
    
    async def _load_integrated_apis(self):
        """Load integrated APIs from config"""
        
        config_file = Path(__file__).parent.parent / "config" / "integrated_apis.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                
                for api in config.get('apis', []):
                    self.integrated_apis[api['name']] = api
                
                logger.info(f"[API-MANAGER] Loaded {len(self.integrated_apis)} integrated APIs")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get API manager status"""
        
        sandbox_status = await api_sandbox_tester.get_status()
        
        return {
            'running': self.running,
            'integrated_apis': len(self.integrated_apis),
            'apis_tested': sandbox_status['apis_tested'],
            'apis_approved': sandbox_status['apis_approved'],
            'apis_blocked': sandbox_status['apis_blocked'],
            'approval_rate': sandbox_status['approval_rate'],
            'discovery_cycle_hours': self.discovery_cycle_interval / 3600
        }


# Global instance
api_integration_manager = APIIntegrationManager()
