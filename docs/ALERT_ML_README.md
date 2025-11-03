# Alert Severity ML Prediction System

## Overview

This system uses machine learning (Random Forest Classifier) to predict the severity of security alerts based on historical patterns. It integrates seamlessly with the Hunter security monitoring system.

## Features

- **ML-Based Prediction**: Uses sklearn's Random Forest to predict alert severity
- **Feature Engineering**: Extracts 8 key features from alerts:
  - Action type hash
  - Resource pattern (admin/config/api paths)
  - Hour of day
  - Day of week
  - Actor risk score (based on history)
  - Recent alert count
  - Resource path length
  - Action name length

- **High Confidence Override**: ML predictions override rule-based severity when confidence > 90%
- **Transparent Predictions**: Every prediction includes explanation and confidence scores
- **Governance Integration**: Training requires governance approval
- **Model Versioning**: All trained models tracked in ML models table

## Files

### Core Implementation
- `backend/ml_classifiers.py` - AlertSeverityPredictor class
- `backend/training_pipeline.py` - Training orchestration (updated)
- `backend/hunter.py` - Integration with security monitoring (updated)

### Data & Training
- `backend/seed_security_events.py` - Generate synthetic training data
- `backend/train_alert_model.py` - Training script with evaluation
- `backend/test_alert_ml.py` - Comprehensive integration tests

## Quick Start

### 1. Install Dependencies
```bash
cd grace_rebuild
pip install -r requirements.txt
```

### 2. Generate Training Data
```bash
python -m backend.seed_security_events
```

This creates 200+ synthetic security events with realistic patterns across 4 severity levels.

### 3. Train the Model
```bash
python -m backend.train_alert_model
```

This will:
- Train Random Forest classifier on historical events
- Display classification metrics (accuracy, precision, recall, F1)
- Show feature importance
- Test predictions on sample alerts
- Save model to `backend/models/alert_severity_predictor.pkl`

### 4. Run Tests
```bash
python -m backend.test_alert_ml
```

This tests:
- Full ML integration with Hunter
- Alert creation with ML predictions
- Prediction accuracy on random events

## Usage

### Automatic ML Integration

The Hunter system automatically uses ML predictions when:
1. Model is trained and loaded
2. Confidence score > 90%

```python
from backend.hunter import hunter

# Create alert - ML automatically predicts severity
triggered = await hunter.inspect(
    actor="admin",
    action="file_access",
    resource="/etc/passwd",
    payload={"ip": "192.168.1.1"}
)
```

### Manual Prediction

```python
from backend.ml_classifiers import alert_severity_predictor

alert_data = {
    'actor': 'admin',
    'action': 'config_change',
    'resource': '/config/security.yaml',
    'timestamp': datetime.utcnow()
}

severity, confidence = await alert_severity_predictor.predict_severity(alert_data)
explanation = alert_severity_predictor.explain_prediction()

print(f"Predicted: {severity} (confidence: {confidence:.2%})")
print(f"All probabilities: {explanation['all_probabilities']}")
print(f"Features: {explanation['features']}")
```

### Training New Model

```python
from backend.training_pipeline import training_pipeline

result = await training_pipeline.train_alert_predictor(actor="admin")

if result['success']:
    print(f"Accuracy: {result['accuracy']:.2%}")
    print(f"Samples: {result['training_samples']}")
```

## Model Performance

Expected metrics on synthetic data:
- **Accuracy**: 70-90% (depends on training data quality)
- **Features**: 8 engineered features
- **Algorithm**: Random Forest (100 estimators, max_depth=10)
- **Classes**: 4 severity levels (critical, high, medium, low)

### Feature Importance
Top features typically include:
1. Resource pattern (admin/config paths)
2. Actor risk score
3. Recent alert count
4. Action type

## Configuration

### Adjust ML Confidence Threshold

```python
from backend.hunter import hunter

# Set threshold for ML override (default: 0.9)
hunter.ml_confidence_threshold = 0.85  # 85% confidence required

# Disable ML predictions
hunter.use_ml_prediction = False
```

### Model Parameters

Edit `backend/ml_classifiers.py`:

```python
self.model = RandomForestClassifier(
    n_estimators=100,      # Number of trees
    max_depth=10,          # Max tree depth
    random_state=42,       # For reproducibility
    class_weight='balanced' # Handle imbalanced classes
)
```

## Alert Details

When ML is used, alert details include ML metadata:

```json
{
  "ip": "192.168.1.100",
  "method": "GET",
  "ml_prediction": {
    "predicted_severity": "critical",
    "confidence": 0.95,
    "rule_severity": "high",
    "ml_used": true
  }
}
```

## Monitoring

Check ML predictions in logs:
- `🤖 ML override: high → critical (confidence: 95%)` - ML changed severity
- `📊 ML prediction: medium (confidence: 75%, using rule severity)` - Confidence too low
- `⚠️ ML prediction failed: [error], using rule severity` - Fallback to rules

## Retraining

Retrain periodically as new events accumulate:

```bash
# Generate fresh training data from recent events
python -m backend.train_alert_model
```

Model automatically:
- Uses latest security events from database
- Computes new feature importance
- Saves new model version
- Logs training metrics to ML models table

## API Integration

The system integrates with existing APIs:

### Check Recent Predictions
```bash
GET /api/ml/models
GET /api/security/events?limit=10
```

### View Model Metadata
```bash
GET /api/ml/models/{model_id}
```

## Troubleshooting

### "Insufficient data" error
- Need at least 10 events with severity labels
- Run `python -m backend.seed_security_events` to generate data

### "Insufficient variety" error
- Need at least 2 different severity levels
- Check data has critical, high, medium, low events

### Low accuracy
- Generate more training data
- Ensure data has realistic patterns
- Check feature engineering in `_extract_features()`

### ML predictions not working
- Verify model is trained: `ls backend/models/`
- Check `hunter.use_ml_prediction = True`
- Look for errors in logs

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Hunter.inspect()                      │
│  Triggered by security rule match                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│          AlertSeverityPredictor.predict()                │
│  • Extract 8 features from alert                         │
│  • Get actor history (recent alerts, risk score)         │
│  • Predict using Random Forest                           │
│  • Return severity + confidence                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Confidence Check (> 90%)                    │
│  YES: Use ML prediction                                  │
│  NO:  Use rule-based severity                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│           Create SecurityEvent                           │
│  • Store predicted severity                              │
│  • Include ML metadata in details                        │
│  • Log to immutable audit trail                          │
└─────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Collect Real Data**: Replace synthetic data with production alerts
2. **Tune Hyperparameters**: Optimize n_estimators, max_depth, etc.
3. **Add Features**: Include IP reputation, time since last alert, etc.
4. **Try Other Models**: Test XGBoost, Gradient Boosting, Neural Networks
5. **A/B Testing**: Compare ML vs rule-based severity assignments
6. **Feedback Loop**: Allow analysts to correct predictions for retraining

## Contributing

To add new features to the ML model:

1. Update `_extract_features()` in `ml_classifiers.py`
2. Add feature name to `self.feature_names`
3. Retrain model with new features
4. Evaluate feature importance

Example:
```python
def _extract_features(self, alert_data: dict, actor_history: dict = None) -> np.ndarray:
    # ... existing features ...
    
    # New feature: IP reputation score
    ip_reputation = self._get_ip_reputation(alert_data.get('ip', ''))
    
    features = np.array([
        action_hash,
        resource_pattern,
        # ... other features ...
        ip_reputation  # Add new feature
    ]).reshape(1, -1)
    
    return features
```
