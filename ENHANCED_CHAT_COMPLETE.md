# Enhanced Chat Experience Complete ✅

Live metrics, inline approvals, and embedded error logs now included in every chat response.

---

## Enhanced Response Structure

```json
{
  "reply": "Grace's response with markdown formatting",
  "trace_id": "chat_abc123def456",
  "session_id": "session_xyz789",
  
  // ✅ NEW: Live Metrics (always included)
  "live_metrics": {
    "trust_score": 0.87,
    "confidence": 0.92,
    "guardian_health": "healthy",
    "active_learning_jobs": 3,
    "pending_approvals_count": 1,
    "incidents": 0,
    "timestamp": "2025-11-19T02:00:00.000Z"
  },
  
  // ✅ NEW: Inline Approval Cards
  "inline_approvals": [
    {
      "trace_id": "action_xyz789",
      "action_type": "database_write",
      "tier": "2",
      "description": "Database Write",
      "justification": "User requested to update customer records",
      "params": {
        "table": "customers",
        "operation": "update"
      },
      "risk_level": "medium",
      "requires_approval": true,
      "timestamp": "2025-11-19T02:00:00.000Z"
    }
  ],
  
  // ✅ NEW: Embedded Error Logs
  "error_logs": [
    {
      "log_type": "error",
      "severity": "error",
      "timestamp": "2025-11-19T01:59:45.000Z",
      "message": "Database connection timeout after 30s",
      "stack_trace": "Traceback (most recent call last):\\n  File ...",
      "source": "postgres_connector",
      "context": {
        "database": "production_db",
        "query": "SELECT * FROM users",
        "timeout_seconds": 30
      }
    }
  ],
  "has_errors": false,
  
  // Existing fields
  "actions": [...],
  "citations": ["source1.pdf"],
  "confidence": 0.92,
  "requires_approval": true,
  "pending_approvals": [...],
  "timestamp": "2025-11-19T02:00:00.000Z"
}
```

---

## Feature 1: Live Metrics

### Always Visible System State

Every chat response includes real-time metrics so you always know Grace's current state.

**Backend:**
```python
live_metrics = LiveMetrics(
    trust_score=0.87,              # System trust (0.0-1.0)
    confidence=0.92,               # Response confidence
    guardian_health="healthy",     # healthy|degraded|offline
    active_learning_jobs=3,        # Currently running jobs
    pending_approvals_count=1,     # Actions awaiting approval
    incidents=0,                   # Active incidents
    timestamp=datetime.now().isoformat()
)
```

**Frontend Display:**
```typescript
function ChatMessage({ message }) {
  const metrics = message.live_metrics;
  
  return (
    <div className="message">
      <div className="message-content">{message.reply}</div>
      
      {/* Live metrics bar */}
      <div className="live-metrics">
        <MetricBadge 
          icon="🛡️" 
          label="Trust" 
          value={`${(metrics.trust_score * 100).toFixed(0)}%`}
          color={metrics.trust_score >= 0.7 ? 'green' : 'yellow'}
        />
        <MetricBadge 
          icon="✓" 
          label="Confidence" 
          value={`${(metrics.confidence * 100).toFixed(0)}%`}
        />
        <MetricBadge 
          icon="📚" 
          label="Learning" 
          value={metrics.active_learning_jobs}
        />
        {metrics.pending_approvals_count > 0 && (
          <MetricBadge 
            icon="⏳" 
            label="Approvals" 
            value={metrics.pending_approvals_count}
            color="orange"
          />
        )}
      </div>
    </div>
  );
}
```

**Visual Example:**
```
┌──────────────────────────────────────────────────┐
│ Grace: I've analyzed the Q3 data. Revenue is up  │
│ 15% year-over-year, with strong product sales.  │
│                                                  │
│ 🛡️ Trust: 87% | ✓ Confidence: 92% | 📚 Learning: 3 │
└──────────────────────────────────────────────────┘
```

---

## Feature 2: Inline Approval Cards

### Approve/Reject Right in the Chat

When Grace proposes a Tier 2/3 action, an approval card appears directly under her message.

