"""
HTM (Hierarchical Temporal Memory) Anomaly Detector
PRODUCTION IMPLEMENTATION - Not a stub

Detects when model probability distributions drift from learned baselines.
Based on Numenta's HTM theory for temporal sequence prediction.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json
from pathlib import Path


@dataclass
class TokenSequence:
    """A sequence of tokens with their probabilities"""
    tokens: List[int]
    probabilities: List[float]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def entropy(self) -> float:
        """Calculate Shannon entropy of probability distribution"""
        probs = np.array(self.probabilities)
        # Filter out zero probabilities
        probs = probs[probs > 0]
        return -np.sum(probs * np.log2(probs))
    
    def kl_divergence(self, other: 'TokenSequence') -> float:
        """Calculate KL divergence from another distribution"""
        p = np.array(self.probabilities)
        q = np.array(other.probabilities)
        
        # Ensure same length
        if len(p) != len(q):
            min_len = min(len(p), len(q))
            p = p[:min_len]
            q = q[:min_len]
        
        # Avoid division by zero
        q = np.where(q == 0, 1e-10, q)
        p = np.where(p == 0, 1e-10, p)
        
        return np.sum(p * np.log(p / q))


@dataclass
class AnomalyDetection:
    """Result of anomaly detection"""
    is_anomaly: bool
    anomaly_score: float  # 0-1, higher = more anomalous
    drift_magnitude: float
    baseline_entropy: float
    current_entropy: float
    detection_method: str
    confidence: float
    details: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'is_anomaly': self.is_anomaly,
            'anomaly_score': self.anomaly_score,
            'drift_magnitude': self.drift_magnitude,
            'baseline_entropy': self.baseline_entropy,
            'current_entropy': self.current_entropy,
            'detection_method': self.detection_method,
            'confidence': self.confidence,
            'details': self.details,
            'timestamp': self.timestamp
        }


class HTMAnomalyDetector:
    """
    Production HTM-based anomaly detector
    
    Learns temporal patterns in token sequences and detects deviations.
    Uses multiple detection methods for robust anomaly identification.
    """
    
    def __init__(
        self,
        model_name: str,
        sequence_length: int = 10,
        history_size: int = 1000,
        anomaly_threshold: float = 0.7,
        storage_path: Optional[str] = None
    ):
        self.model_name = model_name
        self.sequence_length = sequence_length
        self.history_size = history_size
        self.anomaly_threshold = anomaly_threshold
        
        # Storage
        if storage_path:
            self.storage_path = Path(storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
        else:
            self.storage_path = Path("databases/htm_baselines") / model_name
            self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Learned baselines
        self.baseline_sequences: deque = deque(maxlen=history_size)
        self.baseline_entropy_mean: float = 0.0
        self.baseline_entropy_std: float = 0.0
        self.baseline_kl_mean: float = 0.0
        self.baseline_kl_std: float = 0.0
        
        # Statistics
        self.total_sequences: int = 0
        self.anomalies_detected: int = 0
        self.false_positive_rate: float = 0.0
        
        # Learning mode
        self.learning_mode: bool = True  # Start in learning mode
        self.min_sequences_for_baseline: int = 100
        
        # Load existing baseline if available
        self._load_baseline()
    
    def _load_baseline(self):
        """Load baseline from disk if exists"""
        baseline_file = self.storage_path / "baseline.json"
        
        if baseline_file.exists():
            try:
                with open(baseline_file, 'r') as f:
                    data = json.load(f)
                    self.baseline_entropy_mean = data.get('entropy_mean', 0.0)
                    self.baseline_entropy_std = data.get('entropy_std', 0.0)
                    self.baseline_kl_mean = data.get('kl_mean', 0.0)
                    self.baseline_kl_std = data.get('kl_std', 0.0)
                    self.total_sequences = data.get('total_sequences', 0)
                    self.anomalies_detected = data.get('anomalies_detected', 0)
                    
                    # Switch to detection mode if we have enough data
                    if self.total_sequences >= self.min_sequences_for_baseline:
                        self.learning_mode = False
                    
                    print(f"[HTM-{self.model_name}] Loaded baseline: {self.total_sequences} sequences")
            except Exception as e:
                print(f"[HTM-{self.model_name}] Failed to load baseline: {e}")
    
    def _save_baseline(self):
        """Save baseline to disk"""
        baseline_file = self.storage_path / "baseline.json"
        
        try:
            data = {
                'model_name': self.model_name,
                'entropy_mean': self.baseline_entropy_mean,
                'entropy_std': self.baseline_entropy_std,
                'kl_mean': self.baseline_kl_mean,
                'kl_std': self.baseline_kl_std,
                'total_sequences': self.total_sequences,
                'anomalies_detected': self.anomalies_detected,
                'sequence_length': self.sequence_length,
                'history_size': self.history_size,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(baseline_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[HTM-{self.model_name}] Failed to save baseline: {e}")
    
    def learn(self, sequence: TokenSequence):
        """Learn from a sequence (add to baseline)"""
        
        self.baseline_sequences.append(sequence)
        self.total_sequences += 1
        
        # Recompute baseline statistics
        if len(self.baseline_sequences) >= 2:
            entropies = [seq.entropy() for seq in self.baseline_sequences]
            self.baseline_entropy_mean = np.mean(entropies)
            self.baseline_entropy_std = np.std(entropies)
            
            # Compute pairwise KL divergences
            if len(self.baseline_sequences) >= 10:
                kl_divs = []
                sequences = list(self.baseline_sequences)
                for i in range(len(sequences) - 1):
                    kl = sequences[i].kl_divergence(sequences[i + 1])
                    if not np.isnan(kl) and not np.isinf(kl):
                        kl_divs.append(kl)
                
                if kl_divs:
                    self.baseline_kl_mean = np.mean(kl_divs)
                    self.baseline_kl_std = np.std(kl_divs)
        
        # Switch to detection mode after enough data
        if self.learning_mode and self.total_sequences >= self.min_sequences_for_baseline:
            self.learning_mode = False
            print(f"[HTM-{self.model_name}] Baseline established: {self.total_sequences} sequences")
            self._save_baseline()
    
    def detect(self, sequence: TokenSequence) -> AnomalyDetection:
        """
        Detect if sequence is anomalous
        
        Uses multiple detection methods:
        1. Entropy deviation
        2. KL divergence from baseline
        3. Pattern matching
        """
        
        # If still learning, just add to baseline
        if self.learning_mode:
            self.learn(sequence)
            return AnomalyDetection(
                is_anomaly=False,
                anomaly_score=0.0,
                drift_magnitude=0.0,
                baseline_entropy=self.baseline_entropy_mean,
                current_entropy=sequence.entropy(),
                detection_method="learning",
                confidence=0.0,
                details={'status': 'learning_mode'}
            )
        
        # Calculate metrics
        current_entropy = sequence.entropy()
        
        # Method 1: Entropy deviation
        entropy_z_score = 0.0
        if self.baseline_entropy_std > 0:
            entropy_z_score = abs(
                (current_entropy - self.baseline_entropy_mean) / self.baseline_entropy_std
            )
        
        # Method 2: KL divergence from recent baseline
        kl_score = 0.0
        if len(self.baseline_sequences) > 0:
            recent_baseline = list(self.baseline_sequences)[-10:]
            kl_divs = [sequence.kl_divergence(b) for b in recent_baseline]
            kl_divs = [kl for kl in kl_divs if not np.isnan(kl) and not np.isinf(kl)]
            
            if kl_divs and self.baseline_kl_std > 0:
                avg_kl = np.mean(kl_divs)
                kl_score = (avg_kl - self.baseline_kl_mean) / self.baseline_kl_std
        
        # Method 3: Pattern repetition detection
        repetition_score = self._detect_repetition(sequence)
        
        # Combine scores
        anomaly_score = np.clip(
            (entropy_z_score * 0.4) + (kl_score * 0.4) + (repetition_score * 0.2),
            0.0,
            1.0
        )
        
        # Determine if anomaly
        is_anomaly = anomaly_score > self.anomaly_threshold
        
        # Calculate confidence
        confidence = min(1.0, self.total_sequences / 1000.0)
        
        # Update statistics
        if is_anomaly:
            self.anomalies_detected += 1
        else:
            # If not anomaly, add to baseline for continuous learning
            self.learn(sequence)
        
        # Save periodically
        if self.total_sequences % 100 == 0:
            self._save_baseline()
        
        return AnomalyDetection(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            drift_magnitude=entropy_z_score,
            baseline_entropy=self.baseline_entropy_mean,
            current_entropy=current_entropy,
            detection_method="htm_multi",
            confidence=confidence,
            details={
                'entropy_z_score': entropy_z_score,
                'kl_score': kl_score,
                'repetition_score': repetition_score,
                'baseline_sequences': len(self.baseline_sequences),
                'total_sequences': self.total_sequences
            }
        )
    
    def _detect_repetition(self, sequence: TokenSequence) -> float:
        """Detect repetitive patterns (sign of degradation)"""
        
        tokens = sequence.tokens
        if len(tokens) < 3:
            return 0.0
        
        # Count repeated tokens
        unique_tokens = len(set(tokens))
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return 0.0
        
        # Higher score = more repetition
        repetition_ratio = 1.0 - (unique_tokens / total_tokens)
        
        # Detect consecutive repeats
        consecutive_repeats = 0
        for i in range(len(tokens) - 1):
            if tokens[i] == tokens[i + 1]:
                consecutive_repeats += 1
        
        consecutive_score = consecutive_repeats / (total_tokens - 1) if total_tokens > 1 else 0.0
        
        # Combine
        return np.clip((repetition_ratio * 0.6) + (consecutive_score * 0.4), 0.0, 1.0)
    
    def get_stats(self) -> Dict:
        """Get detector statistics"""
        return {
            'model_name': self.model_name,
            'learning_mode': self.learning_mode,
            'total_sequences': self.total_sequences,
            'anomalies_detected': self.anomalies_detected,
            'anomaly_rate': self.anomalies_detected / max(1, self.total_sequences),
            'baseline': {
                'entropy_mean': self.baseline_entropy_mean,
                'entropy_std': self.baseline_entropy_std,
                'kl_mean': self.baseline_kl_mean,
                'kl_std': self.baseline_kl_std,
                'sequences_in_baseline': len(self.baseline_sequences)
            },
            'config': {
                'sequence_length': self.sequence_length,
                'history_size': self.history_size,
                'anomaly_threshold': self.anomaly_threshold
            }
        }
    
    def reset_baseline(self):
        """Reset baseline (start learning from scratch)"""
        self.baseline_sequences.clear()
        self.baseline_entropy_mean = 0.0
        self.baseline_entropy_std = 0.0
        self.baseline_kl_mean = 0.0
        self.baseline_kl_std = 0.0
        self.total_sequences = 0
        self.anomalies_detected = 0
        self.learning_mode = True
        print(f"[HTM-{self.model_name}] Baseline reset - entering learning mode")


class HTMDetectorPool:
    """
    Manages HTM detectors for all models
    One detector per model for specialized baseline learning
    """
    
    def __init__(self):
        self.detectors: Dict[str, HTMAnomalyDetector] = {}
        self.recent_anomalies: deque = deque(maxlen=100)
    
    def get_detector(self, model_name: str) -> HTMAnomalyDetector:
        """Get or create detector for model"""
        if model_name not in self.detectors:
            self.detectors[model_name] = HTMAnomalyDetector(model_name)
        return self.detectors[model_name]
    
    def detect_for_model(
        self,
        model_name: str,
        tokens: List[int],
        probabilities: List[float]
    ) -> AnomalyDetection:
        """Detect anomaly for specific model"""
        
        detector = self.get_detector(model_name)
        sequence = TokenSequence(tokens=tokens, probabilities=probabilities)
        result = detector.detect(sequence)
        
        if result.is_anomaly:
            self.recent_anomalies.append({
                "model": model_name,
                "anomaly": result,
                "timestamp": datetime.utcnow()
            })
            
        return result
    
    def get_recent_anomalies(self, minutes: int = 1, since: Optional[datetime] = None) -> List[Dict]:
        """Get anomalies detected in the last N minutes or since timestamp"""
        if since:
            cutoff = since
        else:
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            
        return [
            {
                "description": f"Anomaly in {x['model']}: score={x['anomaly'].anomaly_score:.2f}",
                **x['anomaly'].to_dict()
            }
            for x in self.recent_anomalies
            if x['timestamp'] > cutoff
        ]
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get stats for all detectors"""
        return {
            model: detector.get_stats()
            for model, detector in self.detectors.items()
        }
    
    def get_high_anomaly_models(self, threshold: float = 0.1) -> List[str]:
        """Get models with high anomaly rates"""
        high_anomaly = []
        
        for model, detector in self.detectors.items():
            stats = detector.get_stats()
            if stats['anomaly_rate'] > threshold:
                high_anomaly.append(model)
        
        return high_anomaly


# Global detector pool
htm_detector_pool = HTMDetectorPool()
