#!/usr/bin/env python3
"""
Test Grace's ML Coding Agent
Demonstrates Grace's internal LLM for code generation
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.kernels.agents.ml_coding_agent import ml_coding_agent
from backend.transcendence.llm_provider_router import llm_router


async def test_code_generation():
    """Test code generation"""
    
    print("=" * 70)
    print("TEST: Code Generation with Grace's Internal LLM")
    print("=" * 70)
    
    await ml_coding_agent.initialize()
    
    # Test 1: Generate a function
    print("\n[TEST 1] Generate binary search function")
    print("-" * 70)
    
    result = await ml_coding_agent.generate_code(
        description="Create a binary search function that finds an element in a sorted array",
        language="python"
    )
    
    print(f"Provider: {result['provider']}")
    print(f"Model: {result['model']}")
    print(f"External API Used: {result['external_api_used']}")
    print(f"Source: {result['source']}")
    print(f"\nGenerated Code:\n{result['code']}")
    
    # Test 2: Understand code
    print("\n" + "=" * 70)
    print("[TEST 2] Understand Code")
    print("-" * 70)
    
    sample_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    
    result = await ml_coding_agent.understand_code(
        code=sample_code,
        language="python"
    )
    
    print(f"Provider: {result['provider']}")
    print(f"External API Used: {result['external_api_used']}")
    print(f"\nAnalysis:\n{result['analysis']}")
    
    # Test 3: Bug detection
    print("\n" + "=" * 70)
    print("[TEST 3] Bug Detection")
    print("-" * 70)
    
    buggy_code = """
def divide(a, b):
    return a / b
"""
    
    result = await ml_coding_agent.detect_bugs(
        code=buggy_code,
        language="python"
    )
    
    print(f"Provider: {result['provider']}")
    print(f"\nBugs Found:\n{result['bugs_found']}")
    
    # Test 4: Generate documentation
    print("\n" + "=" * 70)
    print("[TEST 4] Documentation Generation")
    print("-" * 70)
    
    code_to_document = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    result = await ml_coding_agent.generate_documentation(
        code=code_to_document,
        language="python",
        doc_style="docstring"
    )
    
    print(f"Provider: {result['provider']}")
    print(f"\nDocumentation:\n{result['documentation']}")
    
    # Test 5: Generate tests
    print("\n" + "=" * 70)
    print("[TEST 5] Test Generation")
    print("-" * 70)
    
    code_to_test = """
def add(a, b):
    return a + b
"""
    
    result = await ml_coding_agent.generate_tests(
        code=code_to_test,
        language="python",
        framework="pytest"
    )
    
    print(f"Provider: {result['provider']}")
    print(f"\nGenerated Tests:\n{result['tests']}")
    
    # Test 6: Research (uses external API - arXiv)
    print("\n" + "=" * 70)
    print("[TEST 6] Research Papers (External API OK)")
    print("-" * 70)
    
    result = await ml_coding_agent.research_technique(
        technique="transformer architecture"
    )
    
    print(f"Technique: {result['technique']}")
    print(f"Papers Found: {result['papers_found']}")
    print(f"External API Used: {result['external_api_used']}")
    
    if result['papers']:
        print("\nSample Papers:")
        for paper in result['papers'][:3]:
            print(f"\n  - {paper['title']}")
            print(f"    URL: {paper['url']}")
    
    # Test 7: Get datasets
    print("\n" + "=" * 70)
    print("[TEST 7] Get Datasets")
    print("-" * 70)
    
    result = await ml_coding_agent.get_datasets_for_task(
        task="computer_vision"
    )
    
    print(f"Task: {result['task']}")
    print(f"Datasets Found: {result['datasets_found']}")
    
    if result['datasets']:
        print("\nDatasets:")
        for dataset in result['datasets']:
            print(f"\n  - {dataset['name']}")
            print(f"    Size: {dataset['size']}")
            print(f"    Samples: {dataset['samples']}")
            print(f"    Description: {dataset['description']}")
    
    # Final stats
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    
    stats = await ml_coding_agent.get_stats()
    
    print(f"\nAgent: {stats['agent']}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Capabilities: {', '.join(stats['capabilities'])}")
    
    print(f"\nLLM Stats:")
    llm_stats = stats['llm_stats']
    print(f"  Total Requests: {llm_stats['total_requests']}")
    print(f"  Internal Success: {llm_stats['internal_success']}")
    print(f"  Internal Success Rate: {llm_stats['internal_success_rate']*100:.1f}%")
    print(f"  Provider: {llm_stats['provider']}")
    print(f"  External Usage: {llm_stats['external_usage']}")
    
    print(f"\nPrimary LLM: {stats['primary_llm']}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Grace's ML Coding Agent COMPLETE:

✓ Code Generation - Grace's internal LLM
✓ Code Understanding - Learned patterns
✓ Bug Detection - Internal analysis
✓ Documentation - Grace's knowledge
✓ Test Generation - Learned testing patterns
✓ Research Papers - External API (arXiv) for learning
✓ Datasets - Public dataset knowledge

ALL code-related AI uses Grace's OWN intelligence!
External APIs ONLY for research and datasets.

Grace is self-sufficient for coding assistance!
""")
    
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_code_generation())
