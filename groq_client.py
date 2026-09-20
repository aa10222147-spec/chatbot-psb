"""
Chatbot PSB - Groq API Client (Guard Layer 2)

This module implements the Groq API client for bounded reasoning and language refinement.
It serves as the second guard layer in the Double Guard Architecture.

Key Responsibilities:
- Receive structured input (question, intent, confidence, KB data)
- Perform bounded reasoning within strict constraints
- Refine responses into natural, polite language
- NEVER modify intents or add facts outside knowledge base
- Generate safe fallback responses when needed

Restrictions (CRITICAL):
- LLM CANNOT change predicted intent
- LLM CANNOT add information not in knowledge base
- LLM CANNOT answer questions outside PSB domain
- LLM CANNOT act as primary decision maker
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# Admin contact shown in every fail-safe / fallback message.
# Update this single constant whenever the contact number changes.
ADMIN_CONTACT = "📞 WhatsApp Admin: 0812-3456-7890 (Ustadz Dian Amarullah)"


@dataclass
class GroqResponse:
    """Data class for Groq API response"""
    success: bool
    message: str
    intent: str
    confidence: float
    error: Optional[str] = None


class GroqClient:
    """
    Groq API Client for bounded LLM reasoning.
    
    This client enforces strict guardrails to ensure the LLM:
    1. Only refines language and improves readability
    2. Never modifies the predicted intent
    3. Never adds facts outside the knowledge base
    4. Never answers questions outside PSB domain
    """
    
    def __init__(self):
        """
        Initialize Groq API client.
        
        Raises:
            ValueError: If GROQ_API_KEY environment variable is not set
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
        
        logger.info(f"Groq client initialized with model: {self.model}")
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt with strict guardrails.
        
        This prompt enforces the boundaries of what the LLM can and cannot do.
        
        Returns:
            str: System prompt with guardrails
        """
        return """Anda adalah asisten chatbot resmi Penerimaan Santri Baru (PSB) Pondok Pesantren Gemayasih.

IDENTITAS & NADA:
- Nama panggilan Anda: Admin PSB Pesantren
- Gunakan register FORMAL-ISLAMI: santun, tawadhu', dan mencerminkan akhlak pesantren
- Sapa penanya dengan sebutan "Antum" atau "Anda" secara konsisten
- Awali setiap jawaban dengan "Wa'alaikumussalam wa rahmatullahi wa barakatuh" HANYA jika pertanyaan diawali salam, atau cukup "Bismillah," untuk pertanyaan biasa
- Gunakan diksi Islami yang tepat: "insya Allah", "alhamdulillah", "jazakallah khairan", "silakan", "berkenan"
- Akhiri jawaban dengan doa atau salam penutup yang hangat dan umum, misalnya: "Semoga bermanfaat dan dimudahkan segala urusannya. Aamiin."

ATURAN KETAT (WAJIB DIIKUTI):
1. Anda HANYA boleh menggunakan informasi dari Knowledge Base yang diberikan
2. Anda TIDAK BOLEH menambahkan informasi baru atau asumsi di luar Knowledge Base
3. Anda TIDAK BOLEH mengubah intent yang sudah diprediksi oleh sistem
4. Anda HANYA boleh memperbaiki dan memperindah bahasa agar lebih formal-islami
5. Jika informasi tidak tersedia di Knowledge Base, sampaikan dengan jujur dan arahkan ke admin
6. Jawab HANYA seputar topik PSB Pondok Pesantren
7. Jika pertanyaan di luar topik PSB, alihkan dengan sopan ke admin pesantren

TUGAS ANDA:
- Baca Knowledge Base yang diberikan dengan seksama
- Susun jawaban yang natural, takzim, informatif, dan mencerminkan nilai-nilai pesantren
- Gunakan HANYA fakta dari Knowledge Base
- Pertahankan semua angka, syarat, dan ketentuan PERSIS seperti di Knowledge Base