**Approval Card Structure:**
```typescript
interface ApprovalCard {
  trace_id: string;           // "action_xyz789"
  action_type: string;        // "database_write"
  tier: string;               // "2" or "3"
  description: string;        // "Database Write"
  justification: string;      // Why this action is needed
  params: object;             // Action parameters
  risk_level: string;         // "medium" or "high"
  requires_approval: boolean; // true
  timestamp: string;
}
```

**Frontend Component:**
```typescript
function ApprovalCardComponent({ card, onApprove, onReject }) {
  return (
    <div className={`approval-card risk-${card.risk_level}`}>
      <div className="card-header">
        <span className="icon">⚠️</span>
        <span className="title">{card.description}</span>
        <span className={`tier tier-${card.tier}`}>Tier {card.tier}</span>
      </div>
      
      <div className="card-body">
        <p className="justification">{card.justification}</p>
        
        {Object.keys(card.params).length > 0 && (
          <details className="params">
            <summary>Parameters</summary>
            <pre>{JSON.stringify(card.params, null, 2)}</pre>
          </details>
        )}
      </div>
      
      <div className="card-actions">
        <button 
          className="btn-approve" 
          onClick={() => onApprove(card.trace_id)}
        >
          ✓ Approve
        </button>
        <button 
          className="btn-reject" 
          onClick={() => onReject(card.trace_id)}
        >
          ✗ Reject
        </button>
      </div>
    </div>
  );
}
```

**Visual Example:**
```
┌──────────────────────────────────────────────────┐
│ Grace: I can update those customer records for   │
│ you. This requires database write access.        │
└──────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────┐
│ ⚠️ Database Write                      [Tier 2] │
│                                                  │
│ User requested to update customer records        │
│                                                  │
│ ▼ Parameters                                     │
│   table: "customers"                             │
│   operation: "update"                            │
│                                                  │
│  [✓ Approve]  [✗ Reject]                        │
└──────────────────────────────────────────────────┘
```

**Approval Handler:**
```typescript
async function handleApprove(traceId: string) {
  const response = await fetch('/api/chat/approve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      trace_id: traceId,
      approved: true,
      user_id: 'user'
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    showToast('✓ Action approved and executed');
    refreshMessages();
  }
}
```

---

## Feature 3: Embedded Error Logs

### Stack Traces Right in the Chat

When errors occur, Grace shows you the stack trace and context inline.

**Log Excerpt Structure:**
```typescript
interface LogExcerpt {
  log_type: string;           // "error"
  severity: string;           // "error", "warning", "critical"
  timestamp: string;
  message: string;            // Error message
  stack_trace?: string;       // Full stack trace
  source: string;             // Component that errored
  context: object;            // Additional context
}
```

**Frontend Component:**
```typescript
function ErrorLogComponent({ log }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className={`error-log severity-${log.severity}`}>
      <div className="log-header" onClick={() => setExpanded(!expanded)}>
        <span className="icon">❌</span>
        <span className="message">{log.message}</span>
        <span className="source">from {log.source}</span>
        <span className="expand">{expanded ? '▼' : '▶'}</span>
      </div>
      
      {expanded && (
        <div className="log-details">
          <div className="timestamp">
            {new Date(log.timestamp).toLocaleString()}
          </div>
          
          {log.context && Object.keys(log.context).length > 0 && (
            <div className="context">
              <strong>Context:</strong>
              <pre>{JSON.stringify(log.context, null, 2)}</pre>
            </div>
          )}
          
          {log.stack_trace && (
            <div className="stack-trace">
              <strong>Stack Trace:</strong>
              <pre>{log.stack_trace}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

**Visual Example:**
```
┌──────────────────────────────────────────────────┐
│ Grace: I encountered an error while accessing    │
│ the database. Here's what I saw:                 │
└──────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────┐
│ ❌ Database connection timeout after 30s     ▶  │
│    from postgres_connector                       │
└──────────────────────────────────────────────────┘

