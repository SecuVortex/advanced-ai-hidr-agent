"""ML Threat Model - Phase 3 Task 3.3"""
import os
import logging
import numpy as np

logger = logging.getLogger('HIDR.ThreatModel')

class ThreatModel:
    def __init__(self):
        self.model = None
        self.model_path = 'models/threat_classifier.pkl'
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if exists"""
        if os.path.exists(self.model_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                logger.info("ML model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
                self.model = None
        else:
            logger.info("No pre-trained model found, using heuristics")
    
    def predict(self, features):
        """Predict threat probability"""
        if self.model is None:
            return self._heuristic_predict(features)
        
        try:
            feature_vector = [features.get(k, 0) for k in ['name_length', 'path_is_trusted', 
                             'cmdline_length', 'cpu_percent', 'memory_mb', 'num_threads',
                             'num_connections', 'has_signature', 'parent_is_trusted']]
            prob = self.model.predict_proba([feature_vector])[0][1]
            return prob
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._heuristic_predict(features)
    
    def _heuristic_predict(self, features):
        """Fallback heuristic prediction"""
        score = 0
        if features.get('path_is_trusted', 0) == 0:
            score += 0.3
        if features.get('cpu_percent', 0) > 0.5:
            score += 0.2
        if features.get('num_connections', 0) > 0.3:
            score += 0.2
        if features.get('parent_is_trusted', 0) == 0:
            score += 0.3
        return min(score, 1.0)
    
    def train(self, X, y):
        """Train model on data"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            import joblib
            
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info("Model trained and saved successfully")
        except Exception as e:
            logger.error(f"Training failed: {e}")
