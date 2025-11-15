# Layer 1 Chaos Testing

The chaos runner exercises Grace's core kernels by injecting concurrent failure
scenarios and recording the outcome for forensic analysis.

## Running a Wave

```bash
python -m backend.chaos.chaos_runner
```

Arguments can be supplied programmatically when importing `ChaosRunner`:

```python
from backend.chaos import ChaosRunner
import asyncio

async def main():
    runner = ChaosRunner()
    await runner.run_wave(wave_size=3)  # run 3 concurrent scenarios

asyncio.run(main())
```

## Scenario Catalogue

Scenarios live in `backend/chaos/scenarios.yaml`. Each entry provides:

- `injection`: how to introduce the fault (`pause_kernel`, `spam_topic`,
  `corrupt_snapshot`, etc.)
- `verification`: checks that must pass after the fault
- `severity` / `category`: used to filter waves

## Telemetry & Logging

Every scenario write-up includes:

- JSON log per execution under `logs/chaos/*.json`
- Immutable log entry (`actor=chaos_runner`, `action=chaos_scenario`)

These artifacts capture:

- injection parameters
- verification results
- total duration
- success / attention / error status

## Integration Hooks

- Uses `control_plane.pause_kernel` / `resume_kernel` to stress watchdogs
- Publishes high-priority floods through `message_bus`
- Manipulates `.grace_snapshots/models` artifacts to challenge self-healing

Extend the system by adding new scenario definitions and injection/verification
handlers in `backend/chaos/chaos_runner.py`.
