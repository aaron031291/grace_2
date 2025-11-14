"""ML Classifiers - Re-export from ml_training module"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'TrustScoreClassifier':
        from .ml_training.ml_classifiers import TrustScoreClassifier
        return TrustScoreClassifier
    elif name == 'TrustClassifierManager':
        from .ml_training.ml_classifiers import TrustClassifierManager
        return TrustClassifierManager
    elif name == 'trust_classifier_manager':
        from .ml_training.ml_classifiers import trust_classifier_manager
        return trust_classifier_manager
    elif name == 'AlertSeverityPredictor':
        from .ml_training.ml_classifiers import AlertSeverityPredictor
        return AlertSeverityPredictor
    elif name == 'alert_severity_predictor':
        from .ml_training.ml_classifiers import alert_severity_predictor
        return alert_severity_predictor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'TrustScoreClassifier',
    'TrustClassifierManager', 
    'trust_classifier_manager',
    'AlertSeverityPredictor',
    'alert_severity_predictor'
]
