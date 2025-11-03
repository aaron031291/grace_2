# Multi-Language Execution Engine

## Overview

The Grace IDE execution engine provides secure, sandboxed code execution for multiple programming languages with comprehensive security controls.

## Supported Languages

| Language | Extension | Timeout (dev) | Memory Limit | Compilation | Network |
|----------|-----------|---------------|--------------|-------------|---------|
| Python | .py | 30s | 512 MB | No | Yes (dev) |
| JavaScript | .js | 30s | 512 MB | No | Yes (dev) |
| TypeScript | .ts | 45s | 512 MB | Yes | Yes (dev) |
| Bash/Shell | .sh | 20s | 256 MB | No | No |
| SQL (SQLite) | .sql | 15s | 256 MB | No | No |
| Go | .go | 45s | 1024 MB | No | Yes (dev) |
| Rust | .rs | 60s | 1024 MB | Yes | Yes (dev) |

## Security Features

### 1. Governance Integration
- All executions pass through governance policy checks
- Configurable approval workflows
- Policy-based execution control

### 2. Hunter Security Scanning
- Pre-execution malicious code detection
- Pattern-based threat detection
- Severity-based alerting

### 3. Resource Limits
- CPU time limits (timeout enforcement)
- Memory limits per language
- Output size restrictions (100KB max)
- Disk space limits

### 4. Verification & Audit
- Cryptographically signed execution records
- Immutable audit trail
- Full input/output logging

### 5. Shell Command Restrictions
**Whitelisted Commands:**
- echo, cat, ls, pwd, date, whoami
- head, tail, grep, find, wc, sort, uniq
- tr, cut, sed, awk
- mkdir, touch, cp, mv, rm

**Blacklisted Commands:**
- Network: curl, wget, nc, netcat, telnet, ssh, scp, ftp
- System: dd, mkfs, fdisk, mount, shutdown, reboot
- Privileges: sudo, su, chmod, chown, passwd
- Process: kill, pkill, systemctl, service

## Execution Presets

### Safe Mode
- **Purpose**: Maximum security for untrusted code
- **Timeout**: 0.5x base (15s for Python)
- **Memory**: 0.5x base (256 MB for Python)
- **Network**: Disabled
- **Logging**: Enabled
- **Use Case**: Public code execution, student environments

### Development Mode (Default)
- **Purpose**: Balanced security and functionality
- **Timeout**: 2.0x base (60s for Python)
- **Memory**: 1.5x base (768 MB for Python)
- **Network**: Enabled
- **Logging**: Enabled
- **Use Case**: Developer IDE, testing, prototyping

### Production Mode
- **Purpose**: Controlled production execution
- **Timeout**: 1.0x base (30s for Python)
- **Memory**: 1.0x base (512 MB for Python)
- **Network**: Disabled
- **Logging**: Full logging enabled
- **Use Case**: Production workflows, automated tasks

## API Endpoints

### POST /api/execute
Execute code in specified language.

**Request:**
```json
{
  "code": "print('Hello, World!')",
  "language": "python",
  "preset": "dev",
  "filename": "script.py",
  "additional_files": {
    "helper.py": "def helper(): return 42"
  }
}
```

