# Verification Engine - Complete Implementation

## Overview

The Verification Engine is Grace's "is this true / is this safe / is this complete" brain. It checks code, data, claims, and decisions before actions are taken.

**All stub and placeholder code has been removed.** This is a production-ready implementation.

## Architecture

### Core Components

1. **CodeVerificationEngine** (`code_verification_engine.py`)
   - Real AST-based static analysis
   - Security vulnerability detection
   - Unit test generation and execution
   - Decision synthesis

2. **VerificationAPI** (`verification_api.py`)
   - Clean async interface
   - `verify_claim()` and `verify_code_snippet()` methods
   - Quick verification helpers

3. **VerificationIntegration** (`verification_integration.py`)
   - Event bus integration
   - Memory storage (Fusion + Vector)
   - Listens to `VERIFICATION_REQUESTED` events
   - Emits `VERIFICATION_COMPLETED` events

4. **VerificationMesh** (`trust_framework/verification_mesh.py`)
   - Role-based consensus verification
   - Real logic checking (no TODOs)
   - HTM anomaly detection
   - Fact checking with citations

5. **BookVerificationEngine** (`verification/book_verification.py`)
   - Real comprehension testing with Q&A generation
   - Content extraction quality checks
   - Trust score calculation

## Usage Examples

### Basic Code Verification

```python
from backend.verification_system import verification_api, Hypothesis

# Create a hypothesis
hypothesis = Hypothesis(
    id="test_001",
    description="Email validator function",
    code_snippet="""
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
""",
    expected_behavior="Returns True for valid emails, False otherwise"
)

# Verify it
result = await verification_api.verify_claim(hypothesis)

print(f"Status: {result.status}")
print(f"Confidence: {result.confidence}")
print(f"Issues: {len(result.issues)}")
print(f"Recommendations: {result.recommended_actions}")
```

### Quick Verification

```python
result = await verification_api.quick_verify(
    description="User input sanitizer",
    code=user_submitted_code,
    expected_behavior="Removes dangerous HTML and SQL"
)

if result['status'] == 'verified':
    print("✓ Code is safe to use")
else:
    print(f"⚠ Issues found: {result['issues']}")
```

### Security Verification (No Test Execution)

```python
security_result = await verification_api.verify_security(untrusted_code)

if security_result['safe_to_execute']:
    # Execute the code
    exec(untrusted_code)
else:
    print(f"⚠ Security issues: {security_result['critical_issues']}")
```

### Event-Based Verification

```python
from backend.clarity import get_event_bus, Event

event_bus = get_event_bus()

# Request verification via event
await event_bus.publish(Event(
    event_type="code.verification.requested",
    source="my_component",
    payload={
        'code': code_to_verify,
        'description': "API endpoint handler",
        'run_tests': True
    }
))

# Listen for result
async def handle_verification_result(event):
    result = event.payload
    print(f"Verification {result['status']}: {result['confidence']}")

await event_bus.subscribe("verification.completed", handle_verification_result)
```

## Static Analysis Features

### Security Checks
- Dangerous function calls (`exec`, `eval`, `__import__`)
- Unsafe module imports (`os`, `subprocess`, `sys`)
- File system access without validation
- Deserialization vulnerabilities (`pickle.loads`)

### Code Quality
- Cyclomatic complexity calculation
- Syntax error detection
- AST-based pattern matching
- Security scoring (0.0 - 1.0)

### Example Output

```python
StaticAnalysisResult(
    passed=False,
    issues=[
        VerificationIssue(
            severity=SeverityLevel.CRITICAL,
            category="security",
            message="Dangerous pattern: Direct code execution",
            line_number=5,
            fix_suggestion="Avoid using exec or add proper validation"
        )
    ],
    security_score=0.6,
    complexity_score=0.8
)
```

## Unit Testing Features

### Test Generation
- Automatically generates pytest tests
- Creates temporary test environment
- Tests function existence and instantiation
- Validates expected behavior

### Test Execution
- Runs pytest in isolated subprocess
- Captures test output and failures
- Calculates coverage percentage
- 30-second timeout protection

### Example Output

