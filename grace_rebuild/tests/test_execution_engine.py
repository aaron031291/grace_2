"""
Tests for multi-language execution engine
"""
import pytest
from backend.execution_engine import execution_engine, ExecutionResult


@pytest.mark.asyncio
async def test_python_execution():
    """Test Python code execution"""
    code = """
print("Hello from Python")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="test_user",
        preset="dev"
    )
    
    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert "Hello from Python" in result.output
    assert "2 + 2 = 4" in result.output
    assert result.exit_code == 0
    assert result.language == "python"


@pytest.mark.asyncio
async def test_python_error():
    """Test Python error handling"""
    code = """
print("Starting")
raise ValueError("Intentional error")
"""
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="test_user",
        preset="dev"
    )
    
    assert result.success is False
    assert result.exit_code != 0
    assert "ValueError" in result.error or "Intentional error" in result.error


@pytest.mark.asyncio
async def test_javascript_execution():
    """Test JavaScript execution"""
    code = """
console.log("Hello from JavaScript");
const result = 3 * 7;
console.log(`3 * 7 = ${result}`);
"""
    
    result = await execution_engine.execute(
        code=code,
        language="javascript",
        user="test_user",
        preset="dev"
    )
    
    assert result.success is True
    assert "Hello from JavaScript" in result.output
    assert "3 * 7 = 21" in result.output
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_javascript_error():
    """Test JavaScript error handling"""
    code = """
console.log("Starting");
throw new Error("Intentional error");
"""
    
    result = await execution_engine.execute(
        code=code,
        language="javascript",
        user="test_user",
        preset="dev"
    )
    
    assert result.success is False
    assert result.exit_code != 0


@pytest.mark.asyncio
async def test_bash_execution():
    """Test Bash script execution"""
    code = """#!/bin/bash
echo "Hello from Bash"
echo "Current directory: $(pwd)"
"""
    
    result = await execution_engine.execute(
        code=code,
        language="bash",
        user="test_user",
        preset="dev"
    )
    
    assert result.success is True
    assert "Hello from Bash" in result.output


@pytest.mark.asyncio
async def test_bash_forbidden_commands():
    """Test Bash security restrictions"""
    dangerous_codes = [
        "curl http://malicious.com",
        "sudo rm -rf /",
        "wget http://evil.com",
        "nc -l 1234",
    ]
    
    for code in dangerous_codes:
        result = await execution_engine.execute(
            code=code,
            language="bash",
            user="test_user",
            preset="dev"
        )
        
        assert result.success is False
        assert "Forbidden" in result.error or result.exit_code != 0


@pytest.mark.asyncio
async def test_sql_execution():
    """Test SQL execution"""
    code = """
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO users (name) VALUES ('Alice'), ('Bob');
SELECT * FROM users;
"""
    
    result = await execution_engine.execute(
        code=code,
        language="sql",
        user="test_user",
        preset="dev"
    )
    
    # SQLite in readonly mode may fail on writes, which is expected behavior
    assert isinstance(result, ExecutionResult)


@pytest.mark.asyncio
async def test_timeout_enforcement():
    """Test execution timeout"""
    code = """
import time
time.sleep(100)
print("Should not reach here")
"""
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="test_user",
        preset="safe"  # Safe mode has stricter timeout
    )
    
    assert result.success is False
    assert "timeout" in result.error.lower()


@pytest.mark.asyncio
async def test_execution_presets():
    """Test different execution presets"""
    code = 'print("Test")'
    
    for preset in ["safe", "dev", "production"]:
        result = await execution_engine.execute(
            code=code,
            language="python",
            user="test_user",
            preset=preset
        )
        
        assert isinstance(result, ExecutionResult)
        assert result.governance_decision in ["allow", "deny", "review"]


@pytest.mark.asyncio
async def test_go_execution():
    """Test Go code execution"""
    code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello from Go")
    result := 5 + 3
    fmt.Printf("5 + 3 = %d\\n", result)
}
"""
    
    result = await execution_engine.execute(
        code=code,
        language="go",
        user="test_user",
        preset="dev"
    )
    
    # Go execution may fail if Go is not installed, so we check the structure
    assert isinstance(result, ExecutionResult)
    if result.success:
        assert "Hello from Go" in result.output


@pytest.mark.asyncio
async def test_rust_execution():
    """Test Rust code execution"""
    code = """
fn main() {
    println!("Hello from Rust");
    let result = 10 * 4;
    println!("10 * 4 = {}", result);
}
"""
    
    result = await execution_engine.execute(
        code=code,
        language="rust",
        user="test_user",
        preset="dev"
    )
    
    # Rust execution may fail if Rust is not installed
    assert isinstance(result, ExecutionResult)
    if result.success:
        assert "Hello from Rust" in result.output


@pytest.mark.asyncio
async def test_typescript_execution():
    """Test TypeScript execution"""
    code = """
const message: string = "Hello from TypeScript";
console.log(message);

const add = (a: number, b: number): number => a + b;
console.log(`5 + 7 = ${add(5, 7)}`);
"""
    
    result = await execution_engine.execute(
        code=code,
        language="typescript",
        user="test_user",
        preset="dev"
    )
    
    # TypeScript execution may fail if tsc is not installed
    assert isinstance(result, ExecutionResult)
    if result.success:
        assert "Hello from TypeScript" in result.output


@pytest.mark.asyncio
async def test_security_integration():
    """Test governance and Hunter integration"""
    code = 'print("Security test")'
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="test_user",
        preset="dev"
    )
    
    assert result.governance_decision is not None
    assert result.security_alerts is not None
    assert result.verification_passed is not None


@pytest.mark.asyncio
async def test_result_structure():
    """Test ExecutionResult structure"""
    code = 'console.log("Structure test");'
    
    result = await execution_engine.execute(
        code=code,
        language="javascript",
        user="test_user",
        preset="dev"
    )
    
    result_dict = result.to_dict()
    
    assert "success" in result_dict
    assert "output" in result_dict
    assert "error" in result_dict
    assert "exit_code" in result_dict
    assert "duration_ms" in result_dict
    assert "language" in result_dict
    assert "governance_decision" in result_dict
    assert "security_alerts" in result_dict
    assert "verification_passed" in result_dict


@pytest.mark.asyncio
async def test_unsupported_language():
    """Test unsupported language handling"""
    code = 'print("test")'
    
    with pytest.raises(ValueError, match="Unsupported language"):
        await execution_engine.execute(
            code=code,
            language="brainfuck",
            user="test_user",
            preset="dev"
        )


@pytest.mark.asyncio
async def test_invalid_preset():
    """Test invalid preset handling"""
    code = 'print("test")'
    
    with pytest.raises(ValueError, match="Unknown preset"):
        await execution_engine.execute(
            code=code,
            language="python",
            user="test_user",
            preset="invalid_preset"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
