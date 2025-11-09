# Meta-Loop System Architecture

## System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                      GRACE OPERATIONAL LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Reflection  │  │   Learning   │  │  Task Exec   │  ...          │
│  │  Service     │  │   Engine     │  │   Engine     │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
└─────────┼──────────────────┼──────────────────┼───────────────────────┘
          │ generates        │ creates          │ executes
          │ reflections      │ tasks            │ tasks
          │                  │                  │
          ▼ monitors         ▼ monitors         ▼ monitors
┌──────────────────────────────────────────────────────────────────────┐
│                  LEVEL 1: META-LOOP ENGINE                           │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  meta_loop.py - MetaLoopEngine (runs every 300s)              │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  analyze_and_optimize()                                   │ │  │
│  │  │    ├─ _analyze_task_completion_rate()                     │ │  │
│  │  │    │    └─ If <30% → Recommend: increase threshold       │ │  │
│  │  │    ├─ _analyze_reflection_utility()                       │ │  │
│  │  │    │    └─ If reflections not creating tasks             │ │  │
│  │  │    │         → Recommend: lower threshold                │ │  │
│  │  │    └─ _submit_actionable_recommendation()                │ │  │
│  │  │         └─ Convert analysis to actionable rec            │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │ submits recommendations
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  RECOMMENDATION PIPELINE                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  meta_loop_approval.py - ApprovalQueue                         │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  1. submit_for_approval()                                 │ │  │
│  │  │     ├─ Create RecommendationQueue entry                   │ │  │
│  │  │     ├─ Assess risk: low/medium/high                       │ │  │
│  │  │     └─ Check auto-approval criteria                       │ │  │
│  │  │                                                            │ │  │
│  │  │  2. Decision Branch:                                      │ │  │
│  │  │     ├─ If low-risk + high-confidence (≥0.8)              │ │  │
│  │  │     │   └─ auto_approve_safe_changes()                    │ │  │
│  │  │     └─ Else: await manual review                          │ │  │
│  │  │                                                            │ │  │
│  │  │  3. approve_recommendation() / reject_recommendation()    │ │  │
│  │  │     ├─ Manual approval via API                            │ │  │
│  │  │     ├─ Check governance policies                          │ │  │
│  │  │     └─ If approved → proceed to application               │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │ if approved
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  GOVERNANCE & SAFETY CHECKS                          │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  governance.py - GovernanceEngine                              │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  check(actor, action, resource, payload)                  │ │  │
│  │  │    ├─ Match against policies                              │ │  │
│  │  │    ├─ meta_loop_high_risk_review → Require review         │ │  │
│  │  │    ├─ meta_loop_interval_critical → Deny if <30s          │ │  │
│  │  │    └─ Return: allow / deny / review                       │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │ if allowed
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  APPLICATION ENGINE                                  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  meta_loop_engine.py - RecommendationApplicator                │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  1. validate_recommendation()                             │ │  │
│  │  │     └─ Check against safety_limits                        │ │  │
│  │  │                                                            │ │  │
│  │  │  2. measure_before_metrics()                              │ │  │
│  │  │     └─ Capture: tasks, completion rate, reflections       │ │  │
│  │  │                                                            │ │  │
│  │  │  3. Apply change:                                         │ │  │
│  │  │     ├─ apply_threshold_change()                           │ │  │
│  │  │     ├─ apply_interval_change()                            │ │  │
│  │  │     └─ apply_priority_change()                            │ │  │
│  │  │         └─ Update MetaLoopConfig                          │ │  │
│  │  │         └─ Restart loops if needed                        │ │  │
│  │  │                                                            │ │  │
│  │  │  4. Create AppliedRecommendation record                   │ │  │
│  │  │     └─ Store: old_value, new_value, before_metrics        │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  VERIFICATION & AUDIT                                │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  verification.py - VerificationService                         │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  sign_event()                                             │ │  │
│  │  │    ├─ Event: meta.recommendation_applied                  │ │  │
│  │  │    ├─ Payload: rec_id, type, values, governance_audit_id │ │  │
│  │  │    ├─ Generate cryptographic signature                    │ │  │
│  │  │    └─ Store in immutable verification log                 │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │
                  wait 24 hours
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  EFFECTIVENESS MEASUREMENT                           │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  meta_loop_engine.py - RecommendationApplicator                │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  measure_after_metrics(applied_id)                        │ │  │
│  │  │    ├─ Capture: tasks, completion rate, reflections        │ │  │
│  │  │    ├─ Compare before vs after                             │ │  │
│  │  │    ├─ Calculate effectiveness: (after-before)/before*100  │ │  │
│  │  │    └─ Update AppliedRecommendation.effectiveness_score    │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  LEVEL 2: META-META ENGINE                           │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  meta_loop.py - MetaMetaEngine                                 │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  evaluate_improvement(meta_analysis_id, metric, before,   │ │  │
│  │  │                       after)                               │ │  │
│  │  │    ├─ Calculate improvement percentage                     │ │  │
│  │  │    ├─ Determine conclusion:                                │ │  │
│  │  │    │   ├─ >+10% → "Improvement"                           │ │  │
│  │  │    │   ├─ -10 to +10% → "No significant change"           │ │  │
│  │  │    │   └─ <-10% → "Regression"                            │ │  │
│  │  │    ├─ Store MetaMetaEvaluation                             │ │  │
│  │  │    └─ If <-20%:                                            │ │  │
│  │  │        ├─ Trigger auto-rollback                            │ │  │
│  │  │        └─ Publish meta.regression_detected event           │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────────────┘
                           │
           ┌───────────────┴────────────────┐
           │                                │
           ▼ improvement                    ▼ regression
    ┌─────────────┐                  ┌─────────────┐
    │  Continue   │                  │  Rollback   │
    │  Monitoring │                  │  Change     │
    └─────────────┘                  └─────────────┘