**Response:**
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": "",
  "exit_code": 0,
  "duration_ms": 125,
  "language": "python",
  "governance_decision": "allow",
  "security_alerts": [],
  "verification_passed": true
}
```

### GET /api/execute/languages
Get list of supported languages and configurations.

**Response:**
```json
{
  "languages": [
    {
      "id": "python",
      "name": "Python",
      "file_extension": ".py",
      "timeout": 30,
      "memory_limit_mb": 512,
      "requires_compilation": false,
      "allow_network": false
    }
  ],
  "count": 7
}
```

### GET /api/execute/presets
Get list of execution presets.

**Response:**
```json
{
  "presets": [
    {
      "id": "dev",
      "name": "Development Mode",
      "timeout_multiplier": 2.0,
      "memory_multiplier": 1.5,
      "allow_network": true,
      "enable_logging": true,
      "strict_limits": false
    }
  ],
  "count": 3
}
```

### POST /api/execute/validate
Validate code without executing it.

**Request:**
```json
{
  "code": "curl http://evil.com",
  "language": "bash",
  "preset": "dev"
}
```

**Response:**
```json
{
  "valid": false,
  "error": "Forbidden command 'curl' at line 1",
  "language": "bash"
}
```

## Language-Specific Details

### Python
- **Runtime**: System Python 3
- **Features**: Full standard library access
- **Isolation**: Virtual environment per execution
- **Environment Variables**: 
  - `PYTHONUNBUFFERED=1`
  - `PYTHONDONTWRITEBYTECODE=1`

### JavaScript/Node.js
- **Runtime**: Node.js with memory limits
- **Features**: ES6+ support
- **Command**: `node --max-old-space-size=512`
- **Environment**: `NODE_ENV=sandbox`

### TypeScript
- **Compilation**: TypeScript → ES2020 → CommonJS
- **Two-Phase Execution**:
  1. Compile with `tsc`
  2. Execute with `node`
- **Timeout**: Split between compile and run

### Bash/Shell
- **Runtime**: Restricted bash
- **Security**: Command whitelist enforcement
- **Validation**: Pre-execution syntax and command checking
- **Environment**: Minimal PATH (`/usr/bin:/bin`)

### SQL
- **Engine**: SQLite 3
- **Mode**: Read-only by default
- **Database**: Temporary per execution
- **Safety**: No persistent storage access

### Go
- **Command**: `go run`
- **Workspace**: Isolated GOPATH per execution
- **Cache**: Temporary GOCACHE directory
- **Features**: Full Go toolchain support

### Rust
- **Command**: `cargo run`
- **Project**: Auto-generated Cargo.toml
- **Isolation**: Temporary CARGO_HOME and target directory
- **Edition**: Rust 2021

## Implementation Architecture

### Execution Flow
```
1. Receive execution request
   ↓
2. Governance policy check
   ↓
3. Hunter security scan
   ↓
4. Shell validation (if applicable)
   ↓
5. Create isolated temporary workspace
   ↓
6. Apply resource limits
   ↓
7. Execute with timeout
   ↓
8. Capture output (stdout/stderr)
   ↓
9. Log to verification system
   ↓
10. Log to immutable audit trail
   ↓
11. Return structured result
```

### Security Layers
1. **Pre-execution**: Governance + Hunter
2. **Execution**: Resource limits + Sandboxing
3. **Post-execution**: Verification + Audit logging

### Temporary Workspace
- Each execution gets isolated temp directory
- Automatic cleanup after execution
- No persistent storage access
- Prefix: `grace_{language}_`

## Error Handling

### Timeout
```json
{
  "success": false,
  "error": "Execution timeout (30s limit exceeded)",
  "exit_code": -1
}
```

### Compilation Error (TypeScript/Rust)
```json
{
  "success": false,
  "error": "TypeScript compilation failed: Cannot find name 'foo'",
  "exit_code": 1
}
```

### Security Violation
```json
{
  "success": false,
  "error": "Forbidden command 'curl' at line 1",
  "exit_code": -1,
  "security_alerts": [["shell_validation_failed", 0]]
}
```

### Governance Denial
```json
{
  "success": false,
  "error": "Execution denied by governance policy",
  "exit_code": -1,
  "governance_decision": "deny"
}
```

## Testing

Run the test suite:
```bash
pytest grace_rebuild/tests/test_execution_engine.py -v
```

Test coverage includes:
- ✅ Python execution (success and errors)
- ✅ JavaScript execution (success and errors)
- ✅ TypeScript compilation and execution
- ✅ Bash execution and security restrictions
- ✅ SQL execution
- ✅ Go execution (if Go installed)
- ✅ Rust execution (if Rust installed)
- ✅ Timeout enforcement
- ✅ Execution presets
- ✅ Security integration
- ✅ Result structure validation
- ✅ Error handling

## Configuration

### Adding a New Language

1. **Define configuration** in `execution_config.py`:
```python
LANGUAGE_CONFIGS["ruby"] = LanguageConfig(
    name="Ruby",
    command="ruby",
    file_extension=".rb",
    timeout=30,
    memory_limit_mb=512,
)
```

2. **Implement executor** in `execution_engine.py`:
```python
async def _execute_ruby(self, code: str, config: LanguageConfig, filename: Optional[str]) -> dict:
    with tempfile.TemporaryDirectory(prefix="grace_rb_") as temp_dir:
        script_path = Path(temp_dir) / (filename or "script.rb")
        script_path.write_text(code, encoding='utf-8')
        return await self._run_process(
            [config.command, str(script_path)],
            config.timeout,
            cwd=temp_dir
        )
