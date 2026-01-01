"""
Chatbot PSB - Response Router (Core Orchestrator)

This module implements the core decision and routing logic for the chatbot.
It orchestrates the entire Double Guard Architecture pipeline:

Flow:
1. Receive user question
2. Classify intent using Intent Classifier (Guard Layer 1)
3. Load knowledge base data based on predicted intent
4. Send to Groq API for bounded reasoning (Guard Layer 2)
5. Return final refined response

This is the HEART of the system - where all components come together.

Architecture: Double Guard Orchestrator
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

from intent_classifier import get_intent_classifier, IntentPrediction
from groq_client import get_groq_client, GroqResponse
from database import log_user_question, init_db

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ResponseResult:
    """Data class for final response result"""
    success: bool
    message: str
    intent: str
    confidence: float
    confidence_level: str
    knowledge_base_used: bool
    llm_used: bool
    error: Optional[str] = None
    question_id: Optional[int] = None  # Database record ID


class ResponseRouter:
    """
    Response Router - Core Decision and Routing Logic
    
    This class orchestrates the entire chatbot pipeline using the Double Guard Architecture:
    - Guard 1: Intent Classification (determines context)
    - Guard 2: LLM Bounded Reasoning (refines language)
    
    The router ensures:
    - Intent classifier always runs first
    - Knowledge base is the single source of truth
    - LLM only operates within strict constraints
    - System degrades gracefully on errors
    """
    
    def __init__(self, knowledge_base_dir: str = "knowledge_base"):
        """
        Initialize Response Router.
        
        Args:
            knowledge_base_dir: Directory containing knowledge base JSON files
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)
        
        # Initialize components
        self.intent_classifier = get_intent_classifier()
        self.groq_client = get_groq_client()
        
        logger.info(f"Response Router initialized with KB dir: {self.knowledge_base_dir}")
    
    def process_question(self, question: str, user_id: str = "anonymous", platform: str = "telegram") -> ResponseResult:
        """
        Process a user question through the Double Guard Architecture.
        
        This is the main method that implements the complete pipeline:
        1. Intent Classification (Guard 1)
        2. Knowledge Base Retrieval
        3. LLM Bounded Reasoning (Guard 2)
        4. Response Generation
        5. Database Logging
        
        Args:
            question: User's question text
            user_id: User identifier (e.g., Telegram user ID)
            platform: Platform source (telegram, web, etc)
            
        Returns:
            ResponseResult: Final response with metadata
        """
        if not question or not question.strip():
            logger.warning("Empty question received")
            return self._get_error_response("Pertanyaan tidak boleh kosong.")
        
        logger.info(f"Processing question: {question[:100]}...")
        
        try:
            # STEP 1: Intent Classification (Guard Layer 1)
            logger.info("STEP 1: Running intent classification...")
            intent_prediction = self.intent_classifier.predict(question)
            
            logger.info(
                f"Intent predicted: {intent_prediction.intent} "
                f"(confidence: {intent_prediction.confidence:.2%})"
            )
            
            # STEP 2: Knowledge Base Retrieval
            logger.info("STEP 2: Loading knowledge base...")
            kb_data = self._load_knowledge_base(intent_prediction.intent)
            
            if not kb_data:
                logger.warning(f"No knowledge base data found for intent: {intent_prediction.intent}")
                result = self._get_no_kb_response(intent_prediction)
                # Log to database
                self._log_to_database(
                    user_id=user_id,
                    question=question,
                    result=result,
                    platform=platform,
                    knowledge_base_used=None
                )
                return result
            
            # Count entries based on KB structure
            entry_count = len(kb_data.get('qa_pairs', [])) if 'qa_pairs' in kb_data else len(kb_data.get('core_facts', {}))
            logger.info(f"Loaded {entry_count} KB entries")
            
            # STEP 3: LLM Bounded Reasoning (Guard Layer 2)
            logger.info("STEP 3: Generating response with Groq API...")
            groq_response = self.groq_client.generate_response(
                question=question,
                intent=intent_prediction.intent,
                confidence=intent_prediction.confidence,
                knowledge_base_data=kb_data
            )
            
            # STEP 4: Build final response
            logger.info("STEP 4: Building final response...")
            confidence_level = self.intent_classifier.get_confidence_level(
                intent_prediction.confidence
            )
            
            result = ResponseResult(
                success=groq_response.success,
                message=groq_response.message,
                intent=intent_prediction.intent,
                confidence=intent_prediction.confidence,
                confidence_level=confidence_level,
                knowledge_base_used=True,
                llm_used=groq_response.success,
                error=groq_response.error
            )
            
            # STEP 5: Log to database
            logger.info("STEP 5: Logging to database...")
            question_id = self._log_to_database(
                user_id=user_id,
                question=question,
                result=result,
                platform=platform,
                knowledge_base_used=intent_prediction.intent
            )
            result.question_id = question_id
            
            return result
        
        except Exception as e:
            logger.error(f"Error in response router: {str(e)}", exc_info=True)
            return self._get_error_response(f"Terjadi kesalahan: {str(e)}")
    
    def _load_knowledge_base(self, intent: str) -> Dict[str, Any]:
        """
        Load knowledge base data for a specific intent.
        
        Knowledge base files are named by intent: {intent}.json
        
        Supports two formats:
        - New format: Dict with 'core_facts', 'qa_pairs', 'quick_answers'
        - Legacy format: Dict with 'answers' array
        
        Args:
            intent: Intent label (e.g., "biaya_pendidikan")
            
        Returns:
            Dict: Knowledge base data structure, or empty dict if not found
        """
        kb_file = self.knowledge_base_dir / f"{intent}.json"
        
        if not kb_file.exists():
            logger.warning(f"Knowledge base file not found: {kb_file}")
            return {}
        
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Return full KB structure for new format or wrap legacy format
            if isinstance(data, dict):
                # Check if it's new format (has core_facts) or legacy format (has answers)
                if 'core_facts' in data or 'qa_pairs' in data:
                    # New format - return as is
                    return data
                elif 'answers' in data:
                    # Legacy format - wrap for backwards compatibility  
                    return {"qa_pairs": data['answers'], "_legacy": True}
                else:
                    return data
            elif isinstance(data, list):
                # Very old format - list of entries
                return {"qa_pairs": data, "_legacy": True}
            else:
                logger.warning(f"Unexpected KB format in {kb_file}")
                return {}
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {kb_file}: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error loading KB file {kb_file}: {str(e)}")
            return {}
    
    def _log_to_database(
        self,
        user_id: str,
        question: str,
        result: ResponseResult,
        platform: str,
        knowledge_base_used: Optional[str]
    ) -> Optional[int]:
        """
        Log user question and response to database.
        
        Args:
            user_id: User identifier
            question: Original question text
            result: Response result object
            platform: Platform source
            knowledge_base_used: Which KB file was used
            
        Returns:
            Optional[int]: Question ID if logged successfully, None otherwise
        """
        try:
            question_id = log_user_question(
                user_id=user_id,
                question_text=question,
                predicted_intent=result.intent,
                confidence_score=result.confidence,
                confidence_level=result.confidence_level,
                routed_to="llm" if result.llm_used else "fallback",
                response_text=result.message,
                knowledge_base_used=knowledge_base_used,
                llm_used=result.llm_used,
                error_message=result.error,
                platform=platform
            )
            logger.info(f"Question logged to database with ID: {question_id}")
            return question_id
        except Exception as e:
            logger.error(f"Failed to log question to database: {str(e)}")
            # Don't fail the whole request if logging fails
            return None
    
    def _get_no_kb_response(self, intent_prediction: IntentPrediction) -> ResponseResult:
        """
        Generate response when knowledge base is not available.
        
        Args:
            intent_prediction: Intent prediction result
            
        Returns:
            ResponseResult: Safe fallback response
        """
        message = (
            f"Mohon maaf, informasi untuk topik '{intent_prediction.intent}' "
            "belum tersedia dalam sistem. Silakan hubungi admin untuk informasi lebih lanjut.\n\n"
            "📧 Kontak Admin: [info@pesantren.example.com]"
        )
        
        confidence_level = self.intent_classifier.get_confidence_level(
            intent_prediction.confidence
        )
        
        return ResponseResult(
            success=False,
            message=message,
            intent=intent_prediction.intent,
            confidence=intent_prediction.confidence,
            confidence_level=confidence_level,
            knowledge_base_used=False,
            llm_used=False,
            error="Knowledge base not found"
        )
    
    def _get_error_response(self, error_message: str) -> ResponseResult:
        """
        Generate error response.
        
        Args:
            error_message: Error message to display
            
        Returns:
            ResponseResult: Error response
        """
        return ResponseResult(
            success=False,
            message=f"Mohon maaf, {error_message}\n\nSilakan coba lagi atau hubungi admin.",
            intent="unknown",
            confidence=0.0,
            confidence_level="very_low",
            knowledge_base_used=False,
            llm_used=False,
            error=error_message
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get status of all system components.
        
        Returns:
            Dict: System status information
        """
        return {
            "router": {
                "status": "active",
                "kb_directory": str(self.knowledge_base_dir),
                "kb_exists": self.knowledge_base_dir.exists()
            },
            "intent_classifier": self.intent_classifier.get_model_info(),
            "groq_client": {
                "api_available": self.groq_client.health_check(),
                "model": self.groq_client.model
            }
        }
    
    def list_available_intents(self) -> List[str]:
        """
        List all available intents with knowledge base files.
        
        Returns:
            List[str]: List of intents that have KB files
        """
        if not self.knowledge_base_dir.exists():
            return []
        
        kb_files = list(self.knowledge_base_dir.glob("*.json"))
        return [f.stem for f in kb_files]


# Singleton instance
_router_instance: Optional[ResponseRouter] = None


def get_response_router(knowledge_base_dir: str = "knowledge_base") -> ResponseRouter:
    """
    Get singleton instance of Response Router.
    
    Args:
        knowledge_base_dir: Directory containing knowledge base files
        
    Returns:
        ResponseRouter: Singleton instance
    """
    global _router_instance
    
    if _router_instance is None:
        _router_instance = ResponseRouter(knowledge_base_dir=knowledge_base_dir)
    
    return _router_instance
