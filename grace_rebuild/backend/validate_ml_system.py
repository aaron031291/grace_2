"""Validate the ML alert system is properly configured"""

import os
import sys
from pathlib import Path


def validate_files():
    """Check all required files exist"""
    print("=" * 70)
    print("File Validation")
    print("=" * 70)
    
    required_files = [
        'backend/ml_classifiers.py',
        'backend/seed_security_events.py',
        'backend/train_alert_model.py',
        'backend/test_alert_ml.py',
        'ALERT_ML_README.md',
        'ALERT_ML_IMPLEMENTATION.md',
        'run_alert_ml_demo.bat'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            missing.append(file)
    
    if missing:
        print(f"\n❌ {len(missing)} files missing!")
        return False
    else:
        print(f"\n✓ All {len(required_files)} required files present")
        return True


def validate_imports():
    """Check all required imports work"""
    print("\n" + "=" * 70)
    print("Import Validation")
    print("=" * 70)
    
    imports = [
        ('sklearn.ensemble', 'RandomForestClassifier'),
        ('sklearn.preprocessing', 'LabelEncoder'),
        ('sklearn.model_selection', 'train_test_split'),
        ('sklearn.metrics', 'accuracy_score'),
        ('numpy', None),
        ('backend.ml_classifiers', 'AlertSeverityPredictor'),
        ('backend.governance_models', 'SecurityEvent'),
        ('backend.training_pipeline', 'training_pipeline'),
    ]
    
    failed = []
    for module, attr in imports:
        try:
            if attr:
                exec(f"from {module} import {attr}")
                print(f"✓ from {module} import {attr}")
            else:
                exec(f"import {module}")
                print(f"✓ import {module}")
        except ImportError as e:
            print(f"✗ from {module} import {attr} - FAILED: {e}")
            failed.append((module, attr))
    
    if failed:
        print(f"\n❌ {len(failed)} imports failed!")
        print("\nTo fix, run: py -m pip install -r requirements.txt")
        return False
    else:
        print(f"\n✓ All {len(imports)} imports successful")
        return True


def validate_code_structure():
    """Check key classes and methods exist"""
    print("\n" + "=" * 70)
    print("Code Structure Validation")
    print("=" * 70)
    
    try:
        from backend.ml_classifiers import AlertSeverityPredictor
        predictor = AlertSeverityPredictor()
        
        methods = [
            '_extract_features',
            '_get_actor_history',
            'train',
            'predict_severity',
            'explain_prediction',
            'save_model',
            'load_model'
        ]
        
        for method in methods:
            if hasattr(predictor, method):
                print(f"✓ AlertSeverityPredictor.{method}()")
            else:
                print(f"✗ AlertSeverityPredictor.{method}() - MISSING")
                return False
        
        if len(predictor.feature_names) == 8:
            print(f"✓ Feature count: {len(predictor.feature_names)}")
            for i, feature in enumerate(predictor.feature_names, 1):
                print(f"   {i}. {feature}")
        else:
            print(f"✗ Expected 8 features, found {len(predictor.feature_names)}")
            return False
        
        print("\n✓ AlertSeverityPredictor class structure valid")
        return True
        
    except Exception as e:
        print(f"✗ Failed to validate class structure: {e}")
        return False


def validate_hunter_integration():
    """Check Hunter integration"""
    print("\n" + "=" * 70)
    print("Hunter Integration Validation")
    print("=" * 70)
    
    try:
        from backend.hunter import Hunter
        hunter = Hunter()
        
        checks = [
            ('use_ml_prediction', True),
            ('ml_confidence_threshold', 0.9),
        ]
        
        for attr, expected in checks:
            if hasattr(hunter, attr):
                actual = getattr(hunter, attr)
                if actual == expected:
                    print(f"✓ hunter.{attr} = {actual}")
                else:
                    print(f"⚠ hunter.{attr} = {actual} (expected {expected})")
            else:
                print(f"✗ hunter.{attr} - MISSING")
                return False
        
        print("\n✓ Hunter integration configured")
        return True
        
    except Exception as e:
        print(f"✗ Failed to validate Hunter integration: {e}")
        return False


def validate_training_pipeline():
    """Check training pipeline integration"""
    print("\n" + "=" * 70)
    print("Training Pipeline Validation")
    print("=" * 70)
    
    try:
        from backend.training_pipeline import training_pipeline
        
        if hasattr(training_pipeline, 'train_alert_predictor'):
            print("✓ training_pipeline.train_alert_predictor() method exists")
        else:
            print("✗ training_pipeline.train_alert_predictor() - MISSING")
            return False
        
        print("✓ Training pipeline integration complete")
        return True
        
    except Exception as e:
        print(f"✗ Failed to validate training pipeline: {e}")
        return False


def print_summary(results):
    """Print validation summary"""
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
    
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED!")
        print("\nSystem is ready for:")
        print("  1. Generate training data: py -m backend.seed_security_events")
        print("  2. Train the model: py -m backend.train_alert_model")
        print("  3. Run tests: py -m backend.test_alert_ml")
        print("\nOr run everything: run_alert_ml_demo.bat")
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("\nPlease fix the issues above before proceeding.")
    
    print("=" * 70)
    
    return all_passed


def main():
    """Run all validations"""
    print("\n🔍 ML Alert Severity Prediction System - Validation\n")
    
    results = {
        'Files': validate_files(),
        'Imports': validate_imports(),
        'Code Structure': validate_code_structure(),
        'Hunter Integration': validate_hunter_integration(),
        'Training Pipeline': validate_training_pipeline(),
    }
    
    success = print_summary(results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