// When expanded:
┌──────────────────────────────────────────────────┐
│ ❌ Database connection timeout after 30s     ▼  │
│    from postgres_connector                       │
│                                                  │
│ 2025-11-19 02:00:00                              │
│                                                  │
│ Context:                                         │
│   database: "production_db"                      │
│   query: "SELECT * FROM users"                   │
│   timeout_seconds: 30                            │
│                                                  │
│ Stack Trace:                                     │
│   Traceback (most recent call last):             │
│     File "postgres.py", line 45, in connect      │
│       self.conn = psycopg2.connect(...)          │
│   psycopg2.OperationalError: timeout             │
└──────────────────────────────────────────────────┘
```

---

## Complete Chat Flow with Enhancements

```
User: "Update the customer email for ID 12345 to new@email.com"
    ↓
Grace processes request
    ↓
Response includes:
  1. Reply with explanation
  2. Live metrics (trust: 87%, confidence: 92%)
  3. Inline approval card (Tier 2 database write)
  4. No errors (error_logs: [])
    ↓
User sees:

┌──────────────────────────────────────────────────┐
│ Grace: I can update that customer email for you. │
│ This will modify the database record for         │
│ customer ID 12345.                               │
│                                                  │
│ 🛡️ Trust: 87% | ✓ Confidence: 92% | 📚 Learning: 3 │
└──────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────┐
│ ⚠️ Database Write                      [Tier 2] │
│                                                  │
│ User requested to update customer records        │
│                                                  │
│ ▼ Parameters                                     │
│   table: "customers"                             │
│   field: "email"                                 │
│   customer_id: 12345                             │
│   new_value: "new@email.com"                     │
│                                                  │
│  [✓ Approve]  [✗ Reject]                        │
└──────────────────────────────────────────────────┘

User clicks "✓ Approve"
    ↓
Action executes
    ↓
Toast notification: "✓ Action approved and executed"
```

---

## Frontend Integration Example

```typescript
import { useState, useEffect } from 'react';

function EnhancedChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  async function sendMessage() {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
        session_id: sessionId,
        user_id: 'user'
      })
    });
    
    const data = await response.json();
    
    setMessages(prev => [
      ...prev,
      { role: 'user', content: input },
      { 
        role: 'assistant',
        ...data  // Includes live_metrics, inline_approvals, error_logs
      }
    ]);
    
    setInput('');
  }
  
  async function handleApprove(traceId) {
    await fetch('/api/chat/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trace_id: traceId, approved: true, user_id: 'user' })
    });
    
    showToast('Action approved and executed');
  }
  
  async function handleReject(traceId) {
    await fetch('/api/chat/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trace_id: traceId, approved: false, user_id: 'user' })
    });
    
    showToast('Action rejected');
  }
  
  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            {/* Message content */}
            <div className="content">{msg.content || msg.reply}</div>
            
            {/* Live metrics (assistant messages only) */}
            {msg.role === 'assistant' && msg.live_metrics && (
              <LiveMetricsBar metrics={msg.live_metrics} />
            )}
            
            {/* Inline approval cards */}
            {msg.inline_approvals?.map(card => (
              <ApprovalCard
                key={card.trace_id}
                card={card}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            ))}
            
            {/* Error logs */}
            {msg.error_logs?.map((log, j) => (
              <ErrorLog key={j} log={log} />
            ))}
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input 
          value={input} 
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
```

---

## Benefits

### 1. Always-Visible System State
- No need to switch tabs to check metrics
- Trust and confidence visible for every response
- Learning jobs and approvals at a glance

### 2. Streamlined Approval Workflow
- Approve/reject directly in chat
- No separate approval panel needed
- Action parameters visible inline
- Risk level clearly indicated

### 3. Instant Error Context
- Stack traces embedded in conversation
- No need to dig through log files
- Context (database, query, etc.) immediately available
- Expandable details to avoid clutter

---

## Summary

✅ **Live Metrics**
- Trust score, confidence, guardian health
- Active learning jobs, pending approvals
- Incidents count
- Attached to every response

✅ **Inline Approval Cards**
- Tier 2/3 actions show approval UI
- Justification and parameters visible
- Approve/Reject buttons in chat
- Risk level color coding

✅ **Embedded Error Logs**
- Stack traces shown inline
- Full error context
- Expandable details
- Source component identification

The chat experience is now fully enhanced with contextual information! 🚀