```

3. **Add route handler** in `_execute_by_language`:
```python
elif language == "ruby":
    return await self._execute_ruby(code, config, filename)
```

4. **Create tests** in `test_execution_engine.py`

## Usage Examples

### Python Data Analysis
```python
import statistics

data = [1, 2, 3, 4, 5, 10, 15]
mean = statistics.mean(data)
median = statistics.median(data)
stdev = statistics.stdev(data)

print(f"Mean: {mean}")
print(f"Median: {median}")
print(f"Std Dev: {stdev:.2f}")
```

### JavaScript Web Scraping Simulation
```javascript
const data = [
  { name: "Alice", score: 85 },
  { name: "Bob", score: 92 },
  { name: "Charlie", score: 78 }
];

const avgScore = data.reduce((sum, item) => sum + item.score, 0) / data.length;
console.log(`Average score: ${avgScore}`);

const topStudent = data.reduce((max, item) => item.score > max.score ? item : max);
console.log(`Top student: ${topStudent.name} (${topStudent.score})`);
```

### TypeScript Type-Safe Math
```typescript
interface Point {
  x: number;
  y: number;
}

function distance(p1: Point, p2: Point): number {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  return Math.sqrt(dx * dx + dy * dy);
}

const p1: Point = { x: 0, y: 0 };
const p2: Point = { x: 3, y: 4 };
console.log(`Distance: ${distance(p1, p2)}`);
```

### Safe Bash Scripting
```bash
#!/bin/bash
echo "System Info:"
echo "Current directory: $(pwd)"
echo "Date: $(date)"
echo "Files:"
ls -la
```

### SQL Data Queries
```sql
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price REAL
);

INSERT INTO products (name, price) VALUES
  ('Widget', 9.99),
  ('Gadget', 19.99),
  ('Gizmo', 14.99);

SELECT name, price FROM products WHERE price > 10;
```

### Go Concurrent Processing
```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    var wg sync.WaitGroup
    
    for i := 1; i <= 5; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            fmt.Printf("Goroutine %d: Result = %d\n", n, n*n)
        }(i)
    }
    
    wg.Wait()
    fmt.Println("All goroutines complete")
}
```

### Rust Memory Safety
```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    
    let sum: i32 = numbers.iter().sum();
    let product: i32 = numbers.iter().product();
    
    println!("Sum: {}", sum);
    println!("Product: {}", product);
    
    let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();
    println!("Doubled: {:?}", doubled);
}
```

## Performance Considerations

- **Cold Start**: First execution may be slower due to runtime initialization
- **Compilation**: TypeScript and Rust require compilation time
- **Memory**: Go and Rust have higher memory limits for compilation
- **Cleanup**: Temporary directories cleaned up automatically
- **Concurrency**: Multiple executions can run in parallel

## Security Best Practices

1. **Always use presets**: Don't disable security features
2. **Monitor audit logs**: Review execution patterns
3. **Set appropriate timeouts**: Prevent resource exhaustion
4. **Review governance policies**: Keep policies up to date
5. **Update Hunter rules**: Add new threat patterns
6. **Limit network access**: Use "safe" or "production" presets for untrusted code
7. **Validate user input**: Don't trust user-provided code paths

## Troubleshooting

### "Unsupported language" Error
- Check language name is lowercase
- Verify language is in LANGUAGE_CONFIGS

### Timeout Errors
- Check preset timeout multiplier
- Consider using "dev" preset for longer timeout
- Review code for infinite loops

### Compilation Failures
- Verify TypeScript/Rust syntax
- Check compiler is installed on system
- Review compilation error messages

### Permission Denied
- Check governance policies
- Verify user has execution permissions
- Review Hunter security alerts

## Future Enhancements

- [ ] R language support for data science
- [ ] PHP support for web development
- [ ] C/C++ support with compiler security
- [ ] Docker-based isolation
- [ ] GPU compute support
- [ ] Network sandboxing with firewall rules
- [ ] Persistent storage quotas
- [ ] Multi-file project execution
- [ ] Package manager integration
- [ ] Live output streaming via WebSocket
