"""
Chatbot PSB - Polling Mode (Development)

This is an alternative entry point for local development using Polling instead of Webhooks.
Use this when running on localhost where Telegram cannot reach your webhook.

Usage:
    python app_polling.py
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram_bot import TelegramBotHandler
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramPollingBot:
    """
    Telegram Bot with Polling support for local development.
    This fetches updates from Telegram API instead of receiving webhooks.
    """
    
    def __init__(self):
        """Initialize the polling bot"""
        self.bot_handler = TelegramBotHandler()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.running = False
        
        logger.info("Polling Bot initialized")
    
    async def get_updates(self, timeout: int = 30) -> list:
        """
        Get updates from Telegram using long polling.
        
        Args:
            timeout: Long polling timeout in seconds
            
        Returns:
            list: List of updates
        """
        url = f"{self.api_base_url}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": timeout,
            "allowed_updates": ["message"]
        }
        
        try:
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok"):
                return data.get("result", [])
            else:
                logger.error(f"Telegram API error: {data}")
                return []
        
        except requests.exceptions.Timeout:
            # Timeout is normal for long polling
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {str(e)}")
            return []
    
    async def process_updates(self, updates: list):
        """
        Process a batch of updates.
        
        Args:
            updates: List of Telegram updates
        """
        for update in updates:
            try:
                update_id = update.get("update_id")
                
                # Update last_update_id to avoid processing the same update twice
                if update_id > self.last_update_id:
                    self.last_update_id = update_id
                
                # Log the update
                logger.info(f"Processing update {update_id}")
                
                # Process through bot handler
                await self.bot_handler.process_update(update)
            
            except Exception as e:
                logger.error(f"Error processing update: {str(e)}", exc_info=True)
    
    async def start_polling(self):
        """Start the polling loop"""
        self.running = True
        logger.info("Starting polling... (Press Ctrl+C to stop)")
        logger.info("Bot is now listening for messages!")
        
        try:
            while self.running:
                # Get updates
                updates = await self.get_updates(timeout=30)
                
                # Process updates
                if updates:
                    await self.process_updates(updates)
                
                # Small delay to prevent hammering the API
                await asyncio.sleep(0.1)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping...")
        finally:
            self.running = False
            logger.info("Polling stopped")
    
    def stop(self):
        """Stop the polling loop"""
        self.running = False


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Chatbot PSB - Polling Mode (Development)")
    logger.info("=" * 60)
    
    # Check environment variables
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("TELEGRAM_BOT_TOKEN not set in .env file")
        return
    
    if not os.getenv("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY not set in .env file")
        return
    
    # Create and start polling bot
    try:
        bot = TelegramPollingBot()
        await bot.start_polling()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
