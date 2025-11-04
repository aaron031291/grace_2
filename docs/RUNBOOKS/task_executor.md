# Task Executor Stall Runbook

## Detect
- `task_executor` logger reports 0 workers running.
- `/api/executor/tasks` shows queued tasks with no progress.
- Health monitor emits `restart_task_workers` actions.

## Stabilise
- Pause new orchestrator submissions if possible.
- Notify affected users (tasks may need resubmission).

## Remediate
1. Restart workers:
   ```bash
   py scripts/reset_task_executor.py  # TODO: AMP to implement if needed
   ```
   or via API: `await task_executor.stop_workers(); await task_executor.start_workers()`.
2. Check database table `execution_tasks` for stuck records;
   clear rows with status `running` older than 1 hour.
3. If recurring:
   - Inspect logs for exceptions thrown by task functions.
   - Scale `task_executor.max_parallel` if backlog legitimate.

## Postmortem
- Attach log excerpts with request IDs.
- Record root cause (code bug, resource exhaustion, external dependency).
- Create follow-up ticket to harden worker restart automation if manual steps were required.
