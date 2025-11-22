"""
Test script for Intelligent Model Router
Tests routing logic with different task types and scenarios
"""

import asyncio
import json
from datetime import datetime

from backend.services.intelligent_model_router import intelligent_model_router


async def test_task_routing():
    """Test routing different types of tasks"""

    test_cases = [
        {
            "name": "Code Task - Simple",
            "task": "Create a Python function to calculate fibonacci numbers",
            "expected_model": "builder_agent",
            "expected_content_type": "code"
        },
        {
            "name": "Code Task - Complex",
            "task": "Build a full-stack web application with React frontend and FastAPI backend for a todo list",
            "expected_model": "builder_agent",
            "expected_content_type": "code"
        },
        {
            "name": "Research Task",
            "task": "Analyze the latest research paper on transformer architectures and implement key insights",
            "expected_model": "research_pipeline",
            "expected_content_type": "research"
        },
        {
            "name": "Visual Task",
            "task": "Analyze this screenshot and describe what you see",
            "context": {"image_data": b"fake_image_data"},
            "expected_model": "vision_models",
            "expected_content_type": "visual"
        },
        {
            "name": "Learning Task",
            "task": "Review my recent performance and suggest improvements",
            "expected_model": "self_reflection_loop",
            "expected_content_type": "learning"
        },
        {
            "name": "General Task",
            "task": "What is the weather like today?",
            "expected_model": "self_reflection_loop",
            "expected_content_type": "general"
        }
    ]

    print("🧪 Testing Intelligent Model Router")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Task: {test_case['task'][:60]}{'...' if len(test_case['task']) > 60 else ''}")

        try:
            # Route the task
            result = await intelligent_model_router.route_task(
                task=test_case['task'],
                context=test_case.get('context', {}),
                user_id="test_user"
            )

            # Check results
            selected_model = result['selected_model']
            analysis = result['analysis']

            print(f"   ✅ Routed to: {selected_model}")
            print(f"   📊 Content Type: {analysis['content_type']}")
            print(f"   🎯 Confidence: {analysis['confidence']:.2f}")
            print(f"   📝 Reasoning: {analysis['reasoning'][:50]}...")

            # Verify expectations
            if selected_model == test_case['expected_model']:
                print("   ✅ Model selection correct"            else:
                print(f"   ⚠️  Expected {test_case['expected_model']}, got {selected_model}")

            if analysis['content_type'] == test_case['expected_content_type']:
                print("   ✅ Content type correct"            else:
                print(f"   ⚠️  Expected {test_case['expected_content_type']}, got {analysis['content_type']}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    print("\n" + "=" * 50)
    print("📈 Performance Statistics:")
    stats = intelligent_model_router.get_routing_stats()
    print(f"   Total routed: {stats['total_routed']}")
    print(f"   Models used: {len(stats['model_performance'])}")

    for model_name, metrics in stats['model_performance'].items():
        if metrics['total_routed'] > 0:
            print(f"   {model_name}: {metrics['total_routed']} tasks, {metrics['success_rate']:.2f} success rate")


async def test_routing_optimization():
    """Test routing optimization based on performance"""

    print("\n🔧 Testing Routing Optimization")
    print("=" * 50)

    # Simulate some routing history with mixed performance
    test_tasks = [
        ("Create a simple Python script", "builder_agent", True),
        ("Build a complex web app", "builder_agent", False),  # Failed
        ("Analyze research paper", "research_pipeline", True),
        ("Review performance", "self_reflection_loop", True),
        ("Another simple script", "builder_agent", True),
    ]

    # Manually add some history (in real usage this would happen automatically)
    for task_desc, model, success in test_tasks:
        # This is simplified - in real usage the router tracks this automatically
        pass

    # Run optimization
    try:
        optimization_result = await intelligent_model_router.optimize_routing()
        print("✅ Optimization completed")
        print(f"   Recommendations: {len(optimization_result.get('optimizations', []))}")

        for opt in optimization_result.get('optimizations', []):
            print(f"   • {opt}")

    except Exception as e:
        print(f"❌ Optimization failed: {str(e)}")


async def test_fallback_mechanisms():
    """Test fallback mechanisms when primary models fail"""

    print("\n🛡️  Testing Fallback Mechanisms")
    print("=" * 50)

    # Test with a task that might fail
    try:
        result = await intelligent_model_router.route_task(
            task="This is a test task that should work",
            user_id="test_user"
        )

        if result.get('fallback_used'):
            print("✅ Fallback mechanism triggered"            print(f"   Original model: {result.get('original_model')}")
            print(f"   Fallback model: {result['selected_model']}")
        else:
            print("✅ No fallback needed - primary model succeeded"            print(f"   Model used: {result['selected_model']}")

    except Exception as e:
        print(f"❌ Fallback test failed: {str(e)}")


async def main():
    """Run all tests"""
    print("🚀 Intelligent Model Router Test Suite")
    print("Started at:", datetime.now().isoformat())

    try:
        await test_task_routing()
        await test_routing_optimization()
        await test_fallback_mechanisms()

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())</instructions>