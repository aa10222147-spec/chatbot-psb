# 🆘 Chatbot PSB - Troubleshooting Guide

Solutions to common issues and problems.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Issues](#runtime-issues)
3. [API & Integration Issues](#api--integration-issues)
4. [Database Issues](#database-issues)
5. [Performance Issues](#performance-issues)
6. [Testing Issues](#testing-issues)
7. [Deployment Issues](#deployment-issues)
8. [FAQ](#faq)

---

## Installation Issues

### Issue: `ModuleNotFoundError: No module named 'intent_classifier'`

**Cause**: Virtual environment not activated or Python path not set correctly

**Solutions**:

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 2. Verify you're in the right directory
pwd
# Should show: .../chatbot-psb

# 3. Verify Python interpreter
which python
# Should show: .../chatbot-psb/venv/bin/python
```

---

### Issue: `pip install` fails with permission error

**Cause**: Virtual environment not properly created or activated

**Solutions**:

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Issue: Model files (.pkl) not found

**Cause**: Models not included in repository or corrupted

**Solutions**:

```bash
# Check if models directory exists and has files
ls -la models/
# Should show: vectorizer.pkl, model.pkl, label_encoder.pkl

# If empty, retrain models
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb
# Run all cells and save

# If training notebook fails, check training data
ls -la data/intents_v2.csv
# Should have questions and intents
```

---

### Issue: Database driver not found (`psycopg2`)

**Cause**: PostgreSQL driver not installed

**Solutions**:

```bash
# Install with system packages (if using local PostgreSQL)
# Linux
sudo apt-get install postgresql-client

# Mac
brew install postgresql

# Then reinstall Python package
pip install psycopg2-binary

# Or use minimal requirements
pip install -r requirements-minimal.txt
```

---

## Runtime Issues

### Issue: `TELEGRAM_BOT_TOKEN not found`

**Cause**: Environment variable not set or .env file missing

**Solutions**:

```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit .env and add token
nano .env
# Add: TELEGRAM_BOT_TOKEN=your_token_here

# 3. Verify variable is set
echo $TELEGRAM_BOT_TOKEN
# Should print your token

# 4. Or set directly in shell (temporary)
export TELEGRAM_BOT_TOKEN=your_token
python app.py
```

---

### Issue: `GROQ_API_KEY not found`

**Cause**: Same as TELEGRAM_BOT_TOKEN issue above

**Solutions**:

```bash
# Add to .env file
GROQ_API_KEY=your_groq_api_key

# Get from console.groq.com
# 1. Log in to console.groq.com
# 2. Click "API Keys"
# 3. Create new key
# 4. Copy and paste into .env
```

---

### Issue: `RuntimeError: Models not loaded`

**Cause**: Intent classifier failed to load pre-trained models

**Solutions**:

```python
# Debug: Check model files
from pathlib import Path
models_dir = Path("models")
for file in models_dir.glob("*.pkl"):
    print(f"Found: {file}")

# Try loading manually
import joblib
try:
    vectorizer = joblib.load("models/vectorizer.pkl")
    print("✓ Vectorizer loaded")
except Exception as e:
    print(f"✗ Error: {e}")
```

---

### Issue: `FileNotFoundError: .env file`

**Cause**: .env file doesn't exist

**Solutions**:

```bash
# Create from example
cp .env.example .env

# Verify it exists
ls -la .env

# Check it has required variables
cat .env | grep -E "TELEGRAM|GROQ|DATABASE"
```

---

## API & Integration Issues

### Issue: Telegram webhook not receiving updates

**Cause**: Webhook URL not set or incorrect

**Solutions**:

```bash
# 1. Check current webhook status
TELEGRAM_TOKEN=your_token_here
curl https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo

# Expected response:
# "url": "https://your-domain/webhook",
# "pending_update_count": 0

# 2. If pending_update_count > 0, delete webhook
curl -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/deleteWebhook

# 3. Re-set webhook
curl -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook \
  -d url="https://your-domain/webhook"

# 4. For local development, use polling instead
python app_polling.py
```

---

### Issue: Groq API timeout (5+ seconds)

**Cause**: API is slow, rate limited, or network issue

**Solutions**:

```python
# 1. Check Groq API status
import requests
try:
    response = requests.get("https://api.groq.com/openai/v1/models", timeout=5)
    print(f"Status: {response.status_code}")
except requests.exceptions.Timeout:
    print("Groq API is slow")

# 2. Check rate limits
# Go to console.groq.com and check usage

# 3. Increase timeout in groq_client.py
self.timeout = 10  # Instead of 5

# 4. Check internet connection
curl https://api.groq.com/openai/v1/models

# 5. Wait a few minutes and retry (may be rate limited)
```

---

### Issue: `requests.exceptions.ConnectionError: Connection refused`

**Cause**: External API not reachable (Telegram, Groq)

**Solutions**:

```bash
# 1. Check internet connection
ping google.com

# 2. Check if API is reachable
curl https://api.telegram.org
curl https://api.groq.com

# 3. Check firewall/proxy
# If behind proxy, set environment:
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 4. Check API keys are valid
# Telegram: https://t.me/BotFather -> getme
# Groq: console.groq.com -> test API
```

---

### Issue: Bot doesn't respond to messages

**Cause**: Multiple possible causes

**Debug steps**:

```bash
# 1. Check if FastAPI server is running
curl http://localhost:8000/health
# Should return 200 OK

# 2. Check if bot is receiving messages (webhook mode)
curl https://api.telegram.org/bot${TOKEN}/getWebhookInfo
# pending_update_count should be 0

# 3. Check logs for errors
# Look at terminal output for error messages
# Enable DEBUG logging: LOG_LEVEL=DEBUG

# 4. Test webhook endpoint manually
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1,
    "message": {
      "message_id": 1,
      "date": 1672531200,
      "chat": {"id": 123456789},
      "from": {"id": 987654321},
      "text": "test"
    }
  }'

# 5. Check database logging
python -c "
from database import get_db_session, UserQuestion
session = get_db_session()
latest = session.query(UserQuestion).order_by(UserQuestion.timestamp.desc()).first()
if latest:
    print(f'Latest: {latest.question} -> {latest.intent}')
else:
    print('No questions logged yet')
"
```

---

## Database Issues

### Issue: `psycopg2.OperationalError: could not connect to server`

**Cause**: PostgreSQL not running or wrong connection string

**Solutions**:

```bash
# 1. Check if PostgreSQL is running
# Linux
sudo systemctl status postgresql

# Mac
brew services list | grep postgres

# 2. Start PostgreSQL
# Linux
sudo systemctl start postgresql

# Mac
brew services start postgresql

# 3. Check connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_psb
# Format: postgresql://username:password@host:port/database

# 4. Test connection
python -c "
from database import engine
try:
    with engine.connect() as conn:
        print('✓ Database connected')
except Exception as e:
    print(f'✗ Error: {e}')
"

# 5. For development, use SQLite instead
# Simpler, no server needed
DATABASE_URL=sqlite:///./chatbot_psb.db
```

---

### Issue: `Table 'user_questions' doesn't exist`

**Cause**: Database not initialized

**Solutions**:

```bash
# Initialize database and create tables
python init_database.py

# Verify tables were created
python -c "
from database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
# Should show: ['user_questions']
"
```

---

### Issue: Database connection pooling errors

**Cause**: Too many connections or connection leaked

**Solutions**:

```python
# Always close database sessions
from database import SessionLocal

# ✓ CORRECT: Use context manager
with SessionLocal() as session:
    # Do work
    pass

# ✓ ALSO CORRECT: Close manually
session = SessionLocal()
try:
    # Do work
finally:
    session.close()

# ✗ WRONG: Don't close
session = SessionLocal()
# Work not closed, connection leaked!
```

---

### Issue: Slow database queries

**Cause**: Missing indexes or inefficient queries

**Solutions**:

```bash
# 1. Add indexes
python -c "
from database import engine
with engine.begin() as conn:
    conn.exec_driver_sql(
        'CREATE INDEX idx_user_id ON user_questions(user_id)'
    )
    conn.exec_driver_sql(
        'CREATE INDEX idx_timestamp ON user_questions(timestamp)'
    )
    print('✓ Indexes created')
"

# 2. Analyze query performance
python -c "
from database import SessionLocal, UserQuestion
session = SessionLocal()
# Enable EXPLAIN for query analysis
stmt = session.query(UserQuestion).filter_by(intent='biaya_pendidikan')
print(stmt)  # Shows generated SQL
session.close()
"

# 3. Limit query results
# Instead of: session.query(UserQuestion).all()  # All rows!
# Use: session.query(UserQuestion).limit(100).all()  # Limited
```

---

## Performance Issues

### Issue: Response takes too long (>5 seconds)

**Cause**: One of several bottlenecks

**Solutions**:

```python
# Profile each component
import time

# Intent Classification
start = time.time()
result = classifier.predict("Question")
ic_time = time.time() - start
print(f"Intent Classification: {ic_time:.3f}s")

# Knowledge Base Loading
start = time.time()
kb = router._load_knowledge_base(result.intent)
kb_time = time.time() - start
print(f"KB Loading: {kb_time:.3f}s")

# Groq API Call (usually slowest)
start = time.time()
response = groq_client.generate_response(...)
groq_time = time.time() - start
print(f"Groq API: {groq_time:.3f}s")

# Database Logging
start = time.time()
question_id = log_user_question(...)
db_time = time.time() - start
print(f"Database: {db_time:.3f}s")

# If Groq is slow:
# 1. Reduce max_tokens in .env (e.g., 300 instead of 500)
# 2. Increase temperature slightly for faster generation
# 3. Check Groq API status
# 4. Upgrade Groq plan if rate limited
```

---

### Issue: Memory usage growing over time

**Cause**: Memory leak or large cache

**Solutions**:

```python
# Check memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")

# Monitor over time
import tracemalloc
tracemalloc.start()

# Do work

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")

# Common causes:
# 1. Database sessions not closed
# 2. Cache growing unbounded
# 3. Large objects in memory
```

---

### Issue: High CPU usage

**Cause**: Inefficient processing or tight loop

**Solutions**:

```python
# Profile CPU usage
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Do work
result = router.process_question("Question")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions by time

# Optimize bottleneck functions
# Usually:
# 1. TF-IDF vectorization (use sparse matrices)
# 2. Groq API (increase timeout, reduce requests)
# 3. Database queries (add indexes, limit results)
```

---

## Testing Issues

### Issue: Tests fail with `ModuleNotFoundError`

**Cause**: Python path not set correctly for tests

**Solutions**:

```bash
# Run tests from project root
cd /path/to/chatbot-psb

# Use pytest directly
pytest tests/ -v

# Or with explicit path
python -m pytest tests/ -v

# Ensure virtual environment is activated
source venv/bin/activate
which pytest
# Should show: .../venv/bin/pytest
```

---

### Issue: Database tests fail (table doesn't exist)

**Cause**: Test database not initialized

**Solutions**:

```python
# In conftest.py, ensure test DB is set up
import pytest
from database import Base, engine

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

---

### Issue: Groq API tests timeout

**Cause**: Tests hitting real API (slow)

**Solutions**:

```python
# Mock the Groq API in tests
from unittest.mock import patch, MagicMock

@patch('groq_client.requests.post')
def test_groq_response(mock_post):
    """Test Groq response handling"""
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {"content": "Mocked response"}
        }]
    }
    
    client = GroqClient()
    result = client.generate_response(...)
    assert result.success is True
    
    # Verify API wasn't actually called
    mock_post.assert_called_once()
```

---

## Deployment Issues

### Issue: Railway deployment fails

**Cause**: Missing files or invalid configuration

**Solutions**:

```bash
# 1. Check Procfile exists
cat Procfile
# Should contain: web: uvicorn app:app --host 0.0.0.0 --port $PORT

# 2. Check runtime.txt
cat runtime.txt
# Should contain: python-3.11.0

# 3. Check requirements.txt has all dependencies
pip freeze > requirements.txt
git add requirements.txt

# 4. Verify git is up to date
git status
git add .
git commit -m "Fix deployment"
git push origin main

# 5. Check Railway logs
railway logs
# Look for error messages
```

---

### Issue: Database connection fails in production

**Cause**: DATABASE_URL not set in Railway

**Solutions**:

```bash
# 1. Check environment variables in Railway
# Railway Dashboard → Project → Settings → Environment

# DATABASE_URL should be automatically set by Railway
# If not:
# - Add PostgreSQL addon
# - It will create DATABASE_URL automatically

# 2. Verify DATABASE_URL format
# Should be: postgresql://user:pass@host:port/db

# 3. Check Railway PostgreSQL status
# Dashboard → postgres service → Logs

# 4. Test connection locally
export DATABASE_URL=... # Copy from Railway
python -c "
from database import engine
with engine.connect() as conn:
    print('✓ Connected')
"
```

---

## FAQ

### Q: How often should I retrain the intent classifier?

**A**: Retrain when:
- You add new intents
- Accuracy drops below 90%
- User feedback shows consistent misclassifications
- Monthly as standard practice

### Q: What if Groq API is down?

**A**: The system falls back to knowledge base responses without LLM refinement. Responses will be less natural but still accurate.

### Q: Can I run the bot without PostgreSQL?

**A**: Yes, use SQLite for development:
```
DATABASE_URL=sqlite:///./chatbot_psb.db
```

SQLite works great for development and testing. Use PostgreSQL for production (Railway provides it free).

### Q: How do I backup the database?

**A**: 
```bash
# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Railway automatic backups
# Dashboard → postgres → Backups

# Restore from backup
psql $DATABASE_URL < backup_20260101.sql
```

### Q: How do I see what questions users are asking?

**A**:
```python
from database import get_db_session, UserQuestion
from datetime import datetime, timedelta

session = get_db_session()

# Today's questions
today = datetime.now().date()
today_q = session.query(UserQuestion)\
    .filter(UserQuestion.timestamp >= today)\
    .all()

for q in today_q:
    print(f"{q.timestamp}: {q.question}")
    print(f"  → Intent: {q.intent} (conf: {q.confidence:.1%})")
    print()

session.close()
```

### Q: How do I update the knowledge base?

**A**:
```bash
# 1. Edit JSON files in knowledge_base/
nano knowledge_base/biaya_pendidikan.json

# 2. Restart bot for changes to take effect
# Or reload configuration without restart

# 3. Test changes
python -c "
from response_router import get_response_router
router = get_response_router()
result = router.process_question('Berapa biaya?')
print(result.message)
"
```

### Q: How do I add new intents?

**A**:
```bash
# 1. Create new JSON file
cat > knowledge_base/new_intent.json << 'EOF'
{
  "intent": "new_intent",
  "description": "Description",
  "items": []
}
EOF

# 2. Add training examples
echo "Sample question here,new_intent" >> data/intents_v2.csv

# 3. Retrain classifier
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb

# 4. Test
python -c "
from intent_classifier import get_intent_classifier
c = get_intent_classifier()
print(c.get_all_intents())  # Should include 'new_intent'
"
```

---

## Getting Help

1. **Check logs**: Look for error messages and stack traces
2. **Enable DEBUG logging**: Set LOG_LEVEL=DEBUG
3. **Review documentation**: See docs/ folder
4. **Check GitHub issues**: Common problems already solved
5. **Create detailed issue**: Include:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version)
   - System logs

---

**Still stuck? Create an issue or contact support!**