```

## Data Flow

### Recommendation Submission Flow

```
MetaAnalysis
    │
    ├─ analysis_type: "task_effectiveness"
    ├─ subject: "auto_task_generation"
    ├─ findings: "Only 25% completed"
    ├─ recommendation: "Increase threshold 3→5"
    └─ confidence: 0.75
    
    ↓ _submit_actionable_recommendation()
    
RecommendationQueue
    │
    ├─ meta_analysis_id: 1
    ├─ recommendation_type: "threshold_change"
    ├─ target: "task_threshold"
    ├─ current_value: "3"
    ├─ proposed_value: "5"
    ├─ confidence: 0.75
    ├─ risk_level: "medium"
    └─ status: "pending"
    
    ↓ approve_recommendation()
    
AppliedRecommendation
    │
    ├─ meta_analysis_id: 1
    ├─ recommendation_type: "threshold_change"
    ├─ target: "learning.task_threshold"
    ├─ old_value: "3"
    ├─ new_value: "5"
    ├─ before_metrics: {tasks: 50, completed: 15, rate: 0.30}
    ├─ after_metrics: {tasks: 40, completed: 25, rate: 0.625}
    ├─ effectiveness_score: 108.3
    └─ rolled_back: false
    
    ↓ evaluate_improvement()
    
MetaMetaEvaluation
    │
    ├─ meta_analysis_id: 1
    ├─ metric_name: "task_completion_rate"
    ├─ before_value: 0.30
    ├─ after_value: 0.625
    ├─ improvement: 108.3
    └─ conclusion: "Improvement"
```

## API Layer

```
┌──────────────────────────────────────────────────────────┐
│              REST API (routes/meta_api.py)               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  GET /api/meta/recommendations/pending                   │
│    └─ approval_queue.get_pending_recommendations()       │
│                                                          │
│  POST /api/meta/recommendations/{id}/approve             │
│    ├─ Auth check                                         │
│    └─ approval_queue.approve_recommendation()            │
│        ├─ governance.check()                             │
│        ├─ applicator.apply_*()                           │
│        └─ verification.sign_event()                      │
│                                                          │
│  POST /api/meta/recommendations/{id}/reject              │
│    └─ approval_queue.reject_recommendation()             │
│                                                          │
│  GET /api/meta/recommendations/applied                   │
│    └─ approval_queue.get_applied_recommendations()       │
│                                                          │
│  POST /api/meta/recommendations/{id}/rollback            │
│    └─ applicator.rollback_change()                       │
│                                                          │
│  GET /api/meta/recommendations/stats                     │
│    └─ Query database for counts & averages               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Safety System

