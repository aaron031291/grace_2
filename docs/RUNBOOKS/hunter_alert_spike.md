# Hunter Alert Spike Runbook

## Detect
- Hunter dashboard red or >10 critical alerts in <5 minutes.
- `hunter` logger emitting `alert_and_block` events repeatedly.

## Stabilise
- Engage security lead and review latest alerts via `/api/hunter/alerts`.
- Pause automation that auto-remediates (`auto_fix`, `auto_quarantine`) if causing churn.

## Remediate
1. Confirm alerts are genuine: sample payloads, check source actors.
2. For false positives:
   - Adjust relevant rule via governance approval.
   - Document reason in GovernancePolicy notes.
3. For true positives:
   - Run `py scripts/promote_user.py` if admin intervention needed.
   - Use auto-quarantine or manual mitigation instructions.

## Postmortem
- Update `Hunter` metrics to capture alert volume vs. resolved.
- Schedule rules review if two spikes occur within a week.
- Capture lessons learned in security weekly notes.
