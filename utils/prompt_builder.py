"""
Chatbot PSB - Prompt Builder with Guardrails

This module builds structured prompts for the LLM with strict guardrails.
It implements the PROMPT_GUARD.md specification to ensure:
- LLM operates within bounded reasoning constraints
- No hallucination or uncontrolled responses
- Intent-based operational boundaries
- Standardized prompt construction for AI safety

This is the THIRD control layer:
1. NLP Model → Context control
2. Knowledge Base Schema → Factual control  
3. Prompt Guard (THIS MODULE) → LLM behavior control

Reference: doc/PROMPT_GUARD.md
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PromptComponents:
    """Data class for prompt components"""
    system_prompt: str
    user_prompt: str
    metadata: Dict[str, Any]


class PromptBuilder:
    """
    Prompt Builder with Strict Guardrails
    
    This class constructs prompts according to PROMPT_GUARD.md specification.
    
    Key Principles:
    - LLM is NOT a primary decision maker
    - LLM is NOT authorized to determine intent
    - LLM is NOT permitted to introduce new facts
    - LLM is NOT allowed to answer outside PSB context
    
    The LLM role: Bounded Reasoning and Language Refinement Layer
    """
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    MEDIUM_CONFIDENCE_THRESHOLD = 0.5
    LOW_CONFIDENCE_THRESHOLD = 0.3
    
    def __init__(self):
        """Initialize Prompt Builder"""
        logger.info("Prompt Builder initialized with strict guardrails")
    
    def build_prompt(
        self,
        user_question: str,
        intent: str,
        confidence: float,
        knowledge_base_data: List[Dict[str, Any]]
    ) -> PromptComponents:
        """
        Build a complete prompt with guardrails.
        
        This is the main method that constructs prompts according to
        PROMPT_GUARD.md Section 4 (Global System Prompt) and 
        Section 5 (Standard User Prompt Template).
        
        Args:
            user_question: Original user question
            intent: Predicted intent from classifier
            confidence: Confidence score (0.0 to 1.0)
            knowledge_base_data: Official KB entries
            
        Returns:
            PromptComponents: System prompt, user prompt, and metadata
        """
        # Build system prompt with strict rules
        system_prompt = self._build_system_prompt()
        
        # Build user prompt with mandatory structure
        user_prompt = self._build_user_prompt(
            user_question=user_question,
            intent=intent,
            confidence=confidence,
            knowledge_base_data=knowledge_base_data
        )
        
        # Build metadata for logging/debugging
        metadata = {
            "intent": intent,
            "confidence": confidence,
            "confidence_level": self._get_confidence_level(confidence),
            "kb_entries_count": len(knowledge_base_data),
            "guardrails_version": "1.0"
        }
        
        logger.debug(f"Prompt built for intent: {intent} (confidence: {confidence:.2%})")
        
        return PromptComponents(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata=metadata
        )
    
    def _build_system_prompt(self) -> str:
        """
        Build the global system prompt.
        
        This implements PROMPT_GUARD.md Section 4: Global System Prompt
        
        This prompt MUST be prepended to every LLM call.
        It establishes the strict rules and boundaries for LLM behavior.
        
        Returns:
            str: Global system prompt with guardrails
        """
        system_prompt = """Anda adalah asisten untuk chatbot Penerimaan Santri Baru (PSB) Pondok Pesantren.

ATURAN KETAT (WAJIB DIPATUHI):
1. Gunakan HANYA informasi yang disediakan dalam Knowledge Base
2. JANGAN menambahkan, menyimpulkan, atau membuat informasi baru
3. JANGAN mengubah intent yang telah diprediksi
4. Jika pertanyaan user tidak sesuai dengan intent, berikan respons aman dan sarankan hubungi admin
5. Gunakan bahasa yang sopan, formal, dan sesuai nilai-nilai Islam
6. Jika tidak yakin, arahkan user untuk menghubungi administrator

PERAN ANDA:
Anda adalah lapisan reasoning sekunder.
Model klasifikasi intent adalah pengambil keputusan utama.

LARANGAN MUTLAK:
- JANGAN memberikan nomor, tanggal, atau persyaratan baru
- JANGAN menggabungkan informasi dari berbagai intent
- JANGAN menjawab pertanyaan di luar domain PSB
- JANGAN melakukan obrolan bebas
- JANGAN mengganti atau menafsirkan ulang klasifikasi intent
- JANGAN mengasumsikan informasi yang tidak ada

