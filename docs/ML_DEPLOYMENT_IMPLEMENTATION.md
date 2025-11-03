# ML Deployment & Auto-Retrain Implementation

## Overview

Comprehensive ML deployment system with governance, verification, and automatic retraining capabilities.

## Components Implemented

### 1. ML Runtime (`ml_runtime.py`)

**ModelRegistry Class** - Manages model storage, loading, and deployment lifecycle.

#### Key Features:
- **save_model()**: Serializes trained models to disk with metadata
- **load_model()**: Deserializes models from disk with caching
- **load_latest_model()**: Retrieves latest deployed model by type
- **deploy_model()**: Deploys with comprehensive verification:
  - Model artifact existence check
  - Accuracy threshold validation (>= 0.6)
  - Minimum training samples check (>= 10)
  - Governance approval required
  - Automatic deprecation of previous version
- **rollback_model()**: Reverts to previous deployed version
  - Governance approval required
  - Restores deprecated model to deployed status

#### Storage Structure:
```
ml_artifacts/
  model_<id>.pkl         # Serialized model
  model_<id>_meta.json   # Model metadata
```

### 2. Enhanced Training Pipeline (`training_pipeline.py`)

#### New Methods:
- **save_model_artifact()**: Serializes model to disk after training
- **load_model_artifact()**: Deserializes model for inference
- Updates ml_models table with file path in signature field

#### Integration:
- Automatically saves model artifacts after training
- Stores metadata including model name, version, training samples
- Creates verifiable artifact path for deployment validation

### 3. Model Deployment Pipeline (`model_deployment.py`)

**ModelDeploymentPipeline Class** - End-to-end deployment orchestration.

#### Deployment Stages:

1. **Verification Stage** (`verify_model_metrics`):
   - Accuracy >= 0.6 (configurable threshold)
   - Training samples >= 10
   - Model artifact file exists
   - All metrics evaluated

2. **Governance Stage** (`request_governance_approval`):
   - Policy-based approval required
   - Checks ml_deploy action permissions
   - Records approval decision

3. **Deployment Stage** (`deploy_with_pipeline`):
   - Executes full pipeline
   - Logs events to MLEvent table
   - Atomic deployment with rollback on failure

4. **Auto-Deploy Criteria** (`check_auto_deploy_criteria`):
   - Accuracy improvement >= 5% (configurable)
   - First model with acceptable accuracy
   - Automatic deployment if criteria met

#### Event Logging:
All stages logged to MLEvent table:
- deployment_initiated
- deployment_verified
- deployment_approved
- deployment_denied
- deployment_completed
- deployment_failed

### 4. Enhanced Auto-Retrain Engine (`auto_retrain.py`)

#### Monitoring Triggers:
1. **Knowledge-Based**: >100 new high-trust artifacts
2. **Schedule-Based**: Weekly retrain (7 days)
3. **Manual**: On-demand retrain capability

#### Auto-Retrain Flow:
```
Monitor knowledge_artifacts
  ↓
Detect trigger condition
  ↓
Extract new high-trust content
  ↓
Run signed training pipeline
  ↓
Evaluate model metrics
  ↓
Check improvement threshold (>5%)
  ↓
Auto-deploy if qualified
```

#### Features:
- Tracks high-trust artifacts (trust_score >= 80)
- Simulated model evaluation (accuracy, precision, recall, F1)
- Configurable auto-deploy threshold
- Governance integration throughout

### 5. Deployment CLI (`deploy_model_cli.py`)

#### Commands:

**Deploy Model:**
```bash
python -m grace_rebuild.backend.deploy_model_cli deploy <model_id> [actor]
```
- Runs full deployment pipeline
- Shows verification checks
- Displays governance decision
- Confirms deployment status

**Rollback Model:**
```bash
python -m grace_rebuild.backend.deploy_model_cli rollback <model_type> [actor]
```
- Reverts to previous deployed version
- Requires governance approval
- Shows current and target versions

**List Models:**
```bash
python -m grace_rebuild.backend.deploy_model_cli list-models [model_type]
```
- Shows all models with deployment status
- 🟢 indicator for deployed models
- Displays accuracy, version, created date

**Model Details:**
```bash
python -m grace_rebuild.backend.deploy_model_cli details <model_id>
```
- Complete model information
- Metrics breakdown
- Training details
- Artifact file status

## Database Schema Updates

### MLModel Table Enhancement:
- `signature` field now stores artifact file path
- Enhanced with precision, recall, F1 score metrics
- Deployment lifecycle timestamps

### MLEvent Table:
Records all deployment events with:
- event_type, model_name, version
- accuracy, validation_score
- deployment_status, actor
- event_metadata (JSON)

## End-to-End Test Coverage

### Test Suite (`test_ml_deployment.py`)

#### Test 1: Training Pipeline
- Creates test knowledge artifacts
- Trains classification model
- Verifies artifact file creation
- Confirms database record

