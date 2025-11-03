"""Grace Architect CLI Commands

CLI interface for the Grace Architect Agent - an Amp-like agent
specialized for Grace development.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

sys.path.append("../..")

from ...grace_architect_agent import grace_architect, GraceArchitectureKnowledge, GraceExtensionRequest
from ...models import async_session
from sqlalchemy import select, desc

async def learn_architecture():
    """Parse Grace codebase and learn architectural patterns"""
    
    print("\n" + "="*80)
    print("GRACE ARCHITECT: LEARNING ARCHITECTURE".center(80))
    print("="*80 + "\n")
    
    print("📚 Analyzing Grace codebase...")
    print("   - Scanning all 12 phases")
    print("   - Extracting integration patterns")
    print("   - Learning constitutional flows")
    print()
    
    result = await grace_architect.learn_grace_architecture()
    
    print("✅ Learning complete!\n")
    print(f"📊 Results:")
    print(f"   Phases analyzed: {result['phases_analyzed']}")
    print(f"   Patterns learned: {result['patterns_learned']}")
    print(f"   Knowledge depth: {result['knowledge_depth']}")
    print()
    
    # Learn from documentation too
    print("📖 Learning from documentation...")
    doc_result = await grace_architect.learn_from_documentation()
    
    print(f"   Documentation files parsed: {doc_result['files_parsed']}")
    print(f"   Integration flows learned: {doc_result['flows_learned']}")
    print()
    
    print("🎓 Grace Architect is now ready to build extensions!")
    print()

async def extend_grace(feature_request: str):
    """Generate a new Grace extension"""
    
    print("\n" + "="*80)
    print("GRACE ARCHITECT: GENERATING EXTENSION".center(80))
    print("="*80 + "\n")
    
    print(f"📝 Request: {feature_request}")
    print()
    
    # Determine business need from context
    business_need = None
    if "market" in feature_request.lower():
        business_need = "Detect business opportunities and market intelligence"
    elif "revenue" in feature_request.lower():
        business_need = "Generate or optimize revenue streams"
    
    extension = await grace_architect.generate_grace_extension(
        feature_request=feature_request,
        business_need=business_need
    )
    
    print("\n" + "="*80)
    print("EXTENSION GENERATED".center(80))
    print("="*80 + "\n")
    
    print(f"✅ {extension['message']}")
    print()
    print(f"📄 Files generated:")
    for file in extension['files_generated']:
        print(f"   - {file}")
    print()
    print(f"🔒 Constitutional compliance: {'✅ YES' if extension['constitutional_compliant'] else '❌ NO'}")
    print(f"🚀 Ready to deploy: {'✅ YES' if extension['ready_to_deploy'] else '⏳ Pending'}")
    print()
    print(f"Extension ID: {extension['request_id']}")
    print()
    print("💡 To view code: grace architect show <extension_id>")
    print("💡 To deploy: grace architect deploy <extension_id>")
    print()

async def show_patterns(category: str = None, phase: int = None):
    """Show learned Grace patterns"""
    
    print("\n" + "="*80)
    print("GRACE ARCHITECTURAL PATTERNS".center(80))
    print("="*80 + "\n")
    
    async with async_session() as session:
        query = select(GraceArchitectureKnowledge)
        
        if category:
            query = query.where(GraceArchitectureKnowledge.category == category)
            print(f"Category: {category}")
        
        if phase:
            query = query.where(GraceArchitectureKnowledge.phase == phase)
            print(f"Phase: {phase}")
        
        query = query.order_by(desc(GraceArchitectureKnowledge.confidence)).limit(50)
        
        result = await session.execute(query)
        patterns = result.scalars().all()
        
        if not patterns:
            print("No patterns found.")
            return
        
        print(f"\nFound {len(patterns)} patterns:\n")
        
        for p in patterns:
            print(f"{'='*80}")
            print(f"🏗️  {p.pattern_name}")
            print(f"{'='*80}")
            print(f"Component: {p.component}")
            print(f"Phase: {p.phase}")
            print(f"Category: {p.category}")
            print(f"Type: {p.knowledge_type}")
            print()
            print(f"Purpose: {p.purpose}")
            print()
            
            if p.code_example:
                print("Code Example:")
                print(f"  {p.code_example}")
                print()
            
            if p.integration_points:
                print("Integration Points:")
                for point in p.integration_points:
                    print(f"  - {point}")
                print()
            
            print(f"Confidence: {p.confidence:.2%}")
            print()

async def list_extensions(status: str = None):
    """List all extension requests"""
    
    print("\n" + "="*80)
    print("GRACE EXTENSIONS".center(80))
    print("="*80 + "\n")
    
    async with async_session() as session:
        query = select(GraceExtensionRequest)
        
        if status:
            query = query.where(GraceExtensionRequest.status == status)
            print(f"Status filter: {status}\n")
        
        query = query.order_by(desc(GraceExtensionRequest.created_at))
        
        result = await session.execute(query)
        extensions = result.scalars().all()
        
        if not extensions:
            print("No extensions found.")
            return
        
        rows = []
        for e in extensions:
            rows.append([
                e.request_id[:20],
                e.feature_request[:40],
                e.status,
                e.risk_level,
                "✅" if e.constitutional_compliant else "❌",
                "✅" if e.deployed else "❌",
                e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else ""
            ])
        
        print(tabulate(
            rows,
            headers=["Extension ID", "Feature", "Status", "Risk", "Constitutional", "Deployed", "Created"],
            tablefmt="grid"
        ))
        
        print(f"\nTotal: {len(extensions)} extensions")
        
        deployed = len([e for e in extensions if e.deployed])
        print(f"Deployed: {deployed}")
        print(f"Pending: {len(extensions) - deployed}")

async def show_extension(extension_id: str):
    """Show extension details and code"""
    
    async with async_session() as session:
        result = await session.execute(
            select(GraceExtensionRequest).where(
                GraceExtensionRequest.request_id.like(f"{extension_id}%")
            )
        )
        extension = result.scalar_one_or_none()
        
        if not extension:
            print(f"❌ Extension not found: {extension_id}")
            return
        
        print("\n" + "="*80)
        print(f"EXTENSION: {extension.request_id}".center(80))
        print("="*80 + "\n")
        
        print(f"Feature: {extension.feature_request}")
        if extension.business_need:
            print(f"Business Need: {extension.business_need}")
        print()
        
        print(f"Status: {extension.status}")
        print(f"Risk Level: {extension.risk_level}")
        print(f"Constitutional Compliant: {'✅ YES' if extension.constitutional_compliant else '❌ NO'}")
        print(f"Governance Approved: {'✅ YES' if extension.governance_approved else '⏳ Pending'}")
        print(f"Deployed: {'✅ YES' if extension.deployed else '❌ NO'}")
        print()
        
        if extension.new_components_needed:
            print("New Components:")
            for comp in extension.new_components_needed:
                print(f"  - {comp}")
            print()
        
        if extension.integration_points:
            print("Integration Points:")
            for point in extension.integration_points:
                print(f"  - {point}")
            print()
        
        print(f"Created: {extension.created_at}")
        if extension.completed_at:
            print(f"Completed: {extension.completed_at}")
        print()
        
        if extension.code_generated:
            print("="*80)
            print("GENERATED CODE")
            print("="*80)
            print()
            print(extension.code_generated)
            print()
        
        if extension.tests_generated:
            print("="*80)
            print("GENERATED TESTS")
            print("="*80)
            print()
            print(extension.tests_generated)
            print()

async def deploy_extension(extension_id: str, skip_parliament: bool = False):
    """Deploy an extension"""
    
    print(f"\n🚀 Deploying extension: {extension_id}\n")
    
    result = await grace_architect.deploy_extension(
        extension_id=extension_id,
        require_parliament=not skip_parliament,
        auto_test=True
    )
    
    if result['status'] == 'success':
        print(f"✅ Extension deployed successfully!")
        print(f"   Files written: {len(result.get('files_written', []))}")
        
        if result.get('parliament_session_id'):
            print(f"   Parliament session: {result['parliament_session_id']}")
        
        if result.get('tests_passed'):
            print(f"   Tests passed: ✅")
        
        print()
    else:
        print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")

async def show_knowledge():
    """Show Grace architectural knowledge base summary"""
    
    print("\n" + "="*80)
    print("GRACE ARCHITECTURAL KNOWLEDGE BASE".center(80))
    print("="*80 + "\n")
    
    async with async_session() as session:
        result = await session.execute(
            select(GraceArchitectureKnowledge)
        )
        all_patterns = result.scalars().all()
        
        if not all_patterns:
            print("No patterns learned yet. Run: grace architect learn")
            return
        
        print(f"📚 Total Patterns: {len(all_patterns)}")
        print()
        
        # By category
        by_category = {}
        for p in all_patterns:
            if p.category:
                by_category[p.category] = by_category.get(p.category, 0) + 1
        
        print("By Category:")
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat:20s} {count:3d} patterns")
        print()
        
        # By phase
        by_phase = {}
        for p in all_patterns:
            if p.phase:
                by_phase[p.phase] = by_phase.get(p.phase, 0) + 1
        
        print("By Phase:")
        for phase in sorted(by_phase.keys()):
            print(f"  Phase {phase:2d}             {by_phase[phase]:3d} patterns")
        print()
        
        # By type
        by_type = {}
        for p in all_patterns:
            by_type[p.knowledge_type] = by_type.get(p.knowledge_type, 0) + 1
        
        print("By Type:")
        for typ, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  {typ:30s} {count:3d}")
        print()
        
        # Statistics
        validated = len([p for p in all_patterns if p.validated])
        avg_conf = sum(p.confidence for p in all_patterns) / len(all_patterns)
        
        print(f"Validated patterns: {validated}/{len(all_patterns)} ({validated/len(all_patterns)*100:.1f}%)")
        print(f"Average confidence: {avg_conf:.2%}")
        print()

def main():
    """CLI entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python -m backend.cli.commands.architect_command <command>")
        print("\nCommands:")
        print("  learn                       - Learn Grace architecture patterns")
        print("  extend \"<description>\"      - Generate new Grace extension")
        print("  patterns [category] [phase] - Show learned patterns")
        print("  extensions [status]         - List all extensions")
        print("  show <extension_id>         - Show extension details and code")
        print("  deploy <extension_id>       - Deploy extension")
        print("  knowledge                   - Show knowledge base summary")
        print("\nExamples:")
        print("  grace architect learn")
        print("  grace architect extend \"market intelligence system\"")
        print("  grace architect patterns security")
        print("  grace architect patterns --phase 1")
        print("  grace architect deploy grace_ext_12345")
        return
    
    command = sys.argv[1]
    
    if command == "learn":
        asyncio.run(learn_architecture())
    
    elif command == "extend":
        if len(sys.argv) < 3:
            print("Usage: grace architect extend \"<feature description>\"")
            return
        feature_request = " ".join(sys.argv[2:])
        asyncio.run(extend_grace(feature_request))
    
    elif command == "patterns":
        category = None
        phase = None
        
        for i, arg in enumerate(sys.argv[2:]):
            if arg == "--category" and i+3 < len(sys.argv):
                category = sys.argv[i+3]
            elif arg == "--phase" and i+3 < len(sys.argv):
                phase = int(sys.argv[i+3])
            elif not arg.startswith("--"):
                # First non-flag arg is category
                if category is None:
                    category = arg
        
        asyncio.run(show_patterns(category, phase))
    
    elif command == "extensions":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(list_extensions(status))
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: grace architect show <extension_id>")
            return
        extension_id = sys.argv[2]
        asyncio.run(show_extension(extension_id))
    
    elif command == "deploy":
        if len(sys.argv) < 3:
            print("Usage: grace architect deploy <extension_id> [--skip-parliament]")
            return
        extension_id = sys.argv[2]
        skip_parliament = "--skip-parliament" in sys.argv
        asyncio.run(deploy_extension(extension_id, skip_parliament))
    
    elif command == "knowledge":
        asyncio.run(show_knowledge())
    
    else:
        print(f"Unknown command: {command}")
        print("Run without args for usage help.")

if __name__ == "__main__":
    main()
