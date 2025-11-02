"""Quick verification of ML deployment components"""
# -*- coding: utf-8 -*-

import sys
import os

# Fix console encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("ML DEPLOYMENT SYSTEM VERIFICATION")
print("="*60)

# Check file existence
files_to_check = [
    ("ML Runtime", "ml_runtime.py"),
    ("Model Deployment", "model_deployment.py"),
    ("Deploy CLI", "deploy_model_cli.py"),
    ("Auto Retrain", "auto_retrain.py"),
    ("Training Pipeline", "training_pipeline.py"),
    ("Test Suite", "test_ml_deployment.py")
]

print("\nComponent Files:")
all_exist = True
for name, file in files_to_check:
    exists = os.path.exists(file)
    status = "✓" if exists else "✗"
    print(f"  {status} {name:25} {file}")
    all_exist = all_exist and exists

if not all_exist:
    print("\n❌ Some files are missing!")
    sys.exit(1)

print("\n[OK] All component files present")

# Check imports
print("\nImport Verification:")
try:
    from ml_runtime import ModelRegistry, model_registry
    print("  ✓ ml_runtime.ModelRegistry")
except Exception as e:
    print(f"  ✗ ml_runtime.ModelRegistry: {e}")
    all_exist = False

try:
    from model_deployment import ModelDeploymentPipeline, deployment_pipeline
    print("  ✓ model_deployment.ModelDeploymentPipeline")
except Exception as e:
    print(f"  ✗ model_deployment.ModelDeploymentPipeline: {e}")
    all_exist = False

try:
    from auto_retrain import AutoRetrainEngine, auto_retrain_engine
    print("  ✓ auto_retrain.AutoRetrainEngine")
except Exception as e:
    print(f"  ✗ auto_retrain.AutoRetrainEngine: {e}")
    all_exist = False

try:
    from training_pipeline import TrainingPipeline, training_pipeline
    print("  ✓ training_pipeline.TrainingPipeline (enhanced)")
except Exception as e:
    print(f"  ✗ training_pipeline.TrainingPipeline: {e}")
    all_exist = False

if not all_exist:
    print("\n❌ Some imports failed!")
    sys.exit(1)

print("\n[OK] All imports successful")

# Check methods
print("\nMethod Verification:")

methods_to_check = [
    (model_registry, "save_model"),
    (model_registry, "load_model"),
    (model_registry, "load_latest_model"),
    (model_registry, "deploy_model"),
    (model_registry, "rollback_model"),
    (deployment_pipeline, "verify_model_metrics"),
    (deployment_pipeline, "request_governance_approval"),
    (deployment_pipeline, "deploy_with_pipeline"),
    (deployment_pipeline, "check_auto_deploy_criteria"),
    (auto_retrain_engine, "check_and_retrain"),
    (auto_retrain_engine, "_evaluate_and_deploy"),
    (training_pipeline, "save_model_artifact"),
    (training_pipeline, "load_model_artifact"),
]

all_methods = True
for obj, method in methods_to_check:
    has_method = hasattr(obj, method)
    status = "✓" if has_method else "✗"
    print(f"  {status} {obj.__class__.__name__}.{method}()")
    all_methods = all_methods and has_method

if not all_methods:
    print("\n❌ Some methods are missing!")
    sys.exit(1)

print("\n[OK] All methods present")

# Check configuration
print("\nConfiguration:")
print(f"  Auto-retrain threshold:  {auto_retrain_engine.retrain_threshold} artifacts")
print(f"  Check interval:          {auto_retrain_engine.check_interval}s")
print(f"  Weekly retrain:          {auto_retrain_engine.weekly_retrain}")
print(f"  Auto-deploy enabled:     {auto_retrain_engine.auto_deploy_enabled}")
print(f"  Min accuracy threshold:  {deployment_pipeline.min_accuracy_threshold}")
print(f"  Min test samples:        {deployment_pipeline.min_test_samples}")
print(f"  Improvement threshold:   {deployment_pipeline.improvement_threshold * 100}%")

# Check storage
print("\nStorage:")
print(f"  Artifacts directory:     {model_registry.storage_path}")
print(f"  Directory exists:        {model_registry.storage_path.exists()}")

print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)
print("[OK] All files present")
print("[OK] All imports working")
print("[OK] All methods available")
print("[OK] Configuration loaded")
print("\n[SUCCESS] ML Deployment System is ready!")
print("\nNext steps:")
print("  1. Run: python -m grace_rebuild.backend.deploy_model_cli list-models")
print("  2. Train a model via API or training_pipeline.train_model()")
print("  3. Deploy with: deploy_model_cli deploy <model_id>")
print("  4. Start auto-retrain: auto_retrain_engine.start()")
print("="*60)
