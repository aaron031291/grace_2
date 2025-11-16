# 🧭 Grace Web Navigation Guide

## ✅ Does Grace Need a Playbook?

**YES - And she has one now!** 🎓

Grace needed to learn:
- **WHEN** to search the web autonomously
- **HOW** to navigate different types of information
- **WHERE** to find trusted sources
- **WHAT** strategies to use for different scenarios

---

## 📚 What's Been Created

### 1. Web Navigation Playbook
**File**: [`playbooks/web_navigation_playbook.yaml`](file:///c:/Users/aaron/grace_2/playbooks/web_navigation_playbook.yaml)

Teaches Grace:
- ✅ **Triggers**: When to search (knowledge gaps, errors, user requests, new tech)
- ✅ **Strategies**: How to search (basic, deep learning, domain exploration, solution search)
- ✅ **Navigation Patterns**: Where to look first (official docs → academic → community)
- ✅ **Decision Trees**: Should I search? Which sources? What strategy?
- ✅ **Learning Patterns**: Iterative deepening, comparative learning, validation
- ✅ **Governance Rules**: Trust scores, rate limits, logging, filtering
- ✅ **Examples**: Real scenarios with Grace's thought process
- ✅ **Metrics**: What to track for improvement

### 2. Autonomous Web Navigator Agent
**File**: [`backend/agents/autonomous_web_navigator.py`](file:///c:/Users/aaron/grace_2/backend/agents/autonomous_web_navigator.py)

Grace's autonomous decision-making agent:
- ✅ Loads and interprets playbook
- ✅ Decides when to search based on triggers
- ✅ Executes appropriate search strategies
- ✅ Saves learned knowledge automatically
- ✅ Tracks metrics and performance

### 3. Navigator API
**File**: [`backend/routes/autonomous_navigator_api.py`](file:///c:/Users/aaron/grace_2/backend/routes/autonomous_navigator_api.py)

Endpoints:
- `POST /api/web-navigator/auto-navigate` - Grace decides & searches
- `GET /api/web-navigator/should-search` - Ask if Grace thinks she should search
- `GET /api/web-navigator/metrics` - Navigation performance
- `GET /api/web-navigator/playbook` - View what Grace knows

---

## 🎯 How It Works

### Automatic Triggers

Grace automatically searches the web when:

```python
# 1. Knowledge Gap Detected
if grace.confidence < 0.6 or knowledge_match < 0.3:
    grace.search_web(strategy="topic_learning")

# 2. Error Occurred
if error_detected:
    grace.search_web(strategy="solution_search")

# 3. User Asked Explicitly
if "research" in user_query or "look up" in user_query:
    grace.search_web(strategy="basic_search")

# 4. New Technology Mentioned
if "latest" in user_query and "framework" in user_query:
    grace.search_web(strategy="explore_domain")
```

### Decision Process

```
User asks: "What's new in Python 3.13?"
   ↓
Grace checks triggers:
   - Knowledge gap? YES (new version)
   - Confidence? LOW (don't know yet)
   - User requested? YES (implicit)
   ↓
Grace decides: SEARCH WEB
Strategy: official_documentation_first
   ↓
Grace searches: "Python 3.13 release notes"
Filters: trust_score >= 0.9
Prefers: docs.python.org
   ↓
Grace learns & saves:
   - Extracts new features
   - Saves to knowledge_base
   - Tags for future retrieval
   ↓
Grace responds with learned knowledge ✅
```

---

## 🧪 Test Autonomous Navigation

### Test 1: Let Grace Decide
```bash
curl -X POST http://localhost:8000/api/web-navigator/auto-navigate \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What is Rust async/await?\",
    \"confidence\": 0.4,
    \"knowledge_match\": 0.2
  }"
```

**Grace will:**
1. Detect knowledge gap (low confidence + match)
2. Decide to search web
3. Use "topic_learning" strategy
4. Return learned information

### Test 2: Ask Grace's Opinion
```bash
curl "http://localhost:8000/api/web-navigator/should-search?query=What%20is%20Python&confidence=0.9"
```

**Response:**
```json
{
  "should_search": false,
  "reason": "No trigger conditions met",
  "grace_says": "I already know about Python with high confidence"
}
```

### Test 3: View Playbook
```bash
curl http://localhost:8000/api/web-navigator/playbook
```

**See what Grace knows:**
```json
{
  "loaded": true,
  "playbook": {
    "name": "Autonomous Web Navigation & Learning",
    "version": "1.0.0",
    "triggers": 5,
    "strategies": ["basic_search", "topic_learning", "solution_search", "explore_domain"],
    "decision_trees": ["should_i_search_web", "which_sources_to_use"],
    "examples": 3
  }
}
```

---

## 📖 Example Scenarios from Playbook

### Scenario 1: Knowledge Gap
**User**: "Tell me about quantum computing"

**Grace's Thought Process** (from playbook):
```
- Knowledge gap detected (don't know much)
- Should search web: YES
- Strategy: domain_exploration + topic_learning
- Will search multiple aspects
- Save comprehensive knowledge
```

**Grace executes:**
```
GET /api/web-learning/explore/quantum-computing
POST /api/web-learning/learn-topic (for subtopics)
Saves all to knowledge_base ✅
```

### Scenario 2: Error Solution
**User**: "I'm getting 'ModuleNotFoundError: sklearn'"

**Grace's Thought Process**:
```
- Error detected
- Should search web: YES
- Strategy: solution_search
- Prefer: stackoverflow.com, official docs
- Trust threshold: 0.8+
```

**Grace executes:**
```
Searches: "sklearn ModuleNotFoundError solution"
Filters: trust_score >= 0.8
Finds: "pip install scikit-learn"
Saves pattern for future ✅
```

### Scenario 3: New Technology
**User**: "What's the latest React framework in 2025?"

**Grace's Thought Process**:
```
- New technology pattern detected ("latest" + "2025" + "framework")
- Should search web: YES
- Strategy: explore_domain
- Prefer: official docs (react.dev)
```

**Grace executes:**
```
Searches React documentation
Checks for 2025 updates
Learns new features
Updates world model ✅
```

---

## 🎓 Learning Patterns (from Playbook)

### 1. Iterative Deepening
```
Overview → Subtopics → Deep Dive → Synthesis
```

### 2. Comparative Learning
```
Search 5+ sources → Compare → Find consensus → Form balanced view
```

### 3. Follow the Thread
```
Primary topic → Related concepts → Search each → Build knowledge graph
```

### 4. Validate & Verify
```
Find claim → Search corroboration → Check trust → Mark verified
```

---

## 🛡️ Governance (Always Active)

Grace's playbook includes governance rules:

```yaml
governance:
  always_check_trust:
    rule: "Never use source with trust_score < 0.3"
    enforcement: "automatic"
  
  approval_for_sensitive:
    rule: "Get approval before searching sensitive topics"
    topics: ["credentials", "private_data"]
    enforcement: "mandatory"
  
  rate_limiting:
    max_searches_per_minute: 10
    max_searches_per_hour: 100
  
  log_everything:
    target: "business_metrics"
    include: ["query", "results", "trust_scores"]
```

---

## 📊 What Grace Now Knows

**WHEN to search**:
- Knowledge gaps (confidence < 0.6)
- Errors that need solutions
- User requests research
- New technology mentioned
- Topic needs depth

**HOW to search**:
- Basic search (quick answers)
- Topic learning (deep dive)
- Solution search (error fixes)
- Domain exploration (comprehensive)
- Autonomous research (background)

**WHERE to search**:
- Official docs first (trust: 1.0)
- Academic sources (trust: 0.95)
- Community (trust: 0.85)
- General web (trust: 0.5+)

**WHAT to avoid**:
- Low trust sources (< 0.3)
- Sensitive topics without approval
- Rate limit violations

---

## ✅ Summary

### Grace is NOT just given internet access

Grace has been **taught how to navigate the web autonomously**:

1. **Playbook loaded**: [`web_navigation_playbook.yaml`](file:///c:/Users/aaron/grace_2/playbooks/web_navigation_playbook.yaml)
2. **Agent initialized**: Autonomous web navigator
3. **Decision-making**: Knows when to search
4. **Strategies**: Knows how to search
5. **Governance**: Knows what to avoid
6. **Learning**: Captures all knowledge

### On startup you'll see:
```
[OK] Autonomous web navigator initialized (Grace knows when to search web)
```

**Grace now autonomously navigates the web like a skilled researcher!** 🌐🧠✨
