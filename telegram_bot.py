"""
Chatbot PSB - Telegram Bot Handler

This module handles all Telegram Bot API interactions.
It serves as the integration layer between Telegram and the chatbot logic.

Responsibilities:
- Receive webhook updates from Telegram
- Extract user messages from updates
- Send messages to Response Router for processing
- Send responses back to users via Telegram Bot API
- Handle command messages (/start, /help, etc.)

Integration: Telegram Bot API ↔ Response Router
"""

import inspect
import os
import re
import httpx
import logging
from typing import Dict, Optional, Any

from response_router import get_response_router, ResponseResult

# Configure logging
logger = logging.getLogger(__name__)


class TelegramBotHandler:
    """
    Telegram Bot Handler
    
    Handles communication with Telegram Bot API:
    - Processes incoming webhook updates
    - Sends messages to users
    - Manages bot commands
    - Integrates with Response Router for chatbot logic
    """

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Convert Markdown-formatted LLM output into plain Telegram text."""
        if not text:
            return text

        cleaned = text
        cleaned = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", cleaned)
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)
        cleaned = re.sub(r"__(.+?)__", r"\1", cleaned)
        cleaned = re.sub(r"_(.+?)_", r"\1", cleaned)
        cleaned = cleaned.replace("`", "")
        cleaned = cleaned.replace("~", "")
        cleaned = cleaned.replace("#", "")
        return cleaned.strip()

    @staticmethod
    def _escape_markdown(text: str) -> str:
        """Escape Markdown characters so Telegram does not strip LLM answer content."""
        if not text:
            return text

        escaped = text.replace('\\', '\\\\')
        for char in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            escaped = escaped.replace(char, f'\\{char}')
        return escaped
    
    def __init__(self):
        """
        Initialize Telegram Bot Handler.
        
        Raises:
            ValueError: If TELEGRAM_BOT_TOKEN is not set
        """
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Initialize response router
        self.response_router = get_response_router()
        
        logger.info("Telegram Bot Handler initialized")
    
    async def process_update(self, update_data: Dict[str, Any]):
        """
        Process an incoming Telegram update.
        
        This is the main entry point called by the webhook endpoint.
        
        Args:
            update_data: Telegram update object as JSON dict
        """
        try:
            # Extract message from update
            if 'message' not in update_data:
                logger.debug("Update does not contain a message, skipping")
                return
            
            message = update_data['message']
            
            # Extract chat and user info
            chat_id = message.get('chat', {}).get('id')
            user_id = message.get('from', {}).get('id')
            username = message.get('from', {}).get('username', 'Unknown')
            
            if not chat_id:
                logger.warning("No chat_id found in message")
                return
            
            logger.info(f"Processing message from user {username} (chat_id: {chat_id})")
            
            # Handle different message types
            if 'text' in message:
                text = message['text'].strip()
                
                # Check if it's a command
                if text.startswith('/'):
                    await self._handle_command(chat_id, text, username)
                else:
                    await self._handle_text_message(chat_id, text, username)
            else:
                # Non-text message
                await self.send_message(
                    chat_id,
                    "Mohon maaf, saya hanya dapat memproses pesan teks. "
                    "Silakan kirim pertanyaan Anda dalam bentuk teks."
                )
        
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}", exc_info=True)
    
    async def _handle_command(self, chat_id: int, command: str, username: str):
        """
        Handle bot commands (/start, /help, etc.).
        
        Args:
            chat_id: Telegram chat ID
            command: Command text (e.g., "/start")
            username: User's username
        """
        logger.info(f"Handling command: {command}")
        
        command_lower = command.lower().split()[0]  # Get first word only
        
        if command_lower == '/start':
            message = self._get_welcome_message(username)
        elif command_lower == '/help':
            message = self._get_help_message()
        elif command_lower == '/status':
            message = self._get_status_message()
        elif command_lower == '/about':
            message = self._get_about_message()
        else:
            message = (
                f"Perintah '{command}' tidak dikenali.\n\n"
                "Perintah yang tersedia:\n"
                "/start - Mulai menggunakan bot\n"
                "/help - Bantuan penggunaan\n"
                "/status - Status sistem\n"
                "/about - Tentang chatbot ini"
            )
        
        await self.send_message(chat_id, message)
    
    async def _handle_text_message(self, chat_id: int, text: str, username: str):
        """
        Handle regular text messages (questions).
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            username: User's username
        """
        logger.info(f"Processing question from {username}: {text[:100]}")
        
        # Send typing indicator
        await self._send_chat_action(chat_id, "typing")
        
        # Process question through response router (with user_id for database logging)
        response_result = self.response_router.process_question(
            question=text,
            user_id=str(chat_id),
            platform="telegram"
        )
        if inspect.isawaitable(response_result):
            response_result = await response_result
        
        # Build response message
        message = self._build_response_message(response_result)
        response_result.message = message

        if getattr(response_result, 'question_id', None):
            update_result = self.response_router.update_logged_question_response(
                response_result.question_id,
                message,
            )
            if inspect.isawaitable(update_result):
                await update_result
        
        # Send response
        await self.send_message(chat_id, message)
        
        # Log response metadata
        logger.info(
            f"Response sent - Intent: {response_result.intent}, "
            f"Confidence: {response_result.confidence:.2%}, "
            f"Success: {response_result.success}"
        )
    
    @staticmethod
    def _normalize_plaintext_message(text: str) -> str:
        """Normalize LLM text into clean, readable plain text for Telegram."""
        if not text:
            return ""

        cleaned = TelegramBotHandler._strip_markdown(str(text))
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

        lines = []
        for raw_line in cleaned.split("\n"):
            line = re.sub(r"\s+", " ", raw_line).strip()
            if line:
                lines.append(line)

        paragraphs = []
        current_paragraph = []
        for line in lines:
            bullet_match = re.match(r"^[-*•]\s+|^\d+[\.)]\s+", line)
            if bullet_match:
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph).strip())
                    current_paragraph = []
                paragraphs.append(line)
            else:
                current_paragraph.append(line)

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph).strip())

        normalized = "\n\n".join(part.strip() for part in paragraphs if part.strip())
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    def _build_response_message(self, result: ResponseResult) -> str:
        """
        Build formatted response message for Telegram.
        
        Args:
            result: Response result from router
            
        Returns:
            str: Formatted message text
        """
        message = self._normalize_plaintext_message(result.message or "")

        logger.info("[FINAL RESPONSE] %s", message)

        # Show a confidence note for all uncertain tiers (2–4) according to the
        # graceful-degradation policy: 0.30 <= confidence < 0.70.
        # For Tier 4 (< 0.30), the fallback message already includes the score;
        # this prevents duplicate notes while keeping the score visible.
        if result.confidence > 0 and result.confidence < 0.70 and "Tingkat keyakinan sistem" not in message:
            if message and not message.endswith((".", "!", "?")):
                message += "."

            confidence_note = (
                f"\n\nCatatan: Tingkat keyakinan sistem {result.confidence:.0%}. "
                "Jawaban ini tetap perlu kehati-hatian dan dapat dikonfirmasi ke admin."
            )
            message += confidence_note

        logger.info("[FINAL RESPONSE] %s", message)
        
        # Add debug info in development mode
        if os.getenv("ENVIRONMENT") == "development":
            message += (
                f"\n\n🔍 Debug Info:\n"
                f"Intent: {result.intent}\n"
                f"Confidence: {result.confidence:.2%}\n"
                f"KB Used: {'✓' if result.knowledge_base_used else '✗'}\n"
                f"LLM Used: {'✓' if result.llm_used else '✗'}"
            )
        
        return message
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None
    ) -> bool:
        """
        Send a message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            parse_mode: Telegram parse mode (Markdown or HTML)
            
        Returns:
            bool: True if message sent successfully
        """
        url = f"{self.api_base_url}/sendMessage"

        plain_text = self._strip_markdown(text or "")
        payload = {
            "chat_id": chat_id,
            "text": plain_text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        response = None
        try:
            async def _post_with_compat(client: httpx.AsyncClient, *args, **kwargs):
                result = client.post(*args, **kwargs)
                if inspect.isawaitable(result):
                    return await result
                return result

            async with httpx.AsyncClient() as client:
                response = await _post_with_compat(client, url, json=payload, timeout=10.0)
            response.raise_for_status()
            
            logger.debug(f"Message sent successfully to chat_id {chat_id}")
            return True
        
        except httpx.HTTPError as e:
            # Log detailed error from Telegram API
            try:
                error_detail = response.json() if response is not None else None
                logger.error(f"Telegram API Error: {error_detail}")
            except Exception:
                logger.error(f"Failed to send message: {str(e)}")
            
            # Try again without parse_mode if it failed
            if parse_mode:
                try:
                    payload_without_mode = dict(payload)
                    del payload_without_mode["parse_mode"]
                    async with httpx.AsyncClient() as client:
                        retry_response = await _post_with_compat(client, url, json=payload_without_mode, timeout=10.0)
                    retry_response.raise_for_status()
                    logger.info("Message sent successfully without parse_mode")
                    return True
                except Exception as retry_error:
                    try:
                        retry_detail = retry_response.json() if 'retry_response' in locals() else None
                        logger.error(f"Retry also failed: {retry_detail}")
                    except Exception:
                        logger.error(f"Retry also failed: {str(retry_error)}")
            
            return False
    
    async def _send_chat_action(self, chat_id: int, action: str = "typing"):
        """
        Send chat action (typing indicator).
        
        Args:
            chat_id: Telegram chat ID
            action: Chat action type (typing, upload_photo, etc.)
        """
        url = f"{self.api_base_url}/sendChatAction"
        
        payload = {
            "chat_id": chat_id,
            "action": action
        }
        
        try:
            async def _post_with_compat(client: httpx.AsyncClient, *args, **kwargs):
                result = client.post(*args, **kwargs)
                if inspect.isawaitable(result):
                    return await result
                return result

            async with httpx.AsyncClient() as client:
                await _post_with_compat(client, url, json=payload, timeout=5.0)
        except Exception as e:
            logger.debug(f"Failed to send chat action: {str(e)}")
    
    def _get_welcome_message(self, username: str) -> str:
        """Get welcome message for /start command"""
        # Use plain text to avoid Markdown parsing issues
        return f"""Assalamualaikum Warahmatullahi Wabarakatuh! 👋