```
┌────────────────────────────────────────────────────────┐
│                  SAFETY LAYERS                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Layer 1: Validation                                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │  validate_recommendation()                        │ │
│  │    └─ Check against safety_limits:               │ │
│  │         ├─ task_threshold: [1, 10]               │ │
│  │         ├─ reflection_interval: [10, 3600]       │ │
│  │         └─ task_priority: [1, 10]                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Layer 2: Risk Assessment                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │  _assess_risk()                                   │ │
│  │    ├─ interval < 30s → high                      │ │
│  │    ├─ confidence < 0.5 → high                    │ │
│  │    ├─ confidence < 0.7 → medium                  │ │
│  │    └─ else → low                                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Layer 3: Governance                                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │  governance.check()                               │ │
│  │    ├─ High-risk → Review required                │ │
│  │    ├─ Interval <30s → Deny                       │ │
│  │    └─ All changes → Audit log                    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Layer 4: Metrics Tracking                             │
│  ┌──────────────────────────────────────────────────┐ │
│  │  measure_before_metrics()                         │ │
│  │  measure_after_metrics()                          │ │
│  │    └─ Track: tasks, completion, reflections      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Layer 5: Auto-Rollback                                │
│  ┌──────────────────────────────────────────────────┐ │
│  │  If effectiveness < -20%:                         │ │
│  │    ├─ rollback_change()                           │ │
│  │    ├─ Revert to old_value                         │ │
│  │    └─ Publish regression event                    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Layer 6: Cryptographic Verification                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │  verification.sign_event()                        │ │
│  │    ├─ Immutable audit trail                       │ │
│  │    └─ Non-repudiation guarantee                   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Integration Map

```
Meta-Loop System
    │
    ├─→ Reflection Service
    │     └─ Can adjust: reflection_interval
    │
    ├─→ Learning Engine
    │     └─ Can adjust: task_threshold
    │
    ├─→ Task Executor
    │     └─ Can adjust: task_priority
    │
    ├─→ Governance Engine
    │     ├─ Enforces: meta_loop_high_risk_review
    │     ├─ Enforces: meta_loop_interval_critical
    │     └─ Logs: All meta-changes
    │
    ├─→ Verification Service
    │     └─ Signs: meta.recommendation_applied
    │
    └─→ Trigger Mesh
          └─ Publishes: meta.regression_detected
```

## Database Schema Relationships

```
meta_analyses
    │
    └─ meta_analysis_id
        │
        ├─→ recommendation_queue
        │     ├─ status: pending/approved/rejected
        │     └─ (if approved) →
        │
        ├─→ applied_recommendations
        │     ├─ before_metrics: JSON
        │     ├─ after_metrics: JSON
        │     ├─ effectiveness_score: FLOAT
        │     └─ rolled_back: BOOLEAN
        │
        └─→ meta_meta_evaluations
              ├─ before_value: FLOAT
              ├─ after_value: FLOAT
              ├─ improvement: FLOAT
              └─ conclusion: TEXT
```

## Summary

This architecture provides:
- ✅ **Automated Analysis** - Continuous monitoring every 300s
- ✅ **Risk-Based Routing** - Auto-approve safe, manual review risky
- ✅ **Multi-Layer Safety** - Validation, governance, metrics, rollback
- ✅ **Effectiveness Tracking** - Before/after metrics with evaluation
- ✅ **Self-Correction** - Auto-rollback on regression
- ✅ **Complete Audit Trail** - Cryptographically signed changes
- ✅ **Human Oversight** - Manual approval for critical changes

**Result:** GRACE autonomously optimizes itself while maintaining safety and accountability.