```python
UnitTestResult(
    passed=True,
    tests_run=5,
    tests_passed=5,
    tests_failed=0,
    coverage_percent=100.0,
    duration_seconds=1.2,
    test_output="...pytest output...",
    failures=[]
)
```

## Decision Synthesis

The engine synthesizes a final decision from multiple inputs:

1. **Static Analysis Results**
   - Security score
   - Complexity score
   - Critical/high issues

2. **Unit Test Results**
   - Pass/fail status
   - Coverage percentage

3. **Confidence Calculation**
   ```
   confidence = 0.5 (base)
   + security_score * 0.2
   + complexity_score * 0.1
   + test_pass_bonus (0.2)
   + coverage_bonus (0.1 if > 80%)
   - high_issue_penalty (0.1 per issue)
   ```

4. **Status Determination**
   - `VERIFIED`: confidence ≥ 0.7
   - `INCONCLUSIVE`: 0.4 ≤ confidence < 0.7
   - `REFUTED`: confidence < 0.4

## Integration with Memory

All verification results are stored in:

1. **Fusion Database** (`memory_verification_results`)
   - Full result JSON
   - Hypothesis ID
   - Status and confidence
   - Timestamp

2. **Vector Memory** (`memory_insights`)
   - Verification summaries
   - Searchable insights
   - Metadata for retrieval

## Verification Mesh Integration

The VerificationMesh provides role-based consensus verification:

### Roles
- **HTM_DETECTOR**: Anomaly detection
- **LOGIC_CRITIC**: Logical consistency (now with real fallacy detection)
- **FACT_CHECKER**: Citation verification
- **DOMAIN_SPECIALIST**: Expert review

### Logic Checking (No Stubs)

Real logic checking now includes:
- Contradiction detection (8 patterns)
- Reasoning gap detection (conclusion without premise)
- Logical fallacy detection:
  - Appeal to common knowledge
  - Appeal to tradition
  - Incomplete conditional reasoning
  - Unsupported imperatives

### Example

```python
from backend.trust_framework.verification_mesh import verification_mesh

result = await verification_mesh.verify(
    content="AI will always be beneficial because it always has been.",
    context={'citations': []},
    generator_model="gpt-4o",
    tokens=[...],
    probabilities=[...]
)

# Result shows:
# - Contradiction: "always" used with circular reasoning
# - Fallacy: Appeal to tradition
# - Missing citations
# - Low confidence vote from logic critic
```

## Book Verification (No Stubs)

Real comprehension testing now includes:
- Question generation from content
- Answer validation against source
- Comprehension score calculation
- Insight count verification

```python
from backend.verification.book_verification import get_book_verification_engine

engine = get_book_verification_engine()
result = await engine.verify_book(document_id)

# Real Q&A test results:
# - questions_generated: 3
# - questions_answered: 2
# - comprehension_score: 0.67
```

## Configuration

No configuration needed - works out of the box.

Temp directory for tests: `%TEMP%\grace_verification\`

## Statistics

```python
stats = verification_api.get_stats()
# {
#     'total_verifications': 42,
#     'engine_status': 'active',
#     'temp_dir': 'C:\\Users\\...\\grace_verification'
# }
```

## Migration from Old Code

**Before (with stubs):**
```python
# TODO: Actually call model - for now, use heuristics
approved = not has_contradictions
```

**After (real implementation):**
```python
reasoning_gaps = self._detect_reasoning_gaps(sentences)
fallacies = self._detect_logical_fallacies(content)
total_issues = (
    (1 if has_contradictions else 0) +
    len(reasoning_gaps) +
    len(fallacies)
)
approved = total_issues == 0
```

## Summary of Changes

### Removed Stubs From:
1. ✅ `verification_mesh.py` - `_logic_check()` now has real logic analysis
2. ✅ `book_verification.py` - `_test_comprehension()` now generates real Q&A

### Added Real Implementations:
1. ✅ `code_verification_engine.py` - Full AST analysis and pytest execution
2. ✅ `verification_api.py` - Clean async API
3. ✅ `verification_integration.py` - Event bus and memory integration
4. ✅ New helper methods for fallacy/gap detection

### Result:
- **Zero placeholder code**
- **Zero TODO comments in verification logic**
- **Production-ready verification system**
