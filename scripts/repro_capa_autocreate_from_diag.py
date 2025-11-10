import asyncio
import os
from backend.integrations.capa_system import auto_create_from_diagnostic, ENABLE_CAPA_AUTOCREATE


async def main():
    print(f"ENABLE_CAPA_AUTOCREATE={ENABLE_CAPA_AUTOCREATE} (set via env)")
    
    # Simulate a critical diagnostic finding
    diagnostic = {
        "diagnosis": "sql_injection_vulnerability",
        "severity": "critical",
        "status": "failed",
        "details": "SQL injection vector detected in user input handler",
        "summary": "Critical security flaw allowing unauthorized database access",
    }
    
    print(f"\nSimulating critical diagnostic: {diagnostic['diagnosis']}")
    ticket = await auto_create_from_diagnostic(diagnostic)
    
    if ticket:
        print(f"\n✓ CAPA ticket auto-created:")
        print(f"  ID: {ticket.id}")
        print(f"  Title: {ticket.title}")
        print(f"  Category: {ticket.category}")
        print(f"  Severity: {ticket.severity}")
        print(f"  Status: {ticket.status}")
    else:
        print("\n✗ No CAPA ticket created (feature disabled or diagnostic not eligible)")
    
    # Test with non-critical diagnostic (should not create ticket)
    print("\n\nTesting with low-severity diagnostic (should not create):")
    low_diag = {
        "diagnosis": "minor_latency_increase",
        "severity": "low",
        "status": "degraded",
        "details": "Slight increase in response time",
    }
    ticket2 = await auto_create_from_diagnostic(low_diag)
    if ticket2:
        print(f"  Unexpected: ticket created for low severity")
    else:
        print(f"  ✓ Correctly skipped low-severity diagnostic")


if __name__ == "__main__":
    asyncio.run(main())
