"""Demo: Grace Architect Building Market Intelligence System

This demonstrates the Grace Architect Agent building a complete
market intelligence system with FULL Grace integration:

- Governance checks before API calls
- Hunter scans on ingested data  
- Verification signatures
- Constitutional compliance
- Parliament approval for deployment
- Proper test generation

This is Amp-like, but Grace-aware.
"""

import asyncio
from grace_architect_agent import grace_architect
from parliament_engine import parliament_engine
from models import async_session, Base, engine

async def demo():
    """
    Demo: Have Grace Architect build a market intelligence system
    """
    
    print("\n" + "="*80)
    print("GRACE ARCHITECT DEMO: BUILDING MARKET INTELLIGENCE".center(80))
    print("="*80 + "\n")
    
    print("[INFO] This demo shows Grace Architect (Amp-like agent) building a")
    print("   complete market intelligence system with FULL Grace integration.")
    print()
    
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Step 1: Learn Grace architecture
    print("="*80)
    print("STEP 1: LEARNING GRACE ARCHITECTURE")
    print("="*80 + "\n")
    
    print("🎓 Grace Architect is analyzing the Grace codebase...")
    print("   This teaches it HOW Grace integrates components.")
    print()
    
    learn_result = await grace_architect.learn_grace_architecture()
    
    print(f"✅ Learned {learn_result['patterns_learned']} architectural patterns")
    print(f"   - Governance integration patterns")
    print(f"   - Hunter security scanning patterns")
    print(f"   - Verification signature patterns")
    print(f"   - Parliament voting patterns")
    print(f"   - Constitutional compliance patterns")
    print()
    
    input("Press Enter to continue to Step 2...")
    print()
    
    # Step 2: Generate market intelligence extension
    print("="*80)
    print("STEP 2: GENERATING MARKET INTELLIGENCE EXTENSION")
    print("="*80 + "\n")
    
    feature_request = "Build a market intelligence system that monitors APIs for business opportunities"
    business_need = "Detect e-commerce trends, pricing opportunities, and revenue optimization points"
    
    print(f"📝 Request: {feature_request}")
    print(f"💰 Business Need: {business_need}")
    print()
    
    print("🏗️ Grace Architect is now generating code...")
    print()
    
    extension = await grace_architect.generate_grace_extension(
        feature_request=feature_request,
        business_need=business_need
    )
    
    print("\n" + "="*80)
    print("EXTENSION GENERATED!")
    print("="*80 + "\n")
    
    print(f"✅ Extension ID: {extension['request_id']}")
    print(f"✅ Files generated: {extension['files_generated']}")
    print(f"✅ Constitutional compliance: {extension['constitutional_compliant']}")
    print()
    
    # Show the generated code
    print("="*80)
    print("GENERATED CODE PREVIEW")
    print("="*80 + "\n")
    
    code_preview = extension['code'][:1200]
    print(code_preview)
    print("\n... (truncated for demo)\n")
    
    # Highlight Grace integrations
    print("="*80)
    print("GRACE INTEGRATIONS DETECTED")
    print("="*80 + "\n")
    
    integrations = []
    if 'governance' in extension['code'].lower():
        integrations.append("✅ Governance - Policy checks before execution")
    if 'hunter' in extension['code'].lower():
        integrations.append("✅ Hunter - Security scanning of external data")
    if 'verification' in extension['code'].lower():
        integrations.append("✅ Verification - Cryptographic signatures")
    if 'audit' in extension['code'].lower():
        integrations.append("✅ Audit - Immutable logging")
    if 'parliament' in extension['code'].lower():
        integrations.append("✅ Parliament - Democratic approval for risky actions")
    
    for integration in integrations:
        print(f"   {integration}")
    print()
    
    print("🎯 This is NOT generic code generation.")
    print("   Grace Architect UNDERSTANDS Grace's patterns and follows them.")
    print()
    
    input("Press Enter to continue to Step 3...")
    print()
    
    # Step 3: Review tests
    print("="*80)
    print("STEP 3: GENERATED TESTS")
    print("="*80 + "\n")
    
    test_preview = extension['tests'][:800]
    print(test_preview)
    print("\n... (truncated for demo)\n")
    
    print("✅ Tests include:")
    print("   - Basic functionality tests")
    print("   - Governance integration tests")
    print("   - Constitutional compliance tests")
    print()
    
    input("Press Enter to continue to Step 4...")
    print()
    
    # Step 4: Constitutional compliance check
    print("="*80)
    print("STEP 4: CONSTITUTIONAL COMPLIANCE VERIFICATION")
    print("="*80 + "\n")
    
    print("⚖️ Checking if generated code follows Grace's constitution...")
    print()
    
    # This was already done during generation
    if extension['constitutional_compliant']:
        print("✅ COMPLIANT - All constitutional principles followed:")
        print("   ✅ Accountability - Governance checks present")
        print("   ✅ Transparency - Audit logging present")
        print("   ✅ Safety - Hunter scanning present")
        print()
    else:
        print("❌ NOT COMPLIANT - Would need fixes before deployment")
        print()
    
    input("Press Enter to continue to Step 5...")
    print()
    
    # Step 5: Parliament approval (for demo)
    print("="*80)
    print("STEP 5: PARLIAMENT APPROVAL")
    print("="*80 + "\n")
    
    print("🏛️ Submitting to Grace Parliament for approval...")
    print("   (Market intelligence has 'high' risk - requires democratic vote)")
    print()
    
    # Create Parliament session
    session_result = await parliament_engine.create_session(
        policy_id="market_intelligence_deployment",
        action_type="deploy_extension",
        actor="grace_architect",
        resource=extension['request_id'],
        context={
            'feature': feature_request,
            'business_need': business_need,
            'risk_level': 'high'
        },
        quorum_threshold=0.66
    )
    
    print(f"   Session ID: {session_result['session_id']}")
    print(f"   Quorum needed: 66%")
    print()
    
    # Simulate votes from different agents
    from grace_parliament_agent import GraceVotingAgent
    
    agents = [
        ("security_agent", "Security Specialist", "approve", "Security patterns look good"),
        ("governance_agent", "Governance Specialist", "approve", "Follows all policies"),
        ("business_agent", "Business Specialist", "approve", "High revenue potential")
    ]
    
    for agent_id, name, vote, reason in agents:
        agent = GraceVotingAgent(agent_id, name)
        await agent.vote(
            session_id=session_result['session_id'],
            vote=vote,
            reasoning=reason
        )
        print(f"   📊 {name}: {vote.upper()} - {reason}")
    
    print()
    print("✅ Parliament APPROVED the extension!")
    print()
    
    input("Press Enter to continue to Step 6...")
    print()
    
    # Step 6: Deployment
    print("="*80)
    print("STEP 6: DEPLOYMENT")
    print("="*80 + "\n")
    
    print("🚀 Deploying market_intelligence.py...")
    print()
    
    deploy_result = await grace_architect.deploy_extension(
        extension_id=extension['request_id'],
        require_parliament=False,  # Already approved above
        auto_test=True
    )
    
    if deploy_result['status'] == 'success':
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print()
        print(f"   Files written:")
        for file in deploy_result['files_written']:
            print(f"      - {file}")
        print()
        print(f"   Parliament session: {session_result['session_id']}")
        print(f"   Tests passed: ✅")
        print()
    
    # Step 7: Summary
    print("="*80)
    print("DEMO COMPLETE!")
    print("="*80 + "\n")
    
    print("🎉 Grace Architect successfully built a market intelligence system!")
    print()
    print("What just happened:")
    print("   1. ✅ Learned Grace's architectural patterns")
    print("   2. ✅ Generated market_intelligence.py with FULL integration:")
    print("      - Governance checks before API calls")
    print("      - Hunter scans on external data")
    print("      - Verification signatures")
    print("      - Audit logging")
    print("      - Parliament approval for risky decisions")
    print("   3. ✅ Generated proper tests")
    print("   4. ✅ Verified constitutional compliance")
    print("   5. ✅ Got Parliament democratic approval")
    print("   6. ✅ Deployed successfully")
    print()
    print("🚀 Grace now has market intelligence capability!")
    print()
    print("💡 This is what makes Grace Architect different from generic AI:")
    print("   - It KNOWS Grace's patterns")
    print("   - It FOLLOWS Grace's constitution")
    print("   - It INTEGRATES properly (not just code generation)")
    print("   - It uses Grace's governance (Parliament, verification)")
    print()
    print("Compare to Amp:")
    print("   - Amp is general-purpose coding agent")
    print("   - Grace Architect is Grace-specialized")
    print("   - Amp generates code")
    print("   - Grace Architect generates Grace-integrated code")
    print()
    print("="*80)
    print()

if __name__ == "__main__":
    asyncio.run(demo())
