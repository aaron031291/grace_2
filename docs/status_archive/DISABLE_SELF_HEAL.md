# Disable Self-Healing on Startup

To prevent self-healing from running automatically on startup, add these environment variables to your `.env` file:

## Quick Disable (Recommended)

Add to `.env`:

```bash
# Disable self-healing features
SELF_HEAL_OBSERVE_ONLY=false
SELF_HEAL_EXECUTE=false
```

## What This Does

- **SELF_HEAL_OBSERVE_ONLY=false** - Disables the self-heal scheduler (log-only mode)
- **SELF_HEAL_EXECUTE=false** - Disables self-heal execution (fix mode)

## Partial Disable Options

### Keep Observe-Only (logs issues but doesn't fix)
```bash
SELF_HEAL_OBSERVE_ONLY=true
SELF_HEAL_EXECUTE=false
```

### Full Auto-Healing (default)
```bash
SELF_HEAL_OBSERVE_ONLY=true
SELF_HEAL_EXECUTE=true
```

## How to Apply

1. Open `.env` file:
   ```powershell
   notepad .env
   ```

2. Add the disable flags:
   ```
   SELF_HEAL_OBSERVE_ONLY=false
   SELF_HEAL_EXECUTE=false
   ```

3. Save and restart Grace:
   ```powershell
   .\GRACE.ps1 -Stop
   .\GRACE.ps1
   ```

## What Gets Disabled

When both are set to `false`:
- ✗ Self-heal scheduler (stops monitoring for issues)
- ✗ Self-heal execution (stops automatic fixes)
- ✓ Manual healing via API still works
- ✓ Proactive intelligence still runs
- ✓ Autonomous improver still runs
- ✓ Meta loop still runs

## Re-enable Later

Simply remove the lines from `.env` or set them to `true`:

```bash
SELF_HEAL_OBSERVE_ONLY=true
SELF_HEAL_EXECUTE=true
```

## Check Current Status

```powershell
# View self-heal status
Invoke-RestMethod http://localhost:8000/health | ConvertTo-Json
```
