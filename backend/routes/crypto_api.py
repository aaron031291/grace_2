"""
Crypto Trading APIs
Install, configure, and use free crypto trading APIs
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crypto", tags=["Crypto Trading"])


@router.post("/install-apis")
async def install_crypto_apis():
    """
    Install all free crypto trading APIs:
    - CCXT (100+ exchanges)
    - python-binance
    - coinbase-python
    - pycoingecko (NO API KEY REQUIRED!)
    """
    try:
        from backend.integrations.crypto_api_installer import crypto_api_installer
        
        logger.info("[CRYPTO-API] Installing all free crypto APIs...")
        
        results = await crypto_api_installer.install_all_free_apis()
        
        return {
            "success": True,
            "installation_results": results,
            "message": f"Installed {len(results['installed'])} new APIs, {len(results['already_installed'])} already present"
        }
    
    except Exception as e:
        logger.error(f"[CRYPTO-API-ROUTE] Installation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-apis")
async def test_crypto_apis():
    """
    Test installed crypto APIs to ensure they work
    Fetches live Bitcoin price from available APIs
    """
    try:
        from backend.integrations.crypto_api_installer import crypto_api_installer
        
        test_results = await crypto_api_installer.test_crypto_apis()
        
        return {
            "success": True,
            "test_results": test_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[CRYPTO-API-ROUTE] Testing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_crypto_api_status():
    """Check which crypto APIs are installed and working"""
    try:
        from backend.integrations.crypto_api_installer import crypto_api_installer
        
        status = await crypto_api_installer.check_installed_apis()
        metrics = await crypto_api_installer.get_metrics()
        
        return {
            "status": status,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "degraded"
        }
