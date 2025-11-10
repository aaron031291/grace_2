import asyncio
import os

# Ensure the feature flag is enabled for this repro
os.environ.setdefault("ENABLE_CAPA_AUTOCREATE", "1")

from backend.integrations.capa_system import auto_create_from_diagnostic


async def main():
    diag = {
        "severity": "critical",
        "status": "degraded",
        "diagnosis": "latency_spike",
        "details": "p95 latency > 2s for backend_api",
    }
    ticket = await auto_create_from_diagnostic(diag)
    if ticket is None:
        print("No CAPA created (feature flag disabled or diagnostic not eligible)")
    else:
        try:
            print(ticket.model_dump())
        except Exception:
            print(vars(ticket))


if __name__ == "__main__":
    asyncio.run(main())