Prioritas Anda: Keakuratan > Kelengkapan"""
        
        return system_prompt
    
    def _build_user_prompt(
        self,
        user_question: str,
        intent: str,
        confidence: float,
        knowledge_base_data: List[Dict[str, Any]]
    ) -> str:
        """
        Build the user prompt with mandatory structure.
        
        This implements PROMPT_GUARD.md Section 5: Standard User Prompt Template
        
        Args:
            user_question: User's original question
            intent: Predicted intent
            confidence: Confidence score
            knowledge_base_data: KB entries
            
        Returns:
            str: Structured user prompt
        """
        # Format knowledge base content
        kb_text = self._format_knowledge_base(knowledge_base_data)
        
        # Determine confidence behavior
        confidence_instruction = self._get_confidence_instruction(confidence)
        
        # Build structured prompt
        user_prompt = f"""Pertanyaan User:
"{user_question}"

Intent yang Diprediksi:
"{intent}"

Confidence Score:
{confidence:.2%}

Konten Knowledge Base Resmi:
{kb_text}

{confidence_instruction}

TUGAS ANDA:
1. EVALUASI: Apakah pertanyaan user relevan dengan intent "{intent}"?
   
2. JIKA RELEVAN (pertanyaan cocok dengan intent):
   - Jawab berdasarkan Knowledge Base yang disediakan
   - Gunakan semua informasi yang relevan dari KB
   - Sampaikan dengan bahasa yang sopan dan jelas
   - Pertahankan SEMUA angka dan fakta PERSIS seperti di KB
   - Jika confidence rendah, tambahkan disclaimer dan saran konfirmasi
   
3. JIKA TIDAK RELEVAN (pertanyaan tidak cocok dengan intent):
   - JANGAN coba jawab dengan menebak
   - Berikan respons aman: arahkan ke admin
   - Jelaskan bahwa pertanyaan di luar cakupan sistem otomatis

Berikan respons Anda:"""
        
        return user_prompt
    
    def _format_knowledge_base(self, kb_data: List[Dict[str, Any]]) -> str:
        """
        Format knowledge base data into readable text.
        
        Args:
            kb_data: List of KB entries
            
        Returns:
            str: Formatted KB text
        """
        if not kb_data:
            return "⚠️ Tidak ada konten Knowledge Base yang tersedia untuk intent ini."
        
        formatted_entries = []
        for idx, entry in enumerate(kb_data, 1):
            # Support both formats: {"text": ...} and {"question": ..., "answer": ...}
            if "question" in entry and "answer" in entry:
                # Q&A format (standard KB format)
                question = entry.get("question", "")
                answer = entry.get("answer", "")
                formatted_entries.append(f"{idx}. Q: {question}\n   A: {answer}")
            elif "text" in entry:
                # Simple text format (legacy)
                text = entry.get("text", "")
                entry_id = entry.get("id", f"kb-{idx}")
                formatted_entries.append(f"{idx}. [{entry_id}] {text}")
            else:
                # Fallback: stringify the entire entry
                formatted_entries.append(f"{idx}. {entry}")
        
        return "\n\n".join(formatted_entries)
    
    def _get_confidence_instruction(self, confidence: float) -> str:
        """
        Get confidence-aware instruction for the LLM.
        
        This implements PROMPT_GUARD.md Section 8: Confidence-Aware Behavior Rules
        
        Args:
            confidence: Confidence score
            
        Returns:
            str: Confidence-specific instruction
        """
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            # High confidence: answer confidently
            return """STATUS CONFIDENCE: TINGGI
Anda dapat menjawab dengan percaya diri menggunakan konten KB."""
        
        elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            # Medium confidence: use cautious wording
            return """STATUS CONFIDENCE: SEDANG
Gunakan kata-kata yang hati-hati dan hindari klaim yang terlalu pasti.
Pertimbangkan untuk menyarankan konfirmasi dengan admin."""
        
        else:
            # Low confidence: answer with strong disclaimer
            return """STATUS CONFIDENCE: RENDAH ⚠️
INSTRUKSI KHUSUS:
- PERIKSA apakah pertanyaan user COCOK dengan intent yang diprediksi
- JIKA COCOK: Jawab berdasarkan Knowledge Base, TAPI:
  * Awali dengan disclaimer: "Berdasarkan pemahaman saya terhadap pertanyaan Anda..."
  * Sampaikan informasi dari KB dengan jelas dan lengkap
  * Akhiri dengan: "Untuk memastikan informasi lebih akurat, silakan konfirmasi dengan admin kami."
  * Sertakan kontak admin
