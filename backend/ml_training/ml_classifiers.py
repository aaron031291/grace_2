"""ML-based trust score classifier"""

import pickle
import numpy as np
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, classification_report
from sqlalchemy import select
from .models import async_session
from .ml_models_table import MLModel
from .trusted_sources import trust_manager
import re
from datetime import datetime

class TrustScoreClassifier:
    """ML classifier for URL trust scoring"""
    
    KNOWN_OFFICIAL_DOMAINS = {
        'python.org', 'github.com', 'stackoverflow.com', 'wikipedia.org',
        'arxiv.org', 'npmjs.com', 'pypi.org', 'docs.python.org',
        'developer.mozilla.org', 'w3.org', 'ietf.org', 'microsoft.com',
        'google.com', 'amazon.com', 'apple.com', 'oracle.com',
        'docker.com', 'kubernetes.io', 'tensorflow.org', 'pytorch.org'
    }
    
    TRUSTED_TLDS = {'.gov', '.edu', '.org'}
    SUSPICIOUS_PATTERNS = ['bit.ly', 'tinyurl', 'temp', 'tiny.cc', 't.co']
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            )
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.feature_names = [
            'has_https',
            'is_known_official',
            'has_trusted_tld',
            'is_suspicious',
            'domain_length',
            'path_length',
            'has_subdomain',
            'subdomain_count',
            'path_depth',
            'has_query_params',
            'domain_entropy',
            'has_hyphen',
            'numeric_ratio'
        ]
        self.is_trained = False
    
    def extract_features(self, url: str) -> np.ndarray:
        """Extract features from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path
        
        features = [
            1.0 if parsed.scheme == 'https' else 0.0,
            1.0 if any(d in domain for d in self.KNOWN_OFFICIAL_DOMAINS) else 0.0,
            1.0 if any(tld in domain for tld in self.TRUSTED_TLDS) else 0.0,
            1.0 if any(p in domain for p in self.SUSPICIOUS_PATTERNS) else 0.0,
            min(len(domain) / 50.0, 1.0),
            min(len(path) / 100.0, 1.0),
            1.0 if domain.count('.') > 1 else 0.0,
            float(domain.count('.')),
            float(path.count('/')),
            1.0 if parsed.query else 0.0,
            self._calculate_entropy(domain),
            1.0 if '-' in domain else 0.0,
            sum(c.isdigit() for c in domain) / max(len(domain), 1)
        ]
        
        return np.array(features).reshape(1, -1)
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy for text"""
        if not text:
            return 0.0
        
        from collections import Counter
        counts = Counter(text)
        total = len(text)
        entropy = -sum((count/total) * np.log2(count/total) for count in counts.values())
        return min(entropy / 5.0, 1.0)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train the classifier"""
        if len(X) < 10:
            raise ValueError("Insufficient training data (need at least 10 samples)")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        y_pred = self.model.predict(X_test)
        y_pred_train = self.model.predict(X_train)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='weighted', zero_division=0
        )
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'train_accuracy': accuracy_score(y_train, y_pred_train),
            'test_samples': len(y_test),
            'train_samples': len(y_train),
            'classes': len(np.unique(y))
        }
        
        return metrics
    
    def predict(self, url: str) -> int:
        """Predict trust score (0-100) for URL"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self.extract_features(url)
        prediction = self.model.predict(features)[0]
        
        return int(prediction)
    
    def predict_proba(self, url: str) -> Dict[int, float]:
        """Get probability distribution across trust classes"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self.extract_features(url)
        probabilities = self.model.predict_proba(features)[0]
        
        return {int(cls): float(prob) for cls, prob in zip(self.model.classes_, probabilities)}
    
    def explain(self, url: str) -> Dict:
        """Explain prediction with feature importances"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self.extract_features(url)
        prediction = self.predict(url)
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importances = np.abs(self.model.coef_[0])
        else:
            importances = np.zeros(len(self.feature_names))
        
        feature_values = features[0]
        
        feature_contributions = [
            {
                'feature': name,
                'value': float(value),
                'importance': float(importance)
            }
            for name, value, importance in sorted(
                zip(self.feature_names, feature_values, importances),
                key=lambda x: x[2],
                reverse=True
            )
        ]
        
        return {
            'url': url,
            'predicted_score': prediction,
            'probabilities': self.predict_proba(url) if hasattr(self.model, 'predict_proba') else {},
            'feature_contributions': feature_contributions[:5]
        }
    
    def save(self, model_id: int) -> bytes:
        """Serialize model to bytes"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        return pickle.dumps(model_data)
    
    @classmethod
    def load(cls, model_bytes: bytes) -> 'TrustScoreClassifier':
        """Load model from bytes"""
        model_data = pickle.loads(model_bytes)
        
        classifier = cls(model_type=model_data['model_type'])
        classifier.model = model_data['model']
        classifier.feature_names = model_data['feature_names']
        classifier.is_trained = model_data['is_trained']
        
        return classifier

class TrustClassifierManager:
    """Manage trust classifier lifecycle"""
    
    def __init__(self):
        self._cached_classifier: Optional[TrustScoreClassifier] = None
        self._cache_model_id: Optional[int] = None
    
    async def get_active_classifier(self) -> Optional[TrustScoreClassifier]:
        """Get currently deployed classifier"""
        async with async_session() as session:
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_name == "trust_score_classifier")
                .where(MLModel.deployment_status == "deployed")
                .order_by(MLModel.deployed_at.desc())
            )
            model = result.scalar_one_or_none()
            
            if not model:
                return None
            
            if self._cached_classifier and self._cache_model_id == model.id:
                return self._cached_classifier
            
            if model.signature:
                model_bytes = bytes.fromhex(model.signature)
                classifier = TrustScoreClassifier.load(model_bytes)
                self._cached_classifier = classifier
                self._cache_model_id = model.id
                return classifier
            
            return None
    
    async def predict_with_fallback(self, url: str) -> Tuple[int, str]:
        """Predict trust score with fallback to heuristics"""
        classifier = await self.get_active_classifier()
        
        if classifier:
            try:
                score = classifier.predict(url)
                return score, "ml"
            except Exception as e:
                print(f"⚠️ ML prediction failed: {e}, falling back to heuristics")
        
        score = await trust_manager.get_trust_score(url)
        return int(score), "heuristic"
    
    async def explain_prediction(self, url: str) -> Dict:
        """Get explanation for trust score"""
        classifier = await self.get_active_classifier()
        
        if classifier:
            return classifier.explain(url)
        
        score = await trust_manager.get_trust_score(url)
        return {
            'url': url,
            'predicted_score': int(score),
            'method': 'heuristic',
            'message': 'No ML model deployed, using rule-based scoring'
        }

trust_classifier_manager = TrustClassifierManager()

class AlertSeverityPredictor:
    """Predicts the severity of a security alert."""

    def __init__(self):
        # In a real scenario, this would load a trained model.
        self.is_trained = False

    async def predict_severity(self, alert_data: Dict) -> Tuple[str, float]:
        """
        Predicts the severity of an alert.
        For now, it returns a default severity.
        """
        # Placeholder logic
        return "medium", 0.5

alert_severity_predictor = AlertSeverityPredictor()