#### Test 2: Model Verification
- Sets model metrics (accuracy, F1, etc.)
- Runs verification checks
- Validates thresholds

#### Test 3: Model Deployment
- Full deployment pipeline execution
- Governance approval flow
- Verification of deployed status

#### Test 4: Auto-Retrain
- Creates additional knowledge
- Triggers auto-retrain
- Validates new model creation
- Checks auto-deploy decision

#### Test 5: Model Rollback
- Rolls back to previous version
- Verifies governance check
- Confirms status changes

#### Test 6: Load Latest Model
- Retrieves deployed model
- Loads artifact from disk
- Validates model data

## Usage Examples

### Manual Training & Deployment:

```python
from grace_rebuild.backend.training_pipeline import training_pipeline
from grace_rebuild.backend.model_deployment import deployment_pipeline

# Train model
model_id = await training_pipeline.train_model(
    model_name="intent_classifier",
    model_type="classification",
    trust_threshold=75.0,
    actor="data_scientist"
)

# Set evaluation metrics (from actual model evaluation)
async with async_session() as session:
    model = await session.get(MLModel, model_id)
    model.accuracy = 0.87
    model.f1_score = 0.85
    await session.commit()

# Deploy with full pipeline
success, msg = await deployment_pipeline.deploy_with_pipeline(
    model_id,
    actor="ml_engineer"
)
```

### Auto-Retrain Configuration:

```python
from grace_rebuild.backend.auto_retrain import auto_retrain_engine

# Configure thresholds
auto_retrain_engine.retrain_threshold = 100  # artifacts
auto_retrain_engine.weekly_retrain = True
auto_retrain_engine.auto_deploy_enabled = True

# Start monitoring
await auto_retrain_engine.start()
```

### Load Model for Inference:

```python
from grace_rebuild.backend.ml_runtime import model_registry

# Load latest deployed model
model, artifact = await model_registry.load_latest_model("classification")

# Use for inference
predictions = artifact.predict(input_data)
```

### Rollback After Issues:

```python
from grace_rebuild.backend.ml_runtime import model_registry

# Rollback to previous version
success = await model_registry.rollback_model(
    model_type="classification",
    actor="ops_engineer"
)
```

## Governance Integration

### Required Policies:

1. **ml_train**: Allows model training
   - Checks: trust threshold, data quality
   
2. **ml_deploy**: Allows production deployment
   - Checks: accuracy threshold, verification status
   
3. **ml_rollback**: Allows version rollback
   - Checks: incident severity, approval level

### Verification Points:

- Training: Dataset hash, sample count
- Deployment: Model metrics, artifact existence
- Rollback: Previous version availability

## Monitoring & Observability

### Events Published to Trigger Mesh:

- `mldl.training_completed`
- `mldl.model_deployed`
- `mldl.model_rollback`

### MLEvent Records:

All operations logged with:
- Timestamp
- Actor
- Model version
- Metrics
- Status transitions

## Performance Considerations

### Model Artifact Storage:
- Pickled format for Python objects
- JSON metadata for quick lookups
- Lazy loading with in-memory cache

### Auto-Retrain Optimization:
- Configurable check interval (default: 1 hour)
- Knowledge count queries optimized
- Background task execution

### Deployment Safety:
- Atomic status transitions
- Previous version deprecation
- Rollback capability maintained

## Security Features

1. **Governance-Gated Actions**: All deployments require approval
2. **Verified Training**: Dataset hash verification
3. **Immutable Audit Trail**: MLEvent records
4. **Actor Attribution**: All actions tracked to user

## Future Enhancements

### Recommended:
- A/B testing framework
- Canary deployments
- Model performance monitoring
- Drift detection
- Multi-model ensembles
- Model versioning with semantic versioning
- Automated hyperparameter tuning

## Success Criteria ✓

- ✅ ModelRegistry stores/loads trained models
- ✅ Deployment pipeline with verification
- ✅ Governance approval integration
- ✅ Auto-retrain on new knowledge (>100 artifacts)
- ✅ Weekly retrain schedule
- ✅ Auto-deploy on >5% improvement
- ✅ CLI tools for operations
- ✅ Rollback capability
- ✅ Complete audit trail
- ✅ End-to-end test coverage

## Deployment Checklist

Before deploying this system to production:

1. [ ] Configure governance policies for ml_train, ml_deploy, ml_rollback
2. [ ] Set appropriate accuracy thresholds per model type
3. [ ] Configure auto-retrain intervals
4. [ ] Set up artifact storage backup
5. [ ] Configure monitoring alerts for deployment failures
6. [ ] Test rollback procedures
7. [ ] Document model evaluation procedures
8. [ ] Set up model performance dashboards

## Testing

Run the full test suite:

```bash
cd grace_rebuild/backend
python3 -m pytest test_ml_deployment.py -v -s
```

Or use the test runner:

```bash
python3 test_ml_deployment_runner.py
```

## Contact

For questions or issues with the ML deployment system, refer to the GRACE documentation or create an issue in the repository.
