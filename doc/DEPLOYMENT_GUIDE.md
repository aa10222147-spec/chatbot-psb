# 🚀 Chatbot PSB - Production Deployment Guide

Complete guide to deploying the chatbot to production using Railway.app or other platforms.

---

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Railway Deployment](#railway-deployment) (Recommended)
3. [Docker Deployment](#docker-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Scaling](#scaling)

---

## Deployment Options

### Quick Comparison

| Platform | Cost | Setup Time | Ease | Recommendation |
|----------|------|-----------|------|-----------------|
| **Railway** | Free tier available | 5 min | ⭐⭐⭐⭐⭐ | **BEST** - Recommended |
| **Heroku** | Paid only ($7+/mo) | 5 min | ⭐⭐⭐⭐⭐ | Good - Similar to Railway |
| **DigitalOcean** | $5+/mo droplet | 15 min | ⭐⭐⭐⭐ | Good - More control |
| **AWS** | Variable | 20+ min | ⭐⭐⭐ | Advanced - Overkill |
| **VPS** | $5+/mo | 30+ min | ⭐⭐ | Advanced - Full control |

---

## Railway Deployment

### Recommended: Easiest Setup

Railway.app is the easiest way to deploy. It handles PostgreSQL, environment variables, and deployments automatically.

### Step 1: Prepare Repository

```bash
# Ensure you're in the chatbot-psb directory
cd chatbot-psb

# Check required files exist
ls -la Procfile           # Should exist
ls -la runtime.txt        # Should exist
ls -la requirements.txt   # Should exist

# Verify git is initialized
git status

# If not initialized:
git init
git add .
git commit -m "Initial commit"
```

### Step 2: Create Railway Account

1. Go to [Railway.app](https://railway.app)
2. Click "Sign up with GitHub"
3. Authorize Railway to access your GitHub
4. Create new project

### Step 3: Connect GitHub Repository

```bash
# Option A: Via Railway Dashboard
# 1. Create New Project in Railway
# 2. Click "Deploy from GitHub"
# 3. Select your repository
# 4. Confirm

# Option B: Via CLI
railway init
railway link
```

### Step 4: Add PostgreSQL

In Railway Dashboard:

```
1. New → Database
2. Select PostgreSQL
3. PostgreSQL will be automatically linked
4. Railway creates DATABASE_URL automatically
```

### Step 5: Configure Environment Variables

In Railway Dashboard → Environment:

```
TELEGRAM_BOT_TOKEN=your_telegram_token_here
GROQ_API_KEY=your_groq_api_key_here
LOG_LEVEL=INFO
ENVIRONMENT=production
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3
```

**Note**: `DATABASE_URL` is set automatically by Railway when PostgreSQL is linked.

### Step 6: Deploy

```bash
# Option A: Automatic (push to GitHub)
git add .
git commit -m "Deploy to production"
git push origin main

# Railway auto-deploys on push

# Option B: Manual via CLI
railway up
```

### Step 7: Get Public URL

In Railway Dashboard:

```
1. Click on "python" service
2. Look for "Deployment" section
3. Copy the URL (e.g., https://chatbot-psb.railway.app)
```

### Step 8: Configure Telegram Webhook

```bash
TELEGRAM_TOKEN=your_bot_token
RAILWAY_URL=https://chatbot-psb.railway.app

# Set webhook
curl -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook \
  -d url="${RAILWAY_URL}/webhook"

# Verify
curl https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo
```

### Step 9: Test

Send a message to your bot on Telegram. You should get a response in 2-3 seconds.

---

## Docker Deployment

### Option: Self-Hosted with Docker

If you prefer to host on your own server.

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: chatbot_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: chatbot_psb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  chatbot:
    build: .
    environment:
      DATABASE_URL: postgresql://chatbot_user:secure_password@postgres:5432/chatbot_psb
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      GROQ_API_KEY: ${GROQ_API_KEY}
      LOG_LEVEL: INFO
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: always

volumes:
  postgres_data:
```

### Step 3: Build and Run

```bash
# Build image
docker build -t chatbot-psb .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Stop
docker-compose down
```

---

## Environment Configuration

### Production Environment Variables

```bash
# =======================
# REQUIRED - Credentials
# =======================
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
GROQ_API_KEY=your_api_key_from_console_groq_com
DATABASE_URL=postgresql://user:pass@host:port/db

# =======================
# Application Settings
# =======================
ENVIRONMENT=production                  # production or development
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR

# =======================
# Groq API Configuration
# =======================
GROQ_MODEL=llama-3.3-70b-versatile     # LLM model to use
GROQ_MAX_TOKENS=500                     # Max response tokens
GROQ_TEMPERATURE=0.3                    # Lower = more consistent

# =======================
# Optional - Advanced
# =======================
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook
KB_DIR=knowledge_base                   # Knowledge base directory
MODELS_DIR=models                       # Models directory
CLASSIFIER_CONFIDENCE_THRESHOLD=0.7     # Intent confidence threshold
```

### Environment Variable Validation

```bash
# Check all required variables are set
python -c "
import os
required = [
    'TELEGRAM_BOT_TOKEN',
    'GROQ_API_KEY',
    'DATABASE_URL'
]
for var in required:
    if not os.getenv(var):
        print(f'ERROR: {var} not set')
    else:
        print(f'✓ {var} is set')
"
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check if service is running
curl https://chatbot-psb.railway.app/health

# Check if service is ready
curl https://chatbot-psb.railway.app/ready

# Both should return 200 OK with status=healthy
```

### View Logs

```bash
# Option A: Railway Dashboard
# 1. Go to Railway project
# 2. Click "python" service
# 3. View logs in real-time

# Option B: Railway CLI
railway logs

# Option C: Docker logs
docker-compose logs -f chatbot
```

### Monitor Questions & Analytics

```python
# Run analytics script
from database import get_db_session, UserQuestion
from sqlalchemy import func
from datetime import datetime, timedelta

session = get_db_session()

# Questions in last 24 hours
day_ago = datetime.now() - timedelta(days=1)
recent = session.query(UserQuestion)\
    .filter(UserQuestion.timestamp >= day_ago)\
    .count()
print(f"Questions (24h): {recent}")

# Intent distribution
intents = session.query(
    UserQuestion.intent,
    func.count(UserQuestion.id).label('count')
).group_by(UserQuestion.intent).all()

print("\nIntent Distribution:")
for intent, count in intents:
    print(f"  {intent}: {count}")

# Average confidence
avg_conf = session.query(
    func.avg(UserQuestion.confidence)
).scalar()
print(f"\nAverage Confidence: {avg_conf:.2%}")

# High confidence percentage
total = session.query(UserQuestion).count()
high_conf = session.query(UserQuestion)\
    .filter(UserQuestion.confidence >= 0.7)\
    .count()
print(f"High Confidence: {high_conf/total if total > 0 else 0:.2%}")

session.close()
```

### Backup Database

```bash
# Backup PostgreSQL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql $DATABASE_URL < backup_20260101_120000.sql

# For Railway PostgreSQL backups:
# Use Railway Dashboard → Data → Backups
```

### Update Code

```bash
# Make changes locally
git add .
git commit -m "Update feature XYZ"
git push origin main

# Railway automatically deploys on push

# For self-hosted:
git pull
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

### Issue: Webhook Not Receiving Updates

```bash
# Check webhook status
curl https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo

# Should show:
# {
#   "ok": true,
#   "result": {
#     "url": "https://your-domain.com/webhook",
#     "has_custom_certificate": false,
#     "pending_update_count": 0,
#     "ip_address": "1.2.3.4",
#     "last_error_date": null
#   }
# }

# If pending_update_count > 0, delete and reset:
curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook

# Re-set webhook:
curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook \
  -d url="https://your-domain.com/webhook"
```

### Issue: Database Connection Timeout

```python
# Check connection
from database import engine
try:
    with engine.connect() as conn:
        print("✓ Database connected")
except Exception as e:
    print(f"✗ Database error: {e}")

# Check DATABASE_URL format
import os
print(os.getenv("DATABASE_URL"))
# Should be: postgresql://user:pass@host:port/db
```

### Issue: Groq API Rate Limited

```bash
# Check Groq API status
# Wait a few minutes and retry
# Upgrade Groq plan if needed: console.groq.com

# Monitor usage
# 1. Go to console.groq.com
# 2. Check "Usage" section
# 3. Add credits if needed
```

### Issue: Out of Memory

```bash
# Check available memory
free -h

# Check running processes
ps aux | grep python

# Check Railway resources
# 1. Railway Dashboard
# 2. Click python service
# 3. Check "Metrics" tab

# Solution: Upgrade Railway plan or optimize code
```

### Issue: Slow Responses

```bash
# Check Groq API latency
import requests
import time

start = time.time()
response = requests.get("https://api.groq.com/openai/v1/models")
latency = time.time() - start

print(f"API Latency: {latency:.2f}s")
# If > 2s, Groq servers might be slow

# Check database latency
from database import get_db_session
session = get_db_session()
start = time.time()
count = session.query(UserQuestion).count()
db_latency = time.time() - start
print(f"DB Latency: {db_latency:.2f}s")
```

---

## Scaling

### Vertical Scaling (More Powerful Server)

```
Railway Plan Upgrade:
  Free → $5/month → $15/month → Custom

1. Go to Railway Dashboard
2. Settings → Plan
3. Upgrade plan
4. Service restarts automatically
```

### Horizontal Scaling (Multiple Instances)

```bash
# In Procfile, add worker processes
web: uvicorn app:app --host 0.0.0.0 --port $PORT --workers 4

# For Railway, configure in railway.json:
{
  "builder": "dockerfile",
  "deploy": {
    "restartPolicyType": "always",
    "restartPolicyMaxRetries": 10
  }
}
```

### Load Balancing (Multiple Servers)

```
For production with high traffic:
  1. Deploy to multiple servers
  2. Use load balancer (Railway handles this)
  3. Share PostgreSQL database
  4. Use Telegram bot API (stateless)

Railway handles load balancing automatically.
```

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_user_id ON user_questions(user_id);
CREATE INDEX idx_intent ON user_questions(intent);
CREATE INDEX idx_timestamp ON user_questions(timestamp);

-- Analyze query performance
EXPLAIN ANALYZE
  SELECT * FROM user_questions
  WHERE intent = 'biaya_pendidikan'
  ORDER BY timestamp DESC
  LIMIT 10;
```

---

## Production Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] Database migrations run (`python init_database.py`)
- [ ] Telegram webhook set and verified
- [ ] Groq API key validated
- [ ] Knowledge base reviewed and updated
- [ ] Intent classifier models loaded
- [ ] Health check endpoint responds
- [ ] Database backups configured
- [ ] Logging level set to INFO
- [ ] Error handling tested
- [ ] Load test completed
- [ ] Monitoring/alerting configured
- [ ] Backup plan documented
- [ ] Runbook created for common issues

---

## Maintenance Schedule

### Daily
- Monitor logs for errors
- Check health endpoint
- Review bot performance metrics

### Weekly
- Analyze user questions and intents
- Check knowledge base accuracy
- Review user feedback

### Monthly
- Update dependencies
- Review and optimize database
- Backup and test restore
- Performance analysis
- User satisfaction check

### Quarterly
- Retrain intent classifier
- Update knowledge base
- Security audit
- Disaster recovery drill

---

## Disaster Recovery

### What to do if:

**Bot is down**:
1. Check health endpoint: `curl https://chatbot-psb.railway.app/health`
2. Check logs: Railway Dashboard → Logs
3. Check database: PostgreSQL still running?
4. Restart service: Railway Dashboard → Restart
5. Check external APIs: Groq, Telegram

**Database is corrupted**:
1. Stop the bot
2. Restore from backup: `psql $DATABASE_URL < backup_*.sql`
3. Restart bot

**Telegram API is down**:
1. Bot will still process questions
2. Responses won't be sent to Telegram
3. Questions will be logged
4. When Telegram recovers, resume sending

---

## Cost Estimation

### Railway Pricing (as of 2026)

```
Free Tier:
  - $5/month credit
  - Perfect for testing
  - May include limited resources

Paid:
  - $5-20/month base
  - PostgreSQL: included
  - Bandwidth: pay per GB
  - Memory: more = more cost
  - Typical cost: $5-15/month
```

### Example Costs

```
Usage: 100 questions/day

- Web Server: $5/month (shared resources)
- PostgreSQL: $5/month (included)
- Bandwidth: ~$1/month
- TOTAL: ~$6-11/month
```

---

## Support & Debugging

### Getting Help

- Check logs: `railway logs`
- Railway status: https://status.railway.app
- Telegram status: https://telegramstatus.com
- Groq status: https://console.groq.com (status page)

### Debug Mode

```bash
# Set LOG_LEVEL=DEBUG in Railway Environment

# Then check logs for detailed information
railway logs | grep DEBUG
```

### Contact Support

- Railway support: https://railway.app/support
- Telegram: https://core.telegram.org/bots/api
- Groq: https://console.groq.com/help

---

**🎉 Your chatbot is now in production!**
