"""Test the alert severity ML prediction system"""

import asyncio
import json
from datetime import datetime

from backend.models import init_db
from backend.hunter import hunter
from backend.governance_models import SecurityRule
from backend.models import async_session
from backend.ml_classifiers import alert_severity_predictor
from backend.training_pipeline import training_pipeline


async def setup_test_rule():
    """Create a test security rule"""
    async with async_session() as session:
        rule = SecurityRule(
            name="test_admin_access",
            description="Test rule for admin access",
            condition=json.dumps({"action": "admin_access", "keywords": ["sensitive"]}),
            severity="medium",
            action="alert"
        )
        session.add(rule)
        await session.commit()
        print("[OK] Test security rule created")


async def test_ml_integration():
    """Test the full ML integration with Hunter"""
    
    print("\n" + "=" * 70)
    print("Testing ML-Enhanced Alert Severity Prediction")
    print("=" * 70)
    
    await init_db()
    
    print("\n1. Setting up test environment...")
    await setup_test_rule()
    
    print("\n2. Generating training data...")
    from backend.seed_security_events import generate_security_events
    await generate_security_events(200)
    
    print("\n3. Training ML model...")
    result = await training_pipeline.train_alert_predictor(actor="admin")
    
    if not result['success']:
        print(f"❌ Training failed: {result}")
        return
    
    print(f"[OK] Model trained successfully!")
    print(f"  - Accuracy: {result['accuracy']:.2%}")
    print(f"  - Training samples: {result['training_samples']}")
    print(f"  - Test samples: {result['test_samples']}")
    
    print("\n4. Testing alert creation with ML prediction...")
    
    test_cases = [
        {
            'name': 'Critical - Admin file access',
            'actor': 'admin',
            'action': 'admin_access',
            'resource': '/admin/sensitive',
            'payload': {'ip': '192.168.1.100', 'method': 'GET', 'keywords': 'sensitive'}
        },
        {
            'name': 'Low - Regular API call',
            'actor': 'user_1',
            'action': 'admin_access',
            'resource': '/api/search',
            'payload': {'ip': '192.168.1.101', 'method': 'GET', 'keywords': 'sensitive'}
        },
        {
            'name': 'High - Config change',
            'actor': 'devops',
            'action': 'admin_access',
            'resource': '/config/firewall',
            'payload': {'ip': '192.168.1.102', 'method': 'POST', 'keywords': 'sensitive'}
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        print(f"   Actor: {test_case['actor']}, Action: {test_case['action']}")
        print(f"   Resource: {test_case['resource']}")
        
        triggered = await hunter.inspect(
            actor=test_case['actor'],
            action=test_case['action'],
            resource=test_case['resource'],
            payload=test_case['payload']
        )
        
        if triggered:
            print(f"   [OK] Alert triggered: {len(triggered)} rule(s)")
            
            async with async_session() as session:
                from backend.governance_models import SecurityEvent
                from sqlalchemy import select, desc
                
                result = await session.execute(
                    select(SecurityEvent)
                    .order_by(desc(SecurityEvent.created_at))
                    .limit(1)
                )
                event = result.scalar_one_or_none()
                
                if event:
                    details = json.loads(event.details)
                    ml_pred = details.get('ml_prediction', {})
                    
                    print(f"   Severity: {event.severity}")
                    if ml_pred.get('ml_used'):
                        print(f"   [AI] ML-predicted (confidence: {ml_pred['confidence']:.2%})")
                    else:
                        print(f"   📋 Rule-based (ML confidence too low: {ml_pred.get('confidence', 0):.2%})")
                    
                    results.append({
                        'test_case': test_case['name'],
                        'severity': event.severity,
                        'ml_used': ml_pred.get('ml_used', False),
                        'confidence': ml_pred.get('confidence', 0)
                    })
        else:
            print(f"   [WARN] No alerts triggered")
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for result in results:
        ml_icon = "[AI]" if result['ml_used'] else "📋"
        print(f"{ml_icon} {result['test_case']}")
        print(f"   Severity: {result['severity']}, Confidence: {result['confidence']:.2%}")
    
    print("\n" + "=" * 70)
    print("[OK] ML integration test complete!")
    print("=" * 70)


async def test_prediction_accuracy():
    """Test prediction accuracy on known alerts"""
    
    print("\n" + "=" * 70)
    print("Prediction Accuracy Test")
    print("=" * 70)
    
    from backend.governance_models import SecurityEvent
    from sqlalchemy import select, func
    
    async with async_session() as session:
        result = await session.execute(
            select(SecurityEvent)
            .order_by(func.random())
            .limit(20)
        )
        test_events = result.scalars().all()
    
    if len(test_events) < 5:
        print("[WARN] Not enough events for accuracy test")
        return
    
    correct = 0
    total = 0
    
    print(f"\nTesting on {len(test_events)} random events...\n")
    
    for event in test_events:
        alert_data = {
            'actor': event.actor,
            'action': event.action,
            'resource': event.resource,
            'timestamp': event.created_at
        }
        
        predicted_severity, confidence = await alert_severity_predictor.predict_severity(alert_data)
        actual_severity = event.severity
        
        match = predicted_severity == actual_severity
        if match:
            correct += 1
        total += 1
        
        icon = "[OK]" if match else "[FAIL]"
        print(f"{icon} Actual: {actual_severity:8s} | Predicted: {predicted_severity:8s} (confidence: {confidence:.2%})")
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    print("\n" + "-" * 70)
    print(f"Accuracy: {correct}/{total} = {accuracy:.2f}%")
    print("=" * 70)
    
    return accuracy


if __name__ == "__main__":
    asyncio.run(test_ml_integration())
    asyncio.run(test_prediction_accuracy())
