"""
Crypto API Installer and Integrator
Automatically installs and configures free crypto trading APIs
"""

import asyncio
import logging
import subprocess
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CryptoAPIInstaller:
    """
    Installs and configures free crypto trading APIs:
    - CCXT (100+ exchanges)
    - python-binance
    - coinbase-python
    - pycoingecko
    """
    
    def __init__(self):
        self.installed_apis = {}
        self.api_configs = {
            'ccxt': {
                'package': 'ccxt',
                'import_name': 'ccxt',
                'description': 'Unified API for 100+ crypto exchanges',
                'free': True,
                'no_api_key_needed': False
            },
            'python-binance': {
                'package': 'python-binance',
                'import_name': 'binance',
                'description': 'Binance exchange API',
                'free': True,
                'no_api_key_needed': False
            },
            'coinbase': {
                'package': 'coinbase',
                'import_name': 'coinbase',
                'description': 'Coinbase exchange API',
                'free': True,
                'no_api_key_needed': False
            },
            'pycoingecko': {
                'package': 'pycoingecko',
                'import_name': 'pycoingecko',
                'description': 'CoinGecko market data (NO API KEY REQUIRED)',
                'free': True,
                'no_api_key_needed': True  # Completely free!
            }
        }
        self._initialized = False
    
    async def initialize(self):
        """Initialize crypto APIs"""
        if self._initialized:
            return
        
        logger.info("[CRYPTO-API] Initializing crypto trading APIs...")
        
        # Check which APIs are already installed
        await self.check_installed_apis()
        
        self._initialized = True
    
    async def check_installed_apis(self) -> Dict[str, bool]:
        """Check which crypto APIs are installed"""
        status = {}
        
        for api_name, config in self.api_configs.items():
            try:
                __import__(config['import_name'])
                status[api_name] = True
                self.installed_apis[api_name] = config
                logger.info(f"[CRYPTO-API] ✅ {api_name} installed")
            except ImportError:
                status[api_name] = False
                logger.info(f"[CRYPTO-API] ⚠️ {api_name} not installed")
        
        return status
    
    async def install_all_free_apis(self) -> Dict[str, Any]:
        """Install all free crypto trading APIs"""
        results = {
            'installed': [],
            'failed': [],
            'already_installed': []
        }
        
        for api_name, config in self.api_configs.items():
            try:
                # Check if already installed
                try:
                    __import__(config['import_name'])
                    results['already_installed'].append(api_name)
                    logger.info(f"[CRYPTO-API] ✅ {api_name} already installed")
                    continue
                except ImportError:
                    pass
                
                # Install
                logger.info(f"[CRYPTO-API] 📦 Installing {api_name}...")
                
                process = await asyncio.create_subprocess_exec(
                    'pip', 'install', config['package'],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    results['installed'].append(api_name)
                    self.installed_apis[api_name] = config
                    logger.info(f"[CRYPTO-API] ✅ {api_name} installed successfully")
                else:
                    results['failed'].append({
                        'api': api_name,
                        'error': stderr.decode()
                    })
                    logger.error(f"[CRYPTO-API] ❌ {api_name} installation failed")
            
            except Exception as e:
                results['failed'].append({
                    'api': api_name,
                    'error': str(e)
                })
                logger.error(f"[CRYPTO-API] ❌ {api_name} installation error: {e}")
        
        return results
    
    async def test_crypto_apis(self) -> Dict[str, Any]:
        """Test installed crypto APIs to ensure they work"""
        test_results = {}
        
        # Test CCXT
        if 'ccxt' in self.installed_apis:
            try:
                import ccxt
                exchange = ccxt.binance()
                ticker = await asyncio.to_thread(exchange.fetch_ticker, 'BTC/USDT')
                test_results['ccxt'] = {
                    'status': 'working',
                    'test': 'Fetched BTC/USDT ticker',
                    'price': ticker.get('last', 0)
                }
                logger.info(f"[CRYPTO-API] ✅ CCXT working (BTC: ${ticker.get('last', 0)})")
            except Exception as e:
                test_results['ccxt'] = {'status': 'error', 'error': str(e)}
        
        # Test pycoingecko (no API key needed!)
        if 'pycoingecko' in self.installed_apis:
            try:
                from pycoingecko import CoinGeckoAPI
                cg = CoinGeckoAPI()
                price = await asyncio.to_thread(
                    cg.get_price,
                    ids='bitcoin',
                    vs_currencies='usd'
                )
                test_results['pycoingecko'] = {
                    'status': 'working',
                    'test': 'Fetched Bitcoin price',
                    'price': price.get('bitcoin', {}).get('usd', 0)
                }
                logger.info(f"[CRYPTO-API] ✅ CoinGecko working (BTC: ${price.get('bitcoin', {}).get('usd', 0)})")
            except Exception as e:
                test_results['pycoingecko'] = {'status': 'error', 'error': str(e)}
        
        return test_results
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get crypto API metrics"""
        return {
            'total_apis_configured': len(self.api_configs),
            'apis_installed': len(self.installed_apis),
            'installed_list': list(self.installed_apis.keys()),
            'initialized': self._initialized
        }


# Global instance
crypto_api_installer = CryptoAPIInstaller()