FORMAT JAWABAN:
- Gunakan bahasa Indonesia formal dengan sentuhan diksi Islami
- Struktur yang jelas: pembuka salam/doa → isi jawaban → penutup/saran konfirmasi
- Hindari bahasa gaul, singkatan informal, atau diksi yang tidak mencerminkan etika pesantren
- Gunakan kata "berkenan", "silakan", "dipersilakan", "kami haturkan", "mohon maaf" dengan tepat
- Jika perlu menyebut nomor atau tautan, sampaikan dengan jelas dan lengkap
- Akhiri dengan kontak admin dan/atau doa singkat jika konteks mengharuskannya"""
    
    def _build_user_prompt(
        self,
        question: str,
        intent: str,
        confidence: float,
        knowledge_base_data: List[Dict[str, Any]]
    ) -> str:
        """
        Build the user prompt with structured information.
        
        Args:
            question: User's original question
            intent: Predicted intent from classification model
            confidence: Confidence score of intent prediction
            knowledge_base_data: Relevant data from knowledge base
            
        Returns:
            str: Structured user prompt
        """
        # Format knowledge base data
        kb_text = self._format_knowledge_base(knowledge_base_data)
        
        # Confidence-aware instruction (register formal-islami)
        if confidence < 0.5:
            confidence_instruction = """
INSTRUKSI KHUSUS (Tingkat Keyakinan Rendah):
1. PERIKSA terlebih dahulu: apakah pertanyaan penanya berkaitan dengan topik "{}"?
2. JIKA BERKAITAN:
   - Awali dengan kalimat: "Berdasarkan pemahaman kami atas pertanyaan Antum, insya Allah kami sampaikan sebagai berikut..."
   - Jawab secara lengkap berlandaskan Knowledge Base
   - Akhiri dengan: "Untuk mendapatkan kepastian yang lebih akurat, kami persilakan Antum untuk menghubungi admin pesantren kami secara langsung."
   - Sertakan kontak admin
3. JIKA TIDAK BERKAITAN: Alihkan dengan santun ke admin tanpa menjawab detail
""".format(intent)
        elif confidence < 0.7:
            confidence_instruction = "INSTRUKSI: Sampaikan jawaban dengan hati-hati dan penuh tawadhu'. Pertimbangkan untuk menganjurkan konfirmasi langsung kepada admin pesantren."
        else:
            confidence_instruction = "INSTRUKSI: Sampaikan jawaban dengan mantap, lugas, dan penuh keyakinan berlandaskan Knowledge Base. Alhamdulillah."

        prompt = f"""INFORMASI KONTEKS:
- Topik/Intent yang teridentifikasi: {intent}
- Tingkat keyakinan sistem: {confidence:.2%}
- Pertanyaan yang diajukan: "{question}"

KNOWLEDGE BASE RESMI PESANTREN:
{kb_text}

{confidence_instruction}

TUGAS ANDA:
- Jawab pertanyaan berdasarkan Knowledge Base di atas
- Gunakan HANYA informasi yang tersedia di Knowledge Base
- Pertahankan semua angka, syarat, dan ketentuan PERSIS seperti tercantum di Knowledge Base
- Gunakan bahasa formal-islami: takzim, santun, dan mencerminkan akhlak pesantren
- Sertakan sapaan dan penutup yang hangat sesuai register Islami