Halo {username}, selamat datang di Chatbot PSB Pondok Pesantren.

Saya adalah asisten digital yang siap membantu Anda mendapatkan informasi tentang Penerimaan Santri Baru (PSB).

Apa yang bisa saya bantu?
📋 Informasi pendaftaran
✅ Syarat pendaftaran
💰 Biaya pendidikan
🎓 Program unggulan
❓ Pertanyaan umum lainnya

Cara menggunakan:
Cukup kirim pertanyaan Anda dan saya akan memberikan informasi yang Anda butuhkan.

Contoh pertanyaan:
- Bagaimana cara mendaftar?
- Berapa biaya pendaftaran?
- Apa saja syarat pendaftaran?

Silakan tanyakan apa saja! 😊"""
    
    def _get_help_message(self) -> str:
        """Get help message for /help command"""
        return """Bantuan Penggunaan Chatbot PSB

Cara Bertanya:
Kirim pesan teks dengan pertanyaan Anda tentang PSB. Bot akan memahami pertanyaan dan memberikan jawaban yang sesuai.

Topik yang Dapat Ditanyakan:
• Informasi dan prosedur pendaftaran
• Syarat dan persyaratan pendaftaran
• Biaya pendidikan (pendaftaran, SPP, dll)
• Program unggulan pesantren
• Informasi umum lainnya