- JIKA TIDAK COCOK: Berikan respons aman dan arahkan ke admin
- JANGAN mengubah atau menambah fakta dari KB"""
    
    def _get_confidence_level(self, confidence: float) -> str:
        """
        Get human-readable confidence level.
        
        Args:
            confidence: Confidence score
            
        Returns:
            str: Confidence level label
        """
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            return "high"
        elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return "medium"
        elif confidence >= self.LOW_CONFIDENCE_THRESHOLD:
            return "low"
        else:
            return "very_low"
    
    def build_safe_fallback_prompt(
        self,
        user_question: str,
        reason: str = "intent mismatch"
    ) -> PromptComponents:
        """
        Build a safe fallback prompt when normal processing cannot proceed.
        
        This implements PROMPT_GUARD.md Section 9: Intent Mismatch Handling
        
        Args:
            user_question: User's question
            reason: Reason for fallback
            
        Returns:
            PromptComponents: Safe fallback prompt
        """
        system_prompt = self._build_system_prompt()
        
        user_prompt = f"""Pertanyaan User:
"{user_question}"

STATUS: FALLBACK MODE
Alasan: {reason}

TUGAS ANDA:
Berikan respons aman berikut:
"Mohon maaf, pertanyaan tersebut belum dapat kami jawab secara otomatis. Untuk memastikan informasi yang tepat, silakan menghubungi admin pesantren.

📧 Kontak Admin: [info@pesantren.example.com]"

Sesuaikan sedikit bahasa agar lebih natural, tetapi tetap arahkan ke admin."""
        
        metadata = {
            "intent": "fallback",
            "confidence": 0.0,
            "confidence_level": "fallback",
            "kb_entries_count": 0,
            "fallback_reason": reason,
            "guardrails_version": "1.0"
        }
        
        return PromptComponents(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata=metadata
        )
    
    def validate_prompt_structure(self, components: PromptComponents) -> bool:
        """
        Validate that prompt components meet guardrail requirements.
        
        Args:
            components: Prompt components to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # System prompt must exist and contain key guardrails
            if not components.system_prompt:
                logger.error("System prompt is empty")
                return False
            
            required_keywords = ["ATURAN KETAT", "Knowledge Base", "JANGAN"]
            if not all(kw in components.system_prompt for kw in required_keywords):
                logger.error("System prompt missing required guardrail keywords")
                return False
            
            # User prompt must exist and contain mandatory structure
            if not components.user_prompt:
                logger.error("User prompt is empty")
                return False
            
            required_sections = ["Pertanyaan User:", "Intent yang Diprediksi:", "Confidence Score:"]
            if not all(section in components.user_prompt for section in required_sections):
                logger.error("User prompt missing required sections")
                return False
            
            # Metadata must exist
            if not components.metadata:
                logger.error("Metadata is missing")
                return False
            
            logger.debug("Prompt structure validation passed")
            return True
        
        except Exception as e:
            logger.error(f"Prompt validation error: {str(e)}")
            return False
    
    def get_guardrails_summary(self) -> Dict[str, Any]:
        """
        Get summary of active guardrails and constraints.
        
        Returns:
            Dict: Guardrails summary
        """
        return {
            "version": "1.0",
            "specification": "PROMPT_GUARD.md",
            "control_layer": 3,
            "llm_role": "Bounded Reasoning and Language Refinement",
            "primary_decision_maker": "Intent Classification Model",
            "forbidden_actions": [
                "Introduce new facts",
                "Change predicted intent",
                "Answer outside PSB domain",
                "Free-form chatting",
                "Assume missing information"
            ],
            "allowed_actions": [
                "Rephrase for clarity",
                "Improve politeness",
                "Adjust sentence structure",
                "Provide disclaimers",
                "Suggest admin contact"
            ],
            "confidence_thresholds": {
                "high": self.HIGH_CONFIDENCE_THRESHOLD,
                "medium": self.MEDIUM_CONFIDENCE_THRESHOLD,
                "low": self.LOW_CONFIDENCE_THRESHOLD
            }
        }


# Singleton instance
_prompt_builder_instance: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """
    Get singleton instance of Prompt Builder.
    
    Returns:
        PromptBuilder: Singleton instance
    """
    global _prompt_builder_instance
    
    if _prompt_builder_instance is None:
        _prompt_builder_instance = PromptBuilder()
    
    return _prompt_builder_instance
