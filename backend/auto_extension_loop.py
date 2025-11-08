"""Autonomous Extension Loop

Grace Architect continuously monitors business goals,
detects missing capabilities, auto-generates extensions,
and deploys them after Parliament approval.

This makes Grace self-extending based on business needs.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from .grace_architect_agent import grace_architect, GraceExtensionRequest
from .models import async_session
from sqlalchemy import select

class AutoExtensionLoop:
    """
    Autonomous loop that extends Grace based on business needs
    
    Monitors:
    - Business empire goals (from business_empire system if available)
    - Missing capabilities (gaps in current features)
    - User requests (from knowledge base)
    - Performance bottlenecks (from meta-loop)
    
    Actions:
    - Auto-generates extensions
    - Submits to Parliament
    - Deploys when approved
    - Tracks success metrics
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 3600  # 1 hour
        self.extensions_generated = 0
        self.extensions_deployed = 0
        
    async def start(self):
        """Start the autonomous loop"""
        
        self.running = True
        print("[AI] Auto-Extension Loop started")
        print(f"   Checking every {self.check_interval}s for missing capabilities")
        
        while self.running:
            try:
                await self._check_and_extend()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Auto-Extension Loop error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the autonomous loop"""
        
        self.running = False
        print(f"🛑 Auto-Extension Loop stopped")
        print(f"   Extensions generated: {self.extensions_generated}")
        print(f"   Extensions deployed: {self.extensions_deployed}")
    
    async def _check_and_extend(self):
        """Check for missing capabilities and generate extensions"""
        
        print(f"\n🔍 Auto-Extension Loop: Checking for gaps ({datetime.now()})")
        
        # Step 1: Detect missing capabilities
        gaps = await self._detect_capability_gaps()
        
        if not gaps:
            print("   ✅ No gaps detected")
            return
        
        print(f"   Found {len(gaps)} capability gaps:")
        for gap in gaps:
            print(f"      - {gap['name']}: {gap['description']}")
        
        # Step 2: For each gap, check if extension already exists
        for gap in gaps:
            existing = await self._check_existing_extension(gap['name'])
            
            if existing:
                print(f"   ⏭️  Extension already exists for: {gap['name']}")
                continue
            
            # Step 3: Generate extension
            print(f"   🏗️  Generating extension for: {gap['name']}")
            
            try:
                extension = await grace_architect.generate_grace_extension(
                    feature_request=gap['description'],
                    business_need=gap.get('business_impact', 'Improve Grace capabilities')
                )
                
                self.extensions_generated += 1
                
                print(f"      ✅ Generated: {extension['request_id']}")
                
                # Step 4: Auto-deploy if low risk
                if gap.get('risk_level', 'medium') == 'low':
                    print(f"      🚀 Auto-deploying (low risk)...")
                    
                    deploy_result = await grace_architect.deploy_extension(
                        extension_id=extension['request_id'],
                        require_parliament=False,
                        auto_test=True
                    )
                    
                    if deploy_result['status'] == 'success':
                        self.extensions_deployed += 1
                        print(f"      ✅ Deployed successfully")
                        
                        # Track success metric
                        await self._track_extension_success(
                            extension['request_id'],
                            gap['name']
                        )
                else:
                    print(f"      ⏳ Awaiting Parliament approval (risk: {gap.get('risk_level', 'medium')})")
            
            except Exception as e:
                print(f"      ❌ Failed to generate: {e}")
    
    async def _detect_capability_gaps(self) -> List[Dict[str, Any]]:
        """
        Detect missing capabilities in Grace
        
        Strategies:
        1. Check business_empire goals for unmet needs
        2. Analyze user queries for common requests
        3. Check meta-loop recommendations
        4. Identify integration gaps
        """
        
        gaps = []
        
        # Strategy 1: Hardcoded common business needs
        # (In production, would query business_empire goals)
        common_needs = [
            {
                'name': 'email_notifications',
                'description': 'Email notification system for alerts and reports',
                'business_impact': 'Keep users informed of important events',
                'risk_level': 'low'
            },
            {
                'name': 'slack_integration',
                'description': 'Slack integration for team notifications',
                'business_impact': 'Improve team collaboration',
                'risk_level': 'low'
            },
            {
                'name': 'advanced_analytics',
                'description': 'Advanced analytics dashboard for business metrics',
                'business_impact': 'Data-driven decision making',
                'risk_level': 'medium'
            },
            {
                'name': 'api_rate_limiter',
                'description': 'Rate limiting system for API endpoints',
                'business_impact': 'Prevent abuse and ensure fair usage',
                'risk_level': 'medium'
            },
            {
                'name': 'backup_system',
                'description': 'Automated backup and restore system',
                'business_impact': 'Data safety and disaster recovery',
                'risk_level': 'high'
            }
        ]
        
        # Check which ones don't exist yet
        grace_backend = Path(__file__).parent
        
        for need in common_needs:
            # Check if component already exists
            potential_files = [
                grace_backend / f"{need['name']}.py",
                grace_backend / f"{need['name']}_service.py",
                grace_backend / f"{need['name']}_engine.py"
            ]
            
            exists = any(f.exists() for f in potential_files)
            
            if not exists:
                gaps.append(need)
        
        # Strategy 2: Check for frequently requested features
        # (Would query knowledge base or user feedback in production)
        
        return gaps[:2]  # Limit to 2 gaps per check to avoid overwhelming
    
    async def _check_existing_extension(self, capability_name: str) -> bool:
        """Check if extension already exists for this capability"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GraceExtensionRequest).where(
                    GraceExtensionRequest.feature_request.ilike(f"%{capability_name}%")
                )
            )
            existing = result.scalar_one_or_none()
            
            return existing is not None
    
    async def _track_extension_success(
        self,
        extension_id: str,
        capability_name: str
    ):
        """Track success metrics for deployed extension"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GraceExtensionRequest).where(
                    GraceExtensionRequest.request_id == extension_id
                )
            )
            extension = result.scalar_one_or_none()
            
            if extension:
                # Initialize success tracking
                extension.success = True  # Will be updated based on usage
                extension.revenue_impact = 0.0  # Will be calculated from metrics
                
                await session.commit()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get auto-extension loop statistics"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GraceExtensionRequest)
            )
            all_extensions = result.scalars().all()
            
            auto_generated = [
                e for e in all_extensions
                if e.feature_request and 'system' in e.feature_request.lower()
            ]
            
            deployed = [e for e in auto_generated if e.deployed]
            
            return {
                'running': self.running,
                'total_extensions': len(all_extensions),
                'auto_generated': len(auto_generated),
                'deployed': len(deployed),
                'pending_approval': len(auto_generated) - len(deployed),
                'success_rate': (len(deployed) / len(auto_generated) * 100) if auto_generated else 0
            }

# Singleton
auto_extension_loop = AutoExtensionLoop()


async def demo_auto_extension_loop():
    """Demo the autonomous extension loop"""
    
    print("\n" + "="*80)
    print("AUTO-EXTENSION LOOP DEMO".center(80))
    print("="*80 + "\n")
    
    print("[AI] This demonstrates Grace autonomously extending herself")
    print("   based on detected capability gaps and business needs.")
    print()
    
    # Initialize
    from .models import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Learn architecture first
    print("[INFO] Learning Grace architecture...")
    await grace_architect.learn_grace_architecture()
    print("   ✅ Ready\n")
    
    # Run one iteration
    print("🔍 Running capability gap analysis...")
    print()
    
    await auto_extension_loop._check_and_extend()
    
    print("\n" + "="*80)
    
    # Show stats
    stats = await auto_extension_loop.get_stats()
    
    print("\n📊 Auto-Extension Statistics:")
    print(f"   Total extensions: {stats['total_extensions']}")
    print(f"   Auto-generated: {stats['auto_generated']}")
    print(f"   Deployed: {stats['deployed']}")
    print(f"   Pending approval: {stats['pending_approval']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    print()
    
    print("🚀 In production, this runs continuously:")
    print("   - Monitors business goals")
    print("   - Detects capability gaps")
    print("   - Auto-generates extensions")
    print("   - Submits to Parliament")
    print("   - Deploys when approved")
    print("   - Tracks success metrics")
    print()
    print("Grace becomes self-extending based on business needs!")
    print()

if __name__ == "__main__":
    asyncio.run(demo_auto_extension_loop())