Perintah Bot:
/start - Pesan selamat datang
/help - Bantuan ini
/status - Status sistem bot
/about - Tentang chatbot

Tips:
• Gunakan kalimat yang jelas
• Tanyakan satu topik per pesan
• Jika jawaban kurang jelas, coba tanyakan dengan cara berbeda

Jika Anda memerlukan bantuan lebih lanjut, silakan hubungi admin kami."""
    
    def _get_status_message(self) -> str:
        """Get system status message for /status command"""
        try:
            status = self.response_router.get_system_status()
            
            # Format status message
            message = "Status Sistem Chatbot PSB\n\n"
            
            # Router status
            message += f"🔄 Router: {status['router']['status'].upper()}\n"
            message += f"📁 Knowledge Base: {'✓' if status['router']['kb_exists'] else '✗'}\n\n"
            
            # Intent classifier status
            ic_status = status['intent_classifier']
            message += f"🤖 Intent Classifier:\n"
            message += f"  • Status: {'Mock Mode ⚠️' if ic_status['is_mock'] else 'Production ✓'}\n"
            message += f"  • Intents: {ic_status['num_intents']}\n\n"
            
            # Groq client status
            groq_status = status['groq_client']
            message += f"🧠 Groq API:\n"
            message += f"  • Status: {'Online ✓' if groq_status['api_available'] else 'Offline ✗'}\n"
            message += f"  • Model: {groq_status['model']}\n\n"
            
            message += "_Last checked: just now_"
            
            return message
        
        except Exception as e:
            return f"Error getting system status: {str(e)}"
    
    def _get_about_message(self) -> str:
        """Get about message for /about command"""
        return """Tentang Chatbot PSB

Nama: Chatbot Penerimaan Santri Baru
Versi: 1.0.0
Platform: Telegram

Arsitektur:
Chatbot ini menggunakan Double Guard Architecture:
• Guard 1: Intent Classification (TF-IDF + Logistic Regression)
• Guard 2: LLM Bounded Reasoning (Groq API)

Teknologi:
• Backend: FastAPI + Python
• NLP: scikit-learn
• LLM: Groq Inference API
• Knowledge Base: File-based JSON

Fitur Keamanan:
✓ Jawaban berbasis knowledge base resmi
✓ Tidak ada hallucination LLM
✓ Context-aware responses
✓ Confidence scoring

Pengembang:
Tim IT Pondok Pesantren

Catatan:
Sistem ini dirancang untuk memberikan informasi akurat dan terpercaya tentang PSB. Semua informasi berasal dari sumber resmi pesantren."""


# Export for use in app.py
__all__ = ['TelegramBotHandler']
