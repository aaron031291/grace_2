# Grace User Onboarding

## 👋 Welcome to Grace!

Grace is an autonomous AI system that learns from trusted sources, governs itself, and maintains complete transparency.

## 🚀 Getting Started (5 Minutes)

### Step 1: First Login
1. Visit http://localhost:5173
2. Login: `admin` / `admin123`
3. **⚠️ Change password immediately!**

### Step 2: Explore the Interface
Click each button to see:
- 💬 **Chat** - Talk with Grace
- 💻 **IDE** - Write and run code
- 📊 **Dashboard** - System metrics
- 📁 **Memory** - Knowledge base
- 🛡️ **Hunter** - Security alerts

### Step 3: Have Your First Conversation
```
You: Hello Grace
Grace: Hello! I'm Grace. How can I help you today?

You: Show me my history
Grace: We just started chatting...

You: How are you?
Grace: I'm functioning optimally. All systems operational.
```

### Step 4: Try the IDE
1. Click 💻 IDE
2. Write: `print("Hello from Grace!")`
3. Click ▶ Run
4. See output in console

### Step 5: Teach Grace Something
```bash
# In terminal:
curl -X POST http://localhost:8000/api/ingest/text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Knowledge",
    "content": "Grace is an autonomous AI system.",
    "domain": "about_grace"
  }'
```

## 📚 Key Concepts

### 1. Grace is Honest
- She admits when she doesn't know
- Never hallucinates
- Proposes research instead

### 2. Trust-Scored Knowledge
- All sources rated 0-100
- High trust (70+) → Auto-approved
- Medium (40-69) → Needs review
- Low (<40) → Blocked

### 3. Complete Auditability
- Every action logged immutably
- Hash-chained for tamper detection
- View audit trail anytime

### 4. Self-Governing
- Policies enforce rules
- Approvals for risky actions
- Security scanning on all inputs

### 5. Self-Healing
- Monitors own health
- Auto-restarts failed components
- Falls back to safe modes

## 🎯 Common Tasks

### Teaching Grace
```bash
# Add knowledge from URL
POST /api/ingest/url
{"url": "https://python.org/docs"}

# Upload file
POST /api/ingest/file
[file upload]

# Add text directly
POST /api/ingest/text
{"title": "...", "content": "..."}
```

### Setting Trust Levels
```bash
# Add trusted source
POST /api/trust/sources
{
  "domain": "mycompany.com",
  "trust_score": 90,
  "category": "internal"
}
```

### Reviewing Approvals
```bash
# List pending
GET /api/governance/approvals

# Approve
POST /api/governance/approvals/{id}/decision
{"decision": "approve", "reason": "Verified safe"}
```

### Handling Security Alerts
```bash
# View alerts
GET /api/hunter/alerts

# Resolve
POST /api/hunter/alerts/{id}/resolve
{"status": "resolved", "note": "False positive"}
```

## 🔐 Security Best Practices

1. **Change Default Password**
   ```bash
   POST /api/auth/register
   {"username": "yourusername", "password": "strong_password"}
   ```

2. **Set Strong GRACE_JWT_SECRET**
   ```bash
   # In .env file
   GRACE_JWT_SECRET=generate-a-long-random-string-here
   ```

3. **Review Policies Regularly**
   - Check `/api/governance/policies`
   - Add policies for your use case
   - Test approval workflows

4. **Monitor Hunter Alerts**
   - Review daily
   - Adjust rules as needed
   - Train on false positives

5. **Backup Database**
   ```bash
   # Daily backup
   cp grace.db grace_backup_$(date +%Y%m%d).db
   ```

## 📖 Learning Path

**Week 1: Basics**
- Use chat interface
- Explore dashboard
- Try IDE with simple code
- Review documentation

**Week 2: Knowledge**
- Ingest first documents
- Set up trusted sources
- Test trust scoring
- Review knowledge browser

**Week 3: Governance**
- Create custom policies
- Test approval workflows
- Review audit logs
- Configure Hunter rules

**Week 4: Advanced**
- Train models from knowledge
- Set up meta-loop optimization
- Configure self-healing
- Customize for your domain

## 💡 Pro Tips

1. **Check Reflections Daily** - Grace's observations are valuable insights
2. **Use Auto-Tasks** - Let Grace create tasks from patterns
3. **Trust the System** - Audit trail proves everything
4. **Start Conservative** - Add trust sources gradually
5. **Review Meta-Recommendations** - Grace learns to optimize herself

## 🆘 Getting Help

- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health/status
- **Logs:** Check backend terminal
- **Issues:** Review KNOWN_ISSUES.md

Welcome to the future of autonomous AI! 🚀🤖