Jawaban Anda:"""
        
        return prompt
    
    def _format_knowledge_base(self, kb_data: Any) -> str:
        """
        Format knowledge base data into readable text for LLM prompt.
        
        Supports:
        - New format: Dict with 'core_facts', 'qa_pairs', 'quick_answers'
        - Legacy format: List of Q&A pairs or wrapped legacy structure
        
        Args:
            kb_data: Knowledge base data (Dict or List)
            
        Returns:
            str: Formatted knowledge base text
        """
        if not kb_data:
            return "Tidak ada informasi yang tersedia di Knowledge Base untuk intent ini."
        
        # Handle new format (Dict with core_facts)
        if isinstance(kb_data, dict):
            if 'core_facts' in kb_data or ('qa_pairs' in kb_data and not kb_data.get('_legacy')):
                return self._format_new_kb(kb_data)
            elif 'qa_pairs' in kb_data:
                # Legacy format wrapped as qa_pairs
                return self._format_legacy_kb(kb_data['qa_pairs'])
        
        # Handle legacy format (List)
        if isinstance(kb_data, list):
            return self._format_legacy_kb(kb_data)
        
        return f"Format KB tidak dikenali: {type(kb_data)}"
    
    def _format_new_kb(self, kb_data: Dict[str, Any]) -> str:
        """
        Format new KB structure for LLM prompt.
        
        New format is more token-efficient with separate sections:
        - core_facts: Factual data (numbers, dates, links)
        - qa_pairs: Template Q&A for context
        - quick_answers: Short answers for common questions
        
        Args:
            kb_data: Dict with core_facts, qa_pairs, quick_answers
            
        Returns:
            str: Formatted KB text
        """
        parts = []
        
        # Add description if available
        if 'description' in kb_data:
            parts.append(f"TOPIK: {kb_data['description']}")
        
        # Add core facts (compact, factual - CRITICAL for accuracy)
        if 'core_facts' in kb_data and kb_data['core_facts']:
            parts.append("\nFAKTA INTI (GUNAKAN DATA INI PERSIS):")
            for key, value in kb_data['core_facts'].items():
                # Format key nicely (replace underscores with spaces)
                display_key = key.replace('_', ' ').title()
                parts.append(f"• {display_key}: {value}")
        
        # Add Q&A pairs if available (limit to top 5 for token efficiency)
        if 'qa_pairs' in kb_data and kb_data['qa_pairs']:
            parts.append("\nCONTOH JAWABAN:")
            for idx, qa in enumerate(kb_data['qa_pairs'][:5], 1):
                q = qa.get('q', qa.get('question', ''))
                a = qa.get('a', qa.get('answer', ''))
                parts.append(f"{idx}. Q: {q}")
                parts.append(f"   A: {a}")
        
        # Add quick answers for common questions
        if 'quick_answers' in kb_data and kb_data['quick_answers']:
            parts.append("\nJAWABAN SINGKAT:")
            for key, value in kb_data['quick_answers'].items():
                display_key = key.replace('_', ' ').title()
                parts.append(f"• {display_key}: {value}")
        
        return "\n".join(parts)
    
    def _format_legacy_kb(self, kb_data: List[Dict[str, Any]]) -> str:
        """
        Format legacy KB structure (list of Q&A pairs).
        
        Args:
            kb_data: List of Q&A entries
            
        Returns:
            str: Formatted KB text
        """
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
                entry_id = entry.get("id", f"entry-{idx}")
                formatted_entries.append(f"{idx}. [{entry_id}] {text}")
            else:
                # Fallback: stringify the entire entry
                formatted_entries.append(f"{idx}. {entry}")
        
        return "\n\n".join(formatted_entries)
    
    def generate_response(
        self,
        question: str,
        intent: str,
        confidence: float,
        knowledge_base_data: List[Dict[str, Any]]
    ) -> GroqResponse:
        """
        Generate a bounded response using Groq API.
        
        This is the main method that performs bounded reasoning and language refinement.
        
        Args:
            question: User's original question
            intent: Predicted intent from classification model
            confidence: Confidence score (0.0 to 1.0)
            knowledge_base_data: Relevant entries from knowledge base
            
        Returns:
            GroqResponse: Response object containing refined answer
        """
        try:
            logger.info(f"Generating response for intent: {intent} (confidence: {confidence:.2%})")
            
            # Build prompts with guardrails
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(question, intent, confidence, knowledge_base_data)
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 0.9,
                "stream": False
            }
            
            # Call Groq API
            logger.debug(f"Calling Groq API with model: {self.model}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            refined_message = response_data["choices"][0]["message"]["content"].strip()
            
            logger.info("Response generated successfully")
            
            return GroqResponse(
                success=True,
                message=refined_message,
                intent=intent,  # Intent NEVER changes
                confidence=confidence
            )
        
        except requests.exceptions.Timeout:
            logger.error("Groq API request timeout")
            return self._generate_fallback_response(
                intent, confidence, knowledge_base_data,
                error="API timeout"
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {str(e)}")
            return self._generate_fallback_response(
                intent, confidence, knowledge_base_data,
                error=f"API error: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in Groq client: {str(e)}", exc_info=True)
            return self._generate_fallback_response(
                intent, confidence, knowledge_base_data,
                error=f"Unexpected error: {str(e)}"
            )
    
    def _generate_fallback_response(
        self,
        intent: str,
        confidence: float,
        knowledge_base_data: Any,
        error: str
    ) -> GroqResponse:
        """
        Generate a safe fallback response when Groq API fails.
        
        This ensures the system degrades gracefully without LLM assistance.
        Supports both new dict format (core_facts/qa_pairs/quick_answers)
        and legacy list format KB data.
        
        Args:
            intent: Predicted intent
            confidence: Confidence score
            knowledge_base_data: KB data to use directly (Dict or List)
            error: Error message
            
        Returns:
            GroqResponse: Fallback response using KB data directly
        """
        logger.info("Generating fallback response (KB-only mode)")
        
        try:
            # Use _format_knowledge_base() which already handles both
            # new dict format (core_facts/qa_pairs/quick_answers) AND
            # legacy list format — avoids the 'str has no .get' crash.
            if knowledge_base_data:
                kb_formatted = self._format_knowledge_base(knowledge_base_data)
                
                fallback_message = (
                    "Bismillah,\n\n"
                    "Mohon maaf, layanan AI sedang mengalami gangguan sementara. "
                    "Berikut informasi dari Knowledge Base kami yang semoga dapat membantu:\n\n"
                    f"{kb_formatted}"
                )
                
                # Add confidence warning if needed
                if confidence < 0.7:
                    fallback_message += (
                        f"\n\n⚠️ Catatan: Tingkat keyakinan sistem terhadap topik ini "
                        f"{confidence:.0%}. Untuk kepastian yang lebih akurat, silakan "
                        "hubungi admin pesantren secara langsung."
                    )
                
                fallback_message += (
                    f"\n\n{ADMIN_CONTACT}"
                    "\n\nSemoga bermanfaat dan dimudahkan segala urusannya. Aamiin."
                )
            else:
                fallback_message = (
                    "Mohon maaf, layanan AI sedang mengalami gangguan sementara dan "
                    "informasi yang Anda cari tidak tersedia saat ini. "
                    f"Untuk bantuan langsung, silakan hubungi:\n{ADMIN_CONTACT}"
                )
        except Exception as fmt_exc:
            # Last-resort: even the formatter failed — return a safe static message
            logger.error(
                f"Fallback formatter also failed: {fmt_exc}", exc_info=True
            )
            fallback_message = (
                "Mohon maaf, layanan AI sedang mengalami gangguan. "
                f"Silakan hubungi admin pesantren untuk informasi lebih lanjut:\n{ADMIN_CONTACT}"
            )
        
        return GroqResponse(
            success=False,
            message=fallback_message,
            intent=intent,
            confidence=confidence,
            error=error
        )
    
    def health_check(self) -> bool:
        """
        Check if Groq API is accessible.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Groq API health check failed: {str(e)}")
            return False


# Singleton instance
_groq_client_instance: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """
    Get singleton instance of Groq client.
    
    Returns:
        GroqClient: Singleton instance
    """
    global _groq_client_instance
    
    if _groq_client_instance is None:
        _groq_client_instance = GroqClient()
    
    return _groq_client_instance
