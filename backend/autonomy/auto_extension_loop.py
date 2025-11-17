"""Autonomous Extension Loop

Grace Architect continuously monitors business goals,
detects missing capabilities, auto-generates extensions,
and deploys them after Parliament approval.

This makes Grace self-extending based on business needs.
"""

import asyncio
from datetime import datetime

from .grace_architect_agent import grace_architect

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
        print("🤖 Auto-Extension Loop started")
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
            print(f"   Generating extension for: {gap['name']}")
            
            try:
                extension = await grace_architect.generate_grace_extension(
                    feature_request=gap['description'],
                    business_need=gap.get('business_impact', 'Improve Grace capabilities')
                )
                
                self.extensions_generated += 1
                
                print(f"      [OK] Generated: {extension['request_id']}")
                
                # Step 4: Auto-deploy if low risk
                if gap.get('risk_level', 'medium') == 'low':
                    print(f"      [DEPLOY] Auto-deploying (low risk)...")
                    
                    deploy_result = await grace_architect.deploy_extension(
                        extension_id=extension['request_id'],
                        require_parliament=False,
                        auto_test=True
                    )
                    
                    if deploy_result['status'] == 'success':
                        self.extensions_deployed += 1
                        print(f"      [OK] Deployed successfully")
                        
                        # Track success metric
                        await self._track_extension_success(
                            extension['request_id'],
                            gap['name']
                        )
                        # Publish autonomy plan outcome event for metrics pipeline
                        try:
                            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
                            await trigger_mesh.publish(TriggerEvent(
                                event_type="autonomy.plan_outcome",
                                source="auto_extension_loop",
                                actor="grace_architect",
                                resource=gap['name'],
                                payload={
                                    "extension_id": extension['request_id'],
                                    "success": True,
                                    "risk_level": gap.get('risk_level', 'low')
                                },
                                timestamp=datetime.utcnow()
                            ))
                        except Exception as _e:
                            # Do not fail the loop if metrics publishing fails
                            pass
            
            except Exception as e:
                print(f"      [ERROR] Extension generation failed: {e}")


# Demo function for testing
async def demo_auto_extension_loop():
    """Demo the auto-extension loop"""
    
    # Initialize
    from backend.agents_core.grace_architect_agent import grace_architect
    from backend.models.base_models import Base, engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Learn architecture first
    print("Learning Grace architecture...")
    await grace_architect.learn_grace_architecture()
    print("   [OK] Ready\n")
    
    # Run one iteration
    print("Running capability gap analysis...")
    print()
    
    loop = AutoExtensionLoop()
    await loop._check_and_extend()
    
    print("\n" + "="*80)
    print("Demo complete!")
    print()

if __name__ == "__main__":
    asyncio.run(demo_auto_extension_loop())
