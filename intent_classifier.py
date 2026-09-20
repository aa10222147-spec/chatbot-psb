"""
Chatbot PSB - Intent Classifier (Guard Layer 1)

This module implements the intent classification system using classical NLP techniques.
It serves as the FIRST and PRIMARY guard layer in the Double Guard Architecture.

Key Responsibilities:
- Classify user queries into predefined intents
- Generate confidence scores for predictions
- Constrain the answer space based on intent
- Act as the PRIMARY decision maker in the system

Technology:
- Algorithm: TF-IDF + Logistic Regression
- Framework: scikit-learn
- Models: Pre-trained and serialized as .pkl files

Architecture Role: Guard Layer 1 - Context Controller
"""

import os
import re
import joblib
import logging
import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.70


@dataclass
class IntentPrediction:
    """Data class for intent prediction results"""
    intent: str
    confidence: float
    all_probabilities: Dict[str, float]
    is_confident: bool  # True if confidence >= threshold


class IntentClassifier:
    """
    Intent Classification System - Guard Layer 1
    
    This is the PRIMARY NLP component in the chatbot system.
    It determines the context of user queries and constrains the answer space.
    
    The intent classifier ALWAYS runs first, before any LLM interaction.
    Even with low confidence, it still provides a best-match intent (demo mode).
    """
    
    def __init__(
        self,
        models_dir: str = "models",
        confidence_threshold: float = CONFIDENCE_THRESHOLD
    ):
        """
        Initialize the Intent Classifier.
        
        Args:
            models_dir: Directory containing trained model files (.pkl)
            confidence_threshold: Minimum confidence score for high-confidence predictions
            
        Raises:
            FileNotFoundError: If required model files are not found
            ValueError: If models cannot be loaded
        """
        self.models_dir = Path(models_dir)
        self.confidence_threshold = confidence_threshold
        
        # Model components
        self.vectorizer = None
        self.model = None
        self.label_encoder = None
        
        # Load models
        self._load_models()
        
        logger.info(f"Intent Classifier initialized with {len(self.get_all_intents())} intents")
    
    def _load_models(self):
        """
        Load a complete trained model bundle.

        The production system must never silently fall back to a mock classifier.
        We support the current bundle plus the tracked v1 bundle so deployment
        remains resilient if one artifact is unavailable.
        """
        model_bundles = [
            (
                "models-v2",
                self.models_dir / "vectorizer_2.pkl",
                self.models_dir / "lr_intent_model_2.pkl",
                self.models_dir / "label_encoder_2.pkl",
            ),
            (
                "models-v1",
                self.models_dir / "v1" / "vectorizer.pkl",
                self.models_dir / "v1" / "intent_model.pkl",
                self.models_dir / "v1" / "label_encoder.pkl",
            ),
        ]

        missing_by_bundle = []

        for bundle_name, vectorizer_path, model_path, label_encoder_path in model_bundles:
            paths = {
                "vectorizer": vectorizer_path,
                "model": model_path,
                "label_encoder": label_encoder_path,
            }
            missing = [name for name, path in paths.items() if not path.is_file()]

            if missing:
                missing_by_bundle.append(
                    f"{bundle_name}: missing {', '.join(missing)}"
                )
                continue

            try:
                logger.info(
                    "Loading trained intent classifier bundle: %s "
                    "(vectorizer=%s, model=%s, encoder=%s)",
                    bundle_name,
                    vectorizer_path,
                    model_path,
                    label_encoder_path,
                )

                vectorizer = joblib.load(vectorizer_path)
                model = joblib.load(model_path)
                label_encoder = joblib.load(label_encoder_path)

                if not hasattr(vectorizer, "transform"):
                    raise ValueError("Loaded vectorizer does not implement transform()")
                if not hasattr(model, "predict_proba"):
                    raise ValueError("Loaded classifier does not implement predict_proba()")
                if not hasattr(label_encoder, "inverse_transform"):
                    raise ValueError("Loaded label encoder does not implement inverse_transform()")

                # Validate that the model output classes can be mapped to intent labels.
                class_count = len(getattr(model, "classes_", []))
                label_count = len(getattr(label_encoder, "classes_", []))
                if class_count and label_count and class_count != label_count:
                    raise ValueError(
                        f"Model/label encoder class mismatch: "
                        f"model={class_count}, encoder={label_count}"
                    )

                self.vectorizer = vectorizer
                self.model = model
                self.label_encoder = label_encoder
                self.model_bundle = bundle_name
                self.model_path = str(model_path)
                self._is_mock = False

                logger.info(
                    "Trained intent classifier loaded successfully: "
                    "bundle=%s intents=%d",
                    bundle_name,
                    len(self.get_all_intents()),
                )
                return

            except Exception as e:
                logger.exception(
                    "Failed to load trained model bundle %s: %s",
                    bundle_name,
                    e,
                )

        # Mock classification is intentionally opt-in. A production deployment
        # must fail fast instead of producing academically invalid predictions.
        if os.getenv("ALLOW_MOCK_CLASSIFIER", "").strip().lower() == "true":
            logger.warning(
                "ALLOW_MOCK_CLASSIFIER=true: enabling mock classifier explicitly"
            )
            self._initialize_mock_classifier()
            return

        details = "; ".join(missing_by_bundle) if missing_by_bundle else "no valid model bundle"
        raise RuntimeError(
            "No valid trained intent classifier is available. "
            "Production deployment is blocked. "
            f"Checked bundles: {details}"
        )

    def _initialize_mock_classifier(self):
        """
        Initialize a mock classifier for development/demo when models are not available.
        
        This allows the system to run without trained models for initial setup.
        """
        logger.warning("MOCK CLASSIFIER ACTIVE - Not suitable for production!")
        
        # Create mock components
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import LabelEncoder
        
        # Define mock intents based on knowledge base structure
        mock_intents = [
            "info_pendaftaran",
            "syarat_pendaftaran",
            "biaya_pendidikan",
            "program_unggulan",
            "faq_umum"
        ]
        
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.model = LogisticRegression()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(mock_intents)
        
        # Mark as mock
        self._is_mock = True
    
    def predict(self, text: str) -> IntentPrediction:
        """
        Predict the intent of a user query.
        
        This is the main method that performs intent classification.
        It ALWAYS returns a prediction, even with low confidence (demo mode).
        
        Args:
            text: User's input text/question
            
        Returns:
            IntentPrediction: Prediction with intent label, confidence, and probabilities
        """
        if not text or not text.strip():
            logger.warning("Empty text received for prediction")
            return self._get_fallback_prediction()
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Check if using mock classifier
            if hasattr(self, '_is_mock') and self._is_mock:
                return self._mock_predict(processed_text)
            
            # Vectorize input
            text_vector = self.vectorizer.transform([processed_text])
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(text_vector)[0]
            
            # Get predicted class index
            predicted_idx = np.argmax(probabilities)
            
            # Get intent label
            intent = self.label_encoder.inverse_transform([predicted_idx])[0]
            
            # Get confidence (max probability)
            confidence = float(probabilities[predicted_idx])
            
            # Build probability dictionary for all intents
            all_probabilities = {}
            for idx, prob in enumerate(probabilities):
                intent_name = self.label_encoder.inverse_transform([idx])[0]
                all_probabilities[intent_name] = float(prob)
            
            # Check if prediction is confident
            is_confident = confidence >= self.confidence_threshold
            
            logger.info(
                f"Predicted intent: {intent} (confidence: {confidence:.2%}, "
                f"threshold: {self.confidence_threshold:.2%})"
            )
            
            return IntentPrediction(
                intent=intent,
                confidence=confidence,
                all_probabilities=all_probabilities,
                is_confident=is_confident
            )
        
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}", exc_info=True)
            return self._get_fallback_prediction()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before classification.
        
        Args:
            text: Raw input text
            
        Returns:
            str: Preprocessed text
        """
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)   # sama dengan clean_text di notebook
        return re.sub(r'\s+', ' ', text).strip()
    
    def _mock_predict(self, text: str) -> IntentPrediction:
        """
        Generate mock prediction for development/demo.
        
        Uses simple keyword matching to simulate intent classification.
        
        Args:
            text: Preprocessed input text
            
        Returns:
            IntentPrediction: Mock prediction
        """
        logger.warning("Using MOCK prediction - not production-ready")
        
        # Simple keyword-based mock prediction
        keywords_map = {
            "info_pendaftaran": ["pendaftaran", "daftar", "cara daftar", "mendaftar"],
            "syarat_pendaftaran": ["syarat", "persyaratan", "requirement", "butuh"],
            "biaya_pendidikan": ["biaya", "harga", "uang", "bayar", "spp", "cost"],
            "program_unggulan": ["program", "unggulan", "kurikulum", "pelajaran"],
            "faq_umum": ["kontak", "alamat", "lokasi", "dimana", "apa itu"]
        }
        
        # Count keyword matches
        intent_scores = {}
        for intent, keywords in keywords_map.items():
            score = sum(1 for keyword in keywords if keyword in text)
            intent_scores[intent] = score
        
        # Get best match
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]
        
        # If no keyword match, use fallback
        if max_score == 0:
            best_intent = "faq_umum"
            confidence = 0.3
        else:
            # Simulate confidence based on match count
            confidence = min(0.5 + (max_score * 0.15), 0.95)
        
        # Create mock probabilities
        all_probabilities = {}
        remaining_prob = 1.0 - confidence
        other_intents = [i for i in keywords_map.keys() if i != best_intent]
        
        all_probabilities[best_intent] = confidence
        for intent in other_intents:
            all_probabilities[intent] = remaining_prob / len(other_intents)
        
        return IntentPrediction(
            intent=best_intent,
            confidence=confidence,
            all_probabilities=all_probabilities,
            is_confident=confidence >= self.confidence_threshold
        )
    
    def _get_fallback_prediction(self) -> IntentPrediction:
        """
        Get a safe fallback prediction when classification fails.
        
        Returns:
            IntentPrediction: Fallback prediction with low confidence
        """
        fallback_intent = "faq_umum"
        fallback_confidence = 0.0
        
        all_intents = self.get_all_intents()
        all_probabilities = {intent: 0.0 for intent in all_intents}
        all_probabilities[fallback_intent] = fallback_confidence
        
        return IntentPrediction(
            intent=fallback_intent,
            confidence=fallback_confidence,
            all_probabilities=all_probabilities,
            is_confident=False
        )
    
    def get_all_intents(self) -> List[str]:
        """
        Get list of all possible intents.
        
        Returns:
            List[str]: List of intent labels
        """
        if self.label_encoder is None:
            return []
        
        try:
            return list(self.label_encoder.classes_)
        except Exception:
            return [
                "info_pendaftaran",
                "syarat_pendaftaran",
                "biaya_pendidikan",
                "program_unggulan",
                "faq_umum"
            ]
    
    def validate_intent(self, intent: str) -> bool:
        """
        Validate if an intent exists in the model.
        
        Args:
            intent: Intent label to validate
            
        Returns:
            bool: True if intent is valid, False otherwise
        """
        return intent in self.get_all_intents()
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Get human-readable confidence level.
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            str: Confidence level description
        """
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= self.confidence_threshold:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        elif confidence >= 0.3:
            return "low"
        else:
            return "very_low"

    def get_confidence_status(self, confidence: float) -> str:
        """Return 'high' for normal flow and 'low' for graceful degradation."""
        return "high" if confidence >= self.confidence_threshold else "low"
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the loaded models.

        Returns:
            Dict: Model information and statistics
        """
        return {
            "is_mock": hasattr(self, '_is_mock') and self._is_mock,
            "num_intents": len(self.get_all_intents()),
            "intents": self.get_all_intents(),
            "confidence_threshold": self.confidence_threshold,
            "models_directory": str(self.models_dir),
            "model_bundle": getattr(self, "model_bundle", None),
            "model_path": getattr(self, "model_path", None),
            "vectorizer_loaded": self.vectorizer is not None,
            "model_loaded": self.model is not None,
            "label_encoder_loaded": self.label_encoder is not None,
        }

# Singleton instance
_classifier_instance: Optional[IntentClassifier] = None


def get_intent_classifier(
    models_dir: str = "models",
    confidence_threshold: float = CONFIDENCE_THRESHOLD
) -> IntentClassifier:
    """
    Get singleton instance of Intent Classifier.
    
    Args:
        models_dir: Directory containing model files
        confidence_threshold: Confidence threshold for predictions
        
    Returns:
        IntentClassifier: Singleton instance
    """
    global _classifier_instance
    
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier(
            models_dir=models_dir,
            confidence_threshold=confidence_threshold
        )
    
    return _classifier_instance
