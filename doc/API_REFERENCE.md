# 📡 Chatbot PSB - API Reference

Complete REST API documentation and integration guide.

---

## Table of Contents

1. [HTTP Endpoints](#http-endpoints)
2. [Telegram Webhook](#telegram-webhook)
3. [Response Format](#response-format)
4. [Error Codes](#error-codes)
5. [Integration Examples](#integration-examples)
6. [Rate Limiting](#rate-limiting)

---

## HTTP Endpoints

### Base URL

```
Development:  http://localhost:8000
Production:   https://chatbot-psb.railway.app
```

---

## Telegram Webhook Endpoint

### `POST /webhook`

Receive and process Telegram bot updates.

**Description**: 
Telegram Bot API calls this endpoint when a user sends a message. Process the update and send response back to user.

**URL**:
```
POST /webhook
```

**Request Headers**:
```
Content-Type: application/json
```

**Request Body** (Telegram Update Object):
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "date": 1672531200,
    "chat": {
      "id": -987654321,
      "type": "private",
      "username": "user123"
    },
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "John",
      "username": "user123",
      "language_code": "id"
    },
    "text": "Berapa biaya pendaftaran?"
  }
}
```

**Response**:
```json
{
  "status": "ok"
}
```

**Status Code**: `200 OK`

**Processing Flow**:
```
1. Extract message text
2. Get user ID and chat ID
3. Pass to Response Router
4. Classify intent
5. Load knowledge base
6. Generate response with Groq
7. Send message via Telegram API
8. Log to database
```

**Error Response**:
```json
{
  "status": "error",
  "error": "Invalid update format"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123,
    "message": {
      "message_id": 1,
      "date": 1672531200,
      "chat": {"id": 987654321},
      "from": {"id": 123456789, "username": "user123"},
      "text": "Berapa biaya pendaftaran?"
    }
  }'
```

**Example with Python**:
```python
import requests

webhook_url = "http://localhost:8000/webhook"
update = {
    "update_id": 123,
    "message": {
        "message_id": 1,
        "date": 1672531200,
        "chat": {"id": 987654321},
        "from": {"id": 123456789, "username": "user123"},
        "text": "Berapa biaya pendaftaran?"
    }
}

response = requests.post(webhook_url, json=update)
print(response.status_code)  # 200
```

---

## Health Check Endpoints

### `GET /health`

Liveness probe - check if service is running.

**URL**:
```
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T12:00:00Z"
}
```

**Status Code**: `200 OK`

**Purpose**: Used by monitoring systems and load balancers to verify service is alive.

**Example**:
```bash
curl http://localhost:8000/health
```

---

## Interactive API Documentation

### `GET /docs`

Swagger UI - Interactive API documentation (development only).

**URL**:
```
GET /docs
```

**Availability**: Only when `ENVIRONMENT=development`

**Access**:
```
http://localhost:8000/docs
```

---

### `GET /redoc`

ReDoc - Alternative API documentation (development only).

**URL**:
```
GET /redoc
```

**Availability**: Only when `ENVIRONMENT=development`

---

## Response Format

### Success Response (via Telegram)

When a user sends a message to the bot:

```
User Message:
"Berapa biaya pendaftaran santri baru?"

Bot Response (Telegram sendMessage):
"Biaya pendaftaran santri baru kami adalah:
- Biaya Pendaftaran: Rp 500.000
- Biaya SPP Bulanan: Rp 1.500.000
- Biaya Pembangunan: Rp 2.000.000

Hubungi admin untuk informasi lebih lanjut."
```

### Response Metadata (Internal)

The system internally generates:

```json
{
  "success": true,
  "message": "Biaya pendaftaran santri baru kami adalah...",
  "intent": "biaya_pendidikan",
  "confidence": 0.94,
  "confidence_level": "HIGH",
  "knowledge_base_used": true,
  "llm_used": true,
  "error": null,
  "question_id": 42
}
```

### Error Response

When something goes wrong:

```json
{
  "success": false,
  "message": "Maaf, saya tidak dapat memahami pertanyaan Anda. Silakan coba lagi.",
  "intent": null,
  "confidence": 0,
  "confidence_level": "UNKNOWN",
  "knowledge_base_used": false,
  "llm_used": false,
  "error": "Intent classifier error: Model not loaded",
  "question_id": null
}
```

---

## Response Components

### `message` (string)

The final response sent to user.

```
Biaya pendaftaran santri baru kami adalah:
- Biaya Daftar: Rp 500.000
- Biaya SPP: Rp 1.500.000 per bulan
```

### `intent` (string)

Predicted intent category. Possible values:

```
"biaya_pendidikan"      - Education costs
"eskalasi_admin"        - Admin escalation
"faq_umum"              - General FAQ
"info_pendaftaran"      - Registration info
"kegiatan_harian"       - Daily activities
"kirim_dokumen"         - Document submission
"link_formulir"         - Form links
"pendidikan_formal"     - Formal education
"program_unggulan"      - Featured programs
"syarat_pendaftaran"    - Registration requirements
"syariah_guard"         - Islamic compliance
```

### `confidence` (float)

Confidence score of intent prediction. Range: 0.0 to 1.0

```
0.94  = 94% confidence (HIGH)
0.65  = 65% confidence (MEDIUM)
0.45  = 45% confidence (LOW)
```

### `confidence_level` (string)

Human-readable confidence level:

```
"very_high" - confidence >= 0.90
"high"      - confidence >= 0.70 (CONFIDENCE_THRESHOLD)
"medium"    - 0.50 <= confidence < 0.70
"low"       - 0.30 <= confidence < 0.50
"very_low"  - confidence < 0.30
```

### `knowledge_base_used` (boolean)

Whether knowledge base data was consulted.

```
true  - KB data was loaded and used
false - KB data was not available or not used
```

### `llm_used` (boolean)

Whether Groq API was called for response refinement.

```
true  - LLM refined the response
false - Groq API was not called (error/fallback)
```

### `question_id` (integer|null)

Database ID of the logged question.

```
42      - Question logged successfully
null    - Logging failed (will still respond to user)
```

### `error` (string|null)

Error message if something went wrong.

```
"Intent classifier error: Model not loaded"
"Groq API timeout: exceeded 30 seconds"
"Database connection failed"
null - No error
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Request processed successfully |
| `400` | Bad Request | Invalid webhook format |
| `500` | Internal Error | Unexpected server error |
| `503` | Service Unavailable | Components not ready |

### Application Error Codes

| Error | Cause | Resolution |
|-------|-------|------------|
| `CLASSIFIER_ERROR` | Intent classifier failed | Restart service, check models |
| `KB_NOT_FOUND` | Knowledge base file missing | Add missing .json file to knowledge_base/ |
| `GROQ_TIMEOUT` | Groq API took too long | Retry, check Groq status |
| `GROQ_ERROR` | Groq API error | Check API key, rate limits |
| `DB_ERROR` | Database connection failed | Check DATABASE_URL, PostgreSQL status |
| `INVALID_INPUT` | Bad user input | User input validation failed |

---

## Integration Examples

### Python Integration

```python
import requests
import json

# Simulate Telegram webhook
webhook_url = "http://localhost:8000/webhook"

update = {
    "update_id": 123,
    "message": {
        "message_id": 1,
        "date": 1672531200,
        "chat": {"id": 987654321},
        "from": {"id": 123456789, "username": "user123"},
        "text": "Berapa biaya pendaftaran?"
    }
}

response = requests.post(webhook_url, json=update)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### JavaScript Integration (Node.js)

```javascript
const axios = require('axios');

const webhookUrl = 'http://localhost:8000/webhook';

const update = {
  update_id: 123,
  message: {
    message_id: 1,
    date: 1672531200,
    chat: { id: 987654321 },
    from: { id: 123456789, username: 'user123' },
    text: 'Berapa biaya pendaftaran?'
  }
};

axios.post(webhookUrl, update)
  .then(response => {
    console.log('Status:', response.status);
    console.log('Response:', response.data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### cURL Integration

```bash
#!/bin/bash

WEBHOOK_URL="http://localhost:8000/webhook"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123,
    "message": {
      "message_id": 1,
      "date": 1672531200,
      "chat": {"id": 987654321},
      "from": {"id": 123456789, "username": "user123"},
      "text": "Berapa biaya pendaftaran?"
    }
  }' \
  -w "\nStatus: %{http_code}\n"
```

### Multiple Language Support

```python
# The bot works with any language
languages = [
    "Berapa biaya pendaftaran?",      # Indonesian
    "什么是入学费用？",               # Chinese
    "What are registration fees?",     # English
    "Quels sont les frais d'inscription?" # French
]

# All will be processed and matched to appropriate intent
```

---

## Rate Limiting

### Telegram Limits

Telegram Bot API has built-in rate limiting:

```
- 30 messages per second per bot
- 100 concurrent requests
- Connection timeout: 30 seconds
```

The chatbot handles these limits automatically.

### Groq API Limits

Depends on your Groq API plan:

```
Free Plan:
- 30 requests per minute
- 500 requests per day

Paid Plans:
- Higher limits available
- Contact Groq for custom limits
```

**Handling Rate Limits**:

If Groq API is rate limited:
```python
# Automatic fallback
if groq_rate_limited:
    # Use knowledge base response without LLM refinement
    return kb_only_response
```

### Database Limits

PostgreSQL handles concurrent connections:

```
- Default: 100 concurrent connections
- Railway free: Sufficient for chatbot
- Upgrade if needed
```

---

## Request Validation

### Webhook Validation

The chatbot validates incoming webhooks:

```python
def validate_webhook(update_data):
    # Check required fields
    assert 'update_id' in update_data
    assert 'message' in update_data
    assert 'text' in update_data['message']
    
    # Check chat exists
    assert 'chat' in update_data['message']
    assert 'id' in update_data['message']['chat']
    
    # Check user exists
    assert 'from' in update_data['message']
    assert 'id' in update_data['message']['from']
    
    return True
```

### Input Sanitization

```python
def sanitize_input(question: str) -> str:
    # Remove leading/trailing whitespace
    question = question.strip()
    
    # Truncate to 1000 chars (safety)
    question = question[:1000]
    
    # Remove null bytes
    question = question.replace('\x00', '')
    
    return question
```

---

## Timeout Specifications

| Component | Timeout | Note |
|-----------|---------|------|
| Telegram webhook | 30s | Set by Telegram |
| Groq API | 30s | Dikonfigurasi di requests.post() |
| Telegram sendMessage | 10s | Retry tanpa parse_mode jika gagal |
| Telegram sendChatAction | 5s | Fire-and-forget |
| Intent classifier | <100ms | In-memory |

---

## API Security

### Authentication

- **Telegram**: Bot token validates all requests
- **Groq**: API key in Authorization header
- **Database**: Connection string with credentials

### HTTPS

- **Production**: Always use HTTPS
- **Development**: HTTP allowed (localhost)

### Data Privacy

- User messages are logged to database
- Database should be protected/encrypted
- No data sharing with third parties (except Groq for processing)

---

## Monitoring API

### Available Metrics

```bash
# Via database queries
SELECT COUNT(*) FROM user_questions;  # Total questions
SELECT COUNT(*) FROM user_questions WHERE DATE(timestamp) = CURRENT_DATE;  # Today
SELECT intent, COUNT(*) FROM user_questions GROUP BY intent;  # By intent
SELECT AVG(confidence) FROM user_questions;  # Average confidence
```

### Health Status

```bash
# Check health status
curl http://localhost:8000/health

# Returns:
# {
#   "status": "healthy",
#   "components": {
#     "bot_handler": "ready",
#     "database": "connected",
#     "intent_classifier": "loaded"
#   }
# }
```

---

## Version Information

```
API Version: 1.0.0
Compatible Telegram Bot API: v7.0+
OpenAI API Compatibility: v1 (for Groq)
Python: 3.10+
FastAPI: >=0.104.0
```

---

## Changelog

### Version 1.0.0 (2026-01-01)
- Initial release
- Telegram webhook support
- Double Guard Architecture
- Knowledge base integration
- PostgreSQL logging

---

## Support

For API issues:
1. Check status: `GET /health`
2. Check logs
3. Review error messages
4. Check documentation
5. Contact support

---

**API is ready for integration! 🚀**
