# ⚡ Chatbot PSB - Quick Start Guide

Get the chatbot running in 5 minutes on your machine.

---

## Prerequisites

- **Python 3.10+** (Recommended: 3.11)
- **PostgreSQL 13+** (or use local SQLite for development)
- **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
- **Groq API Key** (from [console.groq.com](https://console.groq.com))
- **Git** (for cloning)

---

## 1. Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd chatbot-psb

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

---

## 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# OR for development (includes testing tools)
pip install -r requirements-dev.txt
```

**What gets installed**:
- FastAPI & Uvicorn (web server)
- scikit-learn (intent classification)
- requests (API calls)
- SQLAlchemy & psycopg2 (database)
- python-dotenv (environment config)
- Plus all required dependencies

---

## 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

**Required settings in .env**:
```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
GROQ_API_KEY=your_api_key_from_console_groq_com
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_psb
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**Getting credentials**:

**Telegram Bot Token**:
1. Open Telegram, search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow instructions to create bot
4. Copy the token provided

**Groq API Key**:
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or login
3. Create new API key
4. Copy the key

**Database URL** (for development, you can use local PostgreSQL):
```
postgresql://username:password@localhost:5432/chatbot_psb
```

Or use **Railway** for instant PostgreSQL (recommended for production).

---

## 4. Initialize Database

```bash
# Create database and tables
python init_database.py
```

**Output**:
```
✓ Database initialized successfully
✓ Tables created:
  - user_questions
```

---

## 5. Run the Chatbot

### Development Mode (with auto-reload)

```bash
python app.py
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Press CTRL+C to quit
INFO:     Started server process [12345]
```

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 6. Connect Telegram Webhook

The bot can run in two modes:

### Mode A: Polling (Easier for Development)

Telegram servers push updates to your bot:

```bash
# Use polling mode (see app_polling.py)
python app_polling.py
```

This mode doesn't require a public URL. Perfect for development!

### Mode B: Webhook (Better for Production)

You need a public URL:

```bash
# Set webhook on Telegram
curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook \
  -d url="https://your-public-url/webhook"

# Verify webhook is set
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

For local development, use **ngrok** to create a public URL:

```bash
# In another terminal
ngrok http 8000

# This gives you a public URL like:
# https://abc123.ngrok.io

# Set it as your webhook:
curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook \
  -d url="https://abc123.ngrok.io/webhook"
```

---

## 7. Test the Bot

### Via Telegram

1. Find your bot in Telegram (or search by username)
2. Send a message:
   ```
   Berapa biaya pendaftaran?
   ```
3. Wait for response (should come in 2-3 seconds)

### Via curl (webhook testing)

```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123,
    "message": {
      "message_id": 1,
      "chat": {"id": 987654321},
      "from": {
        "id": 123456789,
        "username": "testuser"
      },
      "text": "Berapa biaya pendaftaran?"
    }
  }'

# Expected: 200 OK
```

### Via Python

```python
import requests

url = "http://localhost:8000/webhook"
data = {
    "update_id": 123,
    "message": {
        "message_id": 1,
        "chat": {"id": 987654321},
        "from": {
            "id": 123456789,
            "username": "testuser"
        },
        "text": "Berapa biaya pendaftaran?"
    }
}

response = requests.post(url, json=data)
print(response.status_code)  # Should be 200
```

---

## 8. Verify Components

### Check Intent Classifier

```bash
python -c "
from intent_classifier import get_intent_classifier

classifier = get_intent_classifier()
result = classifier.predict('Berapa biaya pendaftaran?')
print(f'Intent: {result.intent}')
print(f'Confidence: {result.confidence}')
"
```

Expected output:
```
Intent: biaya_pendidikan
Confidence: 0.94
```

### Check Groq API

```bash
python -c "
from groq_client import get_groq_client

client = get_groq_client()
response = client.generate_response(
    question='Halo',
    intent='faq_umum',
    confidence=0.9,
    knowledge_base_data={'intent': 'faq_umum', 'items': []}
)
print(f'Success: {response.success}')
print(f'Message: {response.message}')
"
```

### Check Database

```bash
python -c "
from database import get_db_session, UserQuestion

session = get_db_session()
count = session.query(UserQuestion).count()
print(f'Total questions logged: {count}')
session.close()
"
```

### Check All Health

```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-01T12:00:00Z"
# }
```

---

## Common Issues & Solutions

### Issue: `TELEGRAM_BOT_TOKEN not set`

**Solution**: Make sure .env file exists and has correct token:
```bash
cat .env | grep TELEGRAM_BOT_TOKEN
```

### Issue: `GROQ_API_KEY not set`

**Solution**: Check .env file:
```bash
cat .env | grep GROQ_API_KEY
```

### Issue: `DATABASE_URL connection failed`

**Solution 1**: Make sure PostgreSQL is running:
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT 1"
```

**Solution 2**: Use Railway PostgreSQL:
```bash
# Sign up at railway.app
# Link PostgreSQL addon
# Copy DATABASE_URL to .env
```

### Issue: `ModuleNotFoundError: No module named 'intent_classifier'`

**Solution**: Activate virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

### Issue: Models not found (`.pkl` files)

**Solution**: Models come with repository. If missing:
```bash
# Models should be in models/ directory
ls -la models/

# If empty, you need to train:
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb
```

### Issue: No response from bot

**Check logs**:
```bash
# Look for errors in terminal output
# Also check database logging:

python -c "
from database import get_db_session, UserQuestion

session = get_db_session()
latest = session.query(UserQuestion).order_by(UserQuestion.timestamp.desc()).first()
print(f'Latest question: {latest.question}')
print(f'Intent: {latest.intent}')
print(f'Response: {latest.response}')
session.close()
"
```

---

## Next Steps

### ✅ You're Done! Now:

1. **Read Full Documentation**:
   - [Architecture](ARCHITECTURE.md) - Deep dive into system design
   - [Components](COMPONENTS.md) - Detailed API reference
   - [API Reference](API_REFERENCE.md) - REST endpoints

2. **Customize Knowledge Base**:
   - Edit files in `knowledge_base/` directory
   - Update intent training data in `data/intents_v2.csv`
   - Retrain models using notebook

3. **Deploy to Production**:
   - See [Deployment Guide](DEPLOYMENT_GUIDE.md)
   - Deploy to Railway.app or your preferred platform

4. **Develop & Extend**:
   - See [Development Guide](DEVELOPMENT_GUIDE.md)
   - Add new features, improve responses
   - Run tests with `pytest`

---

## Development Commands

```bash
# Run tests
pytest tests/ -v

# Format code
black .

# Lint code
flake8 .

# Export training data
python export_training_data.py

# Admin labeling interface
python admin_labeling.py

# Check database schema
psql $DATABASE_URL -c "\dt"

# View logs for user
python -c "
from database import get_db_session, UserQuestion
session = get_db_session()
user_q = session.query(UserQuestion).filter_by(user_id='YOUR_ID').all()
for q in user_q:
    print(f'{q.timestamp}: {q.question} -> {q.intent}')
session.close()
"
```

---

## Architecture Overview

```
User (Telegram)
    ↓
Telegram Bot API
    ↓
FastAPI Server (app.py:8000)
    ↓
Response Router (orchestrator)
    ├─ Intent Classifier (Guard 1)
    ├─ Knowledge Base
    └─ Groq API (Guard 2)
    ↓
Database (PostgreSQL)
    ↓
Response back to User
```

---

## Important Files

| File | Purpose |
|------|---------|
| `app.py` | FastAPI server entry point |
| `telegram_bot.py` | Telegram integration |
| `response_router.py` | Core logic orchestration |
| `intent_classifier.py` | Intent prediction (Guard 1) |
| `groq_client.py` | LLM reasoning (Guard 2) |
| `database.py` | Data persistence |
| `.env` | Environment configuration (create from .env.example) |
| `knowledge_base/` | FAQ/info JSON files |
| `models/` | Trained ML models (.pkl files) |

---

## Useful Links

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Groq Console**: https://console.groq.com
- **FastAPI Docs**: http://localhost:8000/docs (when running)
- **Railway Deployment**: https://railway.app
- **PostgreSQL**: https://www.postgresql.org

---

## Getting Help

- Check logs in terminal output
- Review [Troubleshooting](TROUBLESHOOTING.md) guide
- Check existing GitHub issues
- Create new issue with:
  - Error message
  - Steps to reproduce
  - Python version
  - OS

---

**Enjoy building with Chatbot PSB! 🚀**
