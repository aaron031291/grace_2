# Continuous Validation Loop

| Cadence | Action |
| --- | --- |
| Daily | Run `./scripts/continuous_validation.sh` (CI scheduled) |
| Weekly | Chaos drill: stop task executor + verify auto-recovery; review Hunter alerts |
| Monthly | Refresh dependencies (`./scripts/freeze_dependencies.sh`) and review audit exports |

Log results in the ops channel with links to generated reports under `reports/continuous_validation/`.
