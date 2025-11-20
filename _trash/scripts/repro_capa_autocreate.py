import asyncio
from backend.integrations.capa_system import CAPASystem


async def main():
    capa = CAPASystem()
    ticket = await capa.create_capa(
        title="Critical: Config tampering detected",
        description="Forensic sweep found unauthorized change in prod config",
        severity="critical",
        category="security",
        tags=["forensics", "auto"],
        metadata={"component": "config_watcher", "sweep_id": "demo_123"},
    )
    try:
        # Pydantic v2 path
        print(ticket.model_dump())
    except Exception:
        # Fallback simple dataclass-ish
        print(vars(ticket))


if __name__ == "__main__":
    asyncio.run(main())
