"""
Chatbot PSB - FastAPI Application Entry Point

This module serves as the main entry point for the PSB Chatbot system.
It handles:
- Telegram webhook endpoints
- Health check endpoints
- Database initialization
- Application lifecycle management

Architecture: Double Guard System (Intent Classifier + LLM Reasoning)
Platform: Telegram Bot
Framework: FastAPI

Usage:
    Development: python app.py
    Production:  uvicorn app:app --host 0.0.0.0 --port $PORT
"""

import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
from telegram_bot import TelegramBotHandler

# Load environment variables
load_dotenv()

# Configure logging based on environment
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot PSB - Penerimaan Santri Baru",
    description="Intent-based hybrid NLP chatbot with Double Guard Architecture",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "production") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "production") == "development" else None
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
bot_handler = None
db_initialized = False
startup_time = None


def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🕌 CHATBOT PSB - PENERIMAAN SANTRI BARU 🕌               ║
║                                                              ║
║     Architecture: Double Guard (Intent + LLM)                ║
║     Platform: Telegram Bot                                   ║
║     Framework: FastAPI                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Initializes database, bot handler, and validates environment.
    """
    global bot_handler, db_initialized, startup_time
    
    print_banner()
    
    startup_time = datetime.utcnow()
    logger.info("=" * 60)
    logger.info("Starting Chatbot PSB application...")
    logger.info("=" * 60)
    
    # Log environment info
    environment = os.getenv("ENVIRONMENT", "production")
    logger.info(f"Environment: {environment}")
    logger.info(f"Port: {os.getenv('PORT', 8000)}")
    
    # Validate required environment variables
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "GROQ_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        raise RuntimeError(f"Missing environment variables: {', '.join(missing_vars)}")
    
    logger.info("✅ Environment variables validated")
    
    # Initialize database
    try:
        from database import init_db, check_database_connection
        
        logger.info("🔄 Initializing database...")
        if check_database_connection():
            init_db()
            db_initialized = True
            logger.info("✅ Database initialized successfully")
        else:
            logger.warning("⚠️ Database connection failed - running without database")
            db_initialized = False
    except Exception as e:
        logger.warning(f"⚠️ Database initialization skipped: {str(e)}")
        db_initialized = False
    
    # Initialize bot handler
    try:
        bot_handler = TelegramBotHandler()
        logger.info("✅ Telegram bot handler initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot handler: {str(e)}")
        raise
    
    # Log webhook info
    webhook_url = os.getenv("WEBHOOK_URL", "Not configured")
    logger.info(f"📡 Webhook URL: {webhook_url}")
    
    logger.info("=" * 60)
    logger.info("🚀 Application startup complete!")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Performs cleanup operations.
    """
    logger.info("Shutting down Chatbot PSB application...")
    # Cleanup operations if needed
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """
    Root endpoint - basic health check and system information.
    
    Returns:
        JSONResponse: System information and status
    """
    return JSONResponse(
        content={
            "status": "online",
            "service": "Chatbot PSB - Penerimaan Santri Baru",
            "architecture": "Double Guard (Intent Classifier + LLM Reasoning)",
            "platform": "Telegram",
            "version": "1.0.0"
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment platforms.
    
    Returns:
        JSONResponse: Health status of the application
    """
    try:
        # Calculate uptime
        uptime_seconds = None
        if startup_time:
            uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
        
        # Check database connection
        db_status = "not_configured"
        if db_initialized:
            try:
                from database import check_database_connection
                db_status = "connected" if check_database_connection() else "disconnected"
            except Exception:
                db_status = "error"
        
        # Build health status
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime_seconds,
            "components": {
                "bot_handler": "ready" if bot_handler is not None else "not_initialized",
                "database": db_status,
                "intent_classifier": "loaded",  # Loaded by TelegramBotHandler
            },
            "environment": {
                "mode": os.getenv("ENVIRONMENT", "production"),
                "telegram_token_set": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
                "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
                "webhook_configured": bool(os.getenv("WEBHOOK_URL"))
            }
        }
        
        # Determine overall status
        if bot_handler is None:
            health_status["status"] = "degraded"
        
        return JSONResponse(content=health_status)
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram webhook endpoint.
    
    This endpoint receives updates from Telegram Bot API and processes them
    through the Double Guard architecture:
    1. Message is extracted from webhook payload
    2. Forwarded to telegram_bot handler
    3. Intent classification is performed
    4. Knowledge base is queried
    5. LLM reasoning is applied
    6. Response is sent back to user
    
    Args:
        request (Request): FastAPI request object containing Telegram update
        
    Returns:
        JSONResponse: Success confirmation
        
    Raises:
        HTTPException: If webhook processing fails
    """
    if bot_handler is None:
        logger.error("Bot handler not initialized")
        raise HTTPException(status_code=503, detail="Bot handler not initialized")
    
    try:
        # Get the webhook payload
        update_data = await request.json()
        logger.info(f"Received webhook update: {update_data.get('update_id', 'unknown')}")
        
        # Process the update through bot handler
        await bot_handler.process_update(update_data)
        
        return JSONResponse(content={"status": "ok"})
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")


@app.get("/webhook/info")
async def webhook_info():
    """
    Get webhook configuration information.
    Useful for debugging webhook setup.
    
    Returns:
        JSONResponse: Webhook configuration details
    """
    webhook_url = os.getenv("WEBHOOK_URL", "Not configured")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Mask the token for security
    masked_token = f"{bot_token[:10]}...{bot_token[-5:]}" if len(bot_token) > 15 else "***"
    
    return JSONResponse(
        content={
            "webhook_endpoint": "/webhook",
            "webhook_url": webhook_url,
            "method": "POST",
            "bot_token_preview": masked_token,
            "setup_command": f"curl 'https://api.telegram.org/bot<TOKEN>/setWebhook?url={webhook_url}'",
            "note": "This endpoint receives Telegram updates via webhook"
        }
    )


# ===========================================
# DEBUG ENDPOINTS (Development Only)
# ===========================================

@app.get("/debug/test-intent")
async def test_intent(message: str = "Berapa biaya pendaftaran?"):
    """
    Test intent classification without sending to Telegram.
    Only available in development mode.
    
    Args:
        message: Test message to classify
        
    Returns:
        JSONResponse: Classification result
    """
    if os.getenv("ENVIRONMENT", "production") != "development":
        raise HTTPException(status_code=403, detail="Debug endpoints only available in development mode")
    
    if bot_handler is None:
        raise HTTPException(status_code=503, detail="Bot handler not initialized")
    
    try:
        # Get the response router from bot handler
        result = bot_handler.response_router.process_message(message)
        
        return JSONResponse(content={
            "input_message": message,
            "intent": result.get("intent", "unknown"),
            "confidence": result.get("confidence", 0),
            "confidence_level": result.get("confidence_level", "unknown"),
            "routed_to": result.get("routed_to", "unknown"),
            "response_preview": result.get("response", "")[:200] + "..." if len(result.get("response", "")) > 200 else result.get("response", "")
        })
    except Exception as e:
        logger.error(f"Test intent error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.get("/debug/db-stats")
async def db_stats():
    """
    Get database statistics.
    Only available in development mode.
    
    Returns:
        JSONResponse: Database statistics
    """
    if os.getenv("ENVIRONMENT", "production") != "development":
        raise HTTPException(status_code=403, detail="Debug endpoints only available in development mode")
    
    if not db_initialized:
        return JSONResponse(content={"status": "database_not_initialized"})
    
    try:
        from database import get_user_question_stats, check_database_connection
        
        stats = get_user_question_stats()
        stats["database_connected"] = check_database_connection()
        
        return JSONResponse(content=stats)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.post("/debug/simulate-message")
async def simulate_message(request: Request):
    """
    Simulate a Telegram message for testing.
    Only available in development mode.
    
    Body: {"message": "Your test message"}
    
    Returns:
        JSONResponse: Processing result
    """
    if os.getenv("ENVIRONMENT", "production") != "development":
        raise HTTPException(status_code=403, detail="Debug endpoints only available in development mode")
    
    if bot_handler is None:
        raise HTTPException(status_code=503, detail="Bot handler not initialized")
    
    try:
        body = await request.json()
        message_text = body.get("message", "Test message")
        
        # Create a fake Telegram update
        fake_update = {
            "update_id": 999999999,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 12345,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "test_user"
                },
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "test_user",
                    "type": "private"
                },
                "date": int(datetime.utcnow().timestamp()),
                "text": message_text
            }
        }
        
        # Process without actually sending to Telegram
        result = bot_handler.response_router.process_message(message_text)
        
        return JSONResponse(content={
            "simulated": True,
            "input_message": message_text,
            "result": result,
            "note": "Message processed but NOT sent to Telegram"
        })
    except Exception as e:
        logger.error(f"Simulate message error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


# ===========================================
# ERROR HANDLERS
# ===========================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url.path)}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Run the application
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT", "production") == "development"
    )
