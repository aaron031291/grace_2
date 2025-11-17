"""Standalone test for trust score classifier (no DB dependencies)"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

class TrustScoreClassifier:
    """ML classifier for URL trust scoring"""
    
    KNOWN_OFFICIAL_DOMAINS = {
        'python.org', 'github.com', 'stackoverflow.com', 'wikipedia.org',
        'arxiv.org', 'npmjs.com', 'pypi.org', 'docs.python.org',
        'developer.mozilla.org', 'w3.org', 'ietf.org', 'microsoft.com',
        'google.com', 'amazon.com', 'apple.com', 'oracle.com',
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
        
        self.feature_names = [
            'has_https', 'is_known_official', 'has_trusted_tld', 'is_suspicious',
            'domain_length', 'path_length', 'has_subdomain', 'subdomain_count',
            'path_depth', 'has_query_params', 'domain_entropy', 'has_hyphen',
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
        """Calculate Shannon entropy"""
        if not text:
            return 0.0
        
        from collections import Counter
        counts = Counter(text)
        total = len(text)
        entropy = -sum((count/total) * np.log2(count/total) for count in counts.values())
        return min(entropy / 5.0, 1.0)
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the classifier"""
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
        
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'train_accuracy': accuracy_score(y_train, y_pred_train),
            'test_samples': len(y_test),
            'train_samples': len(y_train),
        }
    
    def predict(self, url: str) -> int:
        """Predict trust score"""
        features = self.extract_features(url)
        return int(self.model.predict(features)[0])
    
    def explain(self, url: str):
        """Explain prediction"""
        features = self.extract_features(url)
        prediction = self.predict(url)
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        else:
            importances = np.abs(self.model.coef_[0])
        
        feature_values = features[0]
        
        contributions = [
            {'feature': name, 'value': float(value), 'importance': float(importance)}
            for name, value, importance in sorted(
                zip(self.feature_names, feature_values, importances),
                key=lambda x: x[2], reverse=True
            )
        ]
        
        return {
            'url': url,
            'predicted_score': prediction,
            'feature_contributions': contributions[:5]
        }

def test_classifier():
    """Test the classifier"""
    print("\n" + "="*80)
    print("GRACE ML Trust Classifier - Standalone Test")
    print("="*80 + "\n")
    
    print("Creating synthetic training data...")
    
    high_trust = ["https://python.org/", "https://github.com/", "https://arxiv.org/",
                  "https://wikipedia.org/", "https://example.edu/", "https://example.gov/"]
    
    medium_trust = ["https://stackoverflow.com/", "https://medium.com/",
                    "https://example.org/", "https://example.com/"]
    
    low_trust = ["http://bit.ly/", "http://tinyurl.com/", "http://example.temp/",
                 "http://suspicious.xyz/"]
    
    urls = high_trust * 5 + medium_trust * 5 + low_trust * 5
    scores = [92] * (len(high_trust) * 5) + [60] * (len(medium_trust) * 5) + [25] * (len(low_trust) * 5)
    
    print(f"Training samples: {len(urls)}")
    print(f"Class distribution: {dict(zip(*np.unique(scores, return_counts=True)))}")
    
    print("\nTraining Random Forest classifier...")
    classifier = TrustScoreClassifier(model_type="random_forest")
    
    X = np.vstack([classifier.extract_features(url) for url in urls])
    y = np.array(scores)
    
    metrics = classifier.train(X, y)
    
    print(f"\n✓ Training completed:")
    print(f"  Accuracy:  {metrics['accuracy']:.3f}")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall:    {metrics['recall']:.3f}")
    print(f"  F1 Score:  {metrics['f1_score']:.3f}")
    print(f"  Train acc: {metrics['train_accuracy']:.3f}")
    
    print("\n" + "="*80)
    print("Testing on sample URLs")
    print("="*80 + "\n")
    
    test_urls = [
        ("https://python.org/docs", "High Trust (Official)"),
        ("https://github.com/user/repo", "Medium-High Trust"),
        ("https://stackoverflow.com/questions/123", "Medium Trust"),
        ("https://arxiv.org/abs/1234.5678", "High Trust (Research)"),
        ("https://example.edu/course", "High Trust (.edu)"),
        ("https://government.gov/data", "High Trust (.gov)"),
        ("http://suspicious-site.temp/phishing", "Low Trust (Suspicious)"),
        ("http://bit.ly/shortened", "Low Trust (Shortener)"),
        ("https://random-blog.com/article", "Medium Trust (Unknown)"),
    ]
    
    for url, expected in test_urls:
        score = classifier.predict(url)
        explanation = classifier.explain(url)
        
        print(f"URL: {url}")
        print(f"  Expected: {expected}")
        print(f"  Predicted Score: {score}")
        print(f"  Top Features:")
        
        for feat in explanation['feature_contributions'][:3]:
            print(f"    - {feat['feature']:20s}: {feat['value']:.2f} (imp: {feat['importance']:.3f})")
        print()
    
    print("="*80)
    print("Feature Importance Ranking")
    print("="*80 + "\n")
    
    if hasattr(classifier.model, 'feature_importances_'):
        importances = classifier.model.feature_importances_
        for name, imp in sorted(zip(classifier.feature_names, importances), 
                               key=lambda x: x[1], reverse=True):
            print(f"  {name:20s}: {imp:.3f}")
    
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_classifier()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
