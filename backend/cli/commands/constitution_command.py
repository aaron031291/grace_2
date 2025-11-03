"""Constitutional AI CLI Commands

CLI interface for viewing constitution, checking compliance,
and managing clarifications.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from tabulate import tabulate

sys.path.append("../..")

from ...constitutional_verifier import constitutional_verifier
from ...constitutional_engine import constitutional_engine
from ...clarifier import clarifier
from ...models import async_session
from ...constitutional_models import ConstitutionalPrinciple, ConstitutionalViolation, ClarificationRequest
from sqlalchemy import select, desc

async def show_constitution():
    """Display full constitution"""
    
    print("\n" + "="*80)
    print("GRACE CONSTITUTIONAL AI FRAMEWORK".center(80))
    print("="*80 + "\n")
    
    async with async_session() as session:
        # Get all principles by level
        for level in ["foundational", "operational", "safety"]:
            result = await session.execute(
                select(ConstitutionalPrinciple).where(
                    ConstitutionalPrinciple.principle_level == level,
                    ConstitutionalPrinciple.active == True
                ).order_by(ConstitutionalPrinciple.id)
            )
            principles = result.scalars().all()
            
            if not principles:
                continue
            
            print(f"\n{'='*80}")
            print(f"{level.upper()} PRINCIPLES ({len(principles)})".center(80))
            print(f"{'='*80}\n")
            
            for p in principles:
                print(f"📜 {p.title}")
                print(f"   Name: {p.principle_name}")
                print(f"   Description: {p.description}")
                print(f"   Enforcement: {p.enforcement_type}")
                print(f"   Severity: {p.severity}")
                if p.rationale:
                    print(f"   Rationale: {p.rationale}")
                if p.immutable:
                    print(f"   🔒 IMMUTABLE - Cannot be changed")
                print()

async def check_compliance(action_type: str):
    """Check if an action type would be compliant"""
    
    print(f"\n🔍 Checking compliance for action: {action_type}\n")
    
    result = await constitutional_verifier.verify_action(
        actor="cli_user",
        action_type=action_type,
        resource="test_resource",
        payload={"test": True},
        confidence=1.0,
        context={}
    )
    
    if result['allowed']:
        print("✅ Action ALLOWED")
        print(f"   Compliant: {result['compliant']}")
    else:
        print("❌ Action BLOCKED")
        print(f"   Compliant: {result['compliant']}")
    
    if result['violations']:
        print(f"\n⚠️  Violations ({len(result['violations'])}):")
        for v in result['violations']:
            print(f"   - {v.get('principle', 'Unknown')}: {v.get('reason', 'No reason')}")
    
    if result['warnings']:
        print(f"\n⚡ Warnings ({len(result['warnings'])}):")
        for w in result['warnings']:
            print(f"   - {w.get('type', 'Unknown')}: {w.get('message', 'No message')}")
    
    if result['constitutional_check']:
        check = result['constitutional_check']
        print(f"\nConstitutional Compliance Score: {check['compliance_score']:.2%}")
        print(f"Principles Checked: {len(check['principles_checked'])}")
        print(f"Principles Passed: {len(check['principles_passed'])}")
        print(f"Principles Failed: {len(check['principles_failed'])}")

async def list_violations(limit: int = 50):
    """List recent violations"""
    
    print(f"\n📋 Recent Constitutional Violations (last {limit})\n")
    
    async with async_session() as session:
        result = await session.execute(
            select(ConstitutionalViolation)
            .order_by(desc(ConstitutionalViolation.created_at))
            .limit(limit)
        )
        violations = result.scalars().all()
        
        if not violations:
            print("No violations found.")
            return
        
        rows = []
        for v in violations:
            rows.append([
                v.id,
                v.principle.principle_name if v.principle else "Unknown",
                v.actor,
                v.action,
                v.severity,
                "✅" if v.blocked else "❌",
                v.created_at.strftime("%Y-%m-%d %H:%M")
            ])
        
        print(tabulate(
            rows,
            headers=["ID", "Principle", "Actor", "Action", "Severity", "Blocked", "Time"],
            tablefmt="grid"
        ))
        
        print(f"\nTotal: {len(violations)} violations")
        
        # Statistics
        blocked = len([v for v in violations if v.blocked])
        print(f"Blocked: {blocked} ({blocked/len(violations)*100:.1f}%)")
        
        by_severity = {}
        for v in violations:
            by_severity[v.severity] = by_severity.get(v.severity, 0) + 1
        
        print(f"\nBy Severity:")
        for severity, count in sorted(by_severity.items()):
            print(f"  {severity}: {count}")

async def list_clarifications():
    """List pending clarifications"""
    
    print("\n💬 Pending Clarification Requests\n")
    
    async with async_session() as session:
        result = await session.execute(
            select(ClarificationRequest)
            .where(ClarificationRequest.status == "pending")
            .order_by(desc(ClarificationRequest.created_at))
        )
        requests = result.scalars().all()
        
        if not requests:
            print("No pending clarifications.")
            return
        
        for req in requests:
            print(f"{'='*80}")
            print(f"Request ID: {req.request_id}")
            print(f"User: {req.user}")
            print(f"Type: {req.uncertainty_type}")
            print(f"Confidence: {req.confidence_score:.2%}")
            print(f"\nOriginal Input: {req.original_input}")
            print(f"\nQuestion: {req.question}")
            
            if req.options:
                print(f"\nOptions:")
                for i, option in enumerate(req.options, 1):
                    print(f"  {i}. {option}")
            
            if req.context_provided:
                print(f"\nContext: {req.context_provided}")
            
            print(f"\nCreated: {req.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Timeout: {req.timeout_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

async def show_stats():
    """Show constitutional metrics"""
    
    print("\n" + "="*80)
    print("CONSTITUTIONAL AI STATISTICS".center(80))
    print("="*80 + "\n")
    
    async with async_session() as session:
        # Principles count
        result = await session.execute(
            select(ConstitutionalPrinciple).where(ConstitutionalPrinciple.active == True)
        )
        principles = result.scalars().all()
        
        print(f"📜 Active Principles: {len(principles)}")
        
        by_level = {}
        for p in principles:
            by_level[p.principle_level] = by_level.get(p.principle_level, 0) + 1
        
        for level, count in sorted(by_level.items()):
            print(f"   {level}: {count}")
        
        # Violations (last 7 days)
        since = datetime.utcnow() - timedelta(days=7)
        result = await session.execute(
            select(ConstitutionalViolation).where(
                ConstitutionalViolation.created_at >= since
            )
        )
        recent_violations = result.scalars().all()
        
        print(f"\n⚠️  Violations (last 7 days): {len(recent_violations)}")
        
        if recent_violations:
            blocked = len([v for v in recent_violations if v.blocked])
            print(f"   Blocked: {blocked}")
            print(f"   Allowed: {len(recent_violations) - blocked}")
            
            by_severity = {}
            for v in recent_violations:
                by_severity[v.severity] = by_severity.get(v.severity, 0) + 1
            
            print(f"\n   By Severity:")
            for severity, count in sorted(by_severity.items()):
                print(f"     {severity}: {count}")
        
        # Clarifications
        result = await session.execute(
            select(ClarificationRequest).where(
                ClarificationRequest.status == "pending"
            )
        )
        pending = result.scalars().all()
        
        print(f"\n💬 Pending Clarifications: {len(pending)}")
        
        # Compliance rate (last 30 days)
        from ...constitutional_models import ConstitutionalCompliance
        
        since_month = datetime.utcnow() - timedelta(days=30)
        result = await session.execute(
            select(ConstitutionalCompliance).where(
                ConstitutionalCompliance.created_at >= since_month
            )
        )
        compliance_records = result.scalars().all()
        
        if compliance_records:
            compliant = len([r for r in compliance_records if r.compliant])
            rate = (compliant / len(compliance_records) * 100)
            print(f"\n📊 Compliance Rate (30 days): {rate:.2f}%")
            print(f"   Total Actions: {len(compliance_records)}")
            print(f"   Compliant: {compliant}")
            print(f"   Non-Compliant: {len(compliance_records) - compliant}")

async def answer_clarification(request_id: str, response: str):
    """Answer a pending clarification"""
    
    try:
        result = await constitutional_engine.answer_clarification(
            request_id=request_id,
            user_response=response
        )
        
        print(f"\n✅ Clarification answered")
        print(f"   Request ID: {result['request_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Original Input: {result['original_input']}")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")

def main():
    """CLI entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python -m cli.commands.constitution_command <command>")
        print("\nCommands:")
        print("  show                    - Display full constitution")
        print("  check <action_type>     - Check compliance for action")
        print("  violations [limit]      - List recent violations")
        print("  clarify                 - List pending clarifications")
        print("  answer <id> <response>  - Answer a clarification")
        print("  stats                   - Show constitutional metrics")
        return
    
    command = sys.argv[1]
    
    if command == "show":
        asyncio.run(show_constitution())
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Usage: constitution check <action_type>")
            return
        action_type = sys.argv[2]
        asyncio.run(check_compliance(action_type))
    
    elif command == "violations":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        asyncio.run(list_violations(limit))
    
    elif command == "clarify":
        asyncio.run(list_clarifications())
    
    elif command == "answer":
        if len(sys.argv) < 4:
            print("Usage: constitution answer <request_id> <response>")
            return
        request_id = sys.argv[2]
        response = " ".join(sys.argv[3:])
        asyncio.run(answer_clarification(request_id, response))
    
    elif command == "stats":
        asyncio.run(show_stats())
    
    else:
        print(f"Unknown command: {command}")
        print("Run without args for usage help.")

if __name__ == "__main__":
    main()
