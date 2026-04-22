# 🔧 Chatbot PSB - Component Reference Guide

## Overview

This guide provides detailed documentation for each component of the Chatbot PSB system.

---

## Table of Contents

1. [Core Components](#core-components)
2. [Component APIs](#component-apis)
3. [Data Classes](#data-classes)
4. [Configuration](#configuration)
5. [Component Dependencies](#component-dependencies)

---

## Core Components

### 1. Telegram Bot Handler (`telegram_bot.py`)

**Purpose**: Handles all Telegram Bot API integration

**Initialization**:
```python
from telegram_bot import TelegramBotHandler

handler = TelegramBotHandler()
# Requires: TELEGRAM_BOT_TOKEN environment variable
```

**Key Methods**:

#### `async process_update(update_data: Dict[str, Any])`
Process incoming Telegram webhook updates.

```python
# Called by FastAPI webhook endpoint
await handler.process_update({
    "update_id": 123456,
    "message": {
        "message_id": 1,
        "chat": {"id": 987654321},
        "from": {
            "id": 123456789,
            "username": "user123"
        },
        "text": "Berapa biaya pendaftaran?"
    }
})
```

**Processing**:
1. Extract message from update
2. Validate chat_id and user_id
3. Call Response Router
4. Send response back via Telegram API

#### `send_message(chat_id: int, text: str)`
Send a message to user via Telegram.

```python
await handler.send_message(
    chat_id=987654321,
    text="Biaya pendaftaran adalah..."
)
```

#### `send_error(chat_id: int, error_message: str)`
Send error message when something goes wrong.

```python
await handler.send_error(
    chat_id=987654321,
    error_message="Maaf, terjadi kesalahan. Silakan coba lagi."
)
```

#### `handle_command(message: Dict[str, Any])`
Process bot commands like `/start`, `/help`.

```python
# Available commands:
# /start - Initialize and show welcome message
# /help - Show help information
# /status - Show bot status
```

**Dependencies**:
- `requests` - HTTP calls to Telegram API
- `response_router.py` - Core processing logic

**Environment Variables**:
- `TELEGRAM_BOT_TOKEN` (required)
- `TELEGRAM_WEBHOOK_URL` (optional, for webhook mode)

---

### 2. FastAPI Application (`app.py`)

**Purpose**: Web server and webhook handler

**Key Features**:
- FastAPI REST API server
- Telegram webhook endpoint
- Health check endpoints
- Graceful startup/shutdown
- CORS middleware for development

**Endpoints**:

#### `POST /webhook`
Receive Telegram webhook updates

```
POST /webhook
Content-Type: application/json

{
  "update_id": 123456,
  "message": { ... }
}

Response: 200 OK
```

#### `GET /health`
Liveness probe for monitoring

```
GET /health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2026-01-01T12:00:00Z"
}
```

#### `GET /ready`
Readiness probe - checks if all components are initialized

```
GET /ready

Response: 200 OK (if ready) or 503 (if not ready)
{
  "ready": true,
  "components": {
    "intent_classifier": "ready",
    "groq_client": "ready",
    "database": "ready"
  }
}
```

**Startup Sequence**:
```python
@app.on_event("startup")
async def startup():
    # 1. Load models
    get_intent_classifier()
    
    # 2. Initialize database
    init_db()
    
    # 3. Verify Groq API
    get_groq_client()
    
    # 4. Initialize Telegram handler
    TelegramBotHandler()
```

**Deployment**:
```bash
# Development (with auto-reload)
python app.py

# Production (with gunicorn/uvicorn)
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

**Configuration**:
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- `ENVIRONMENT`: development, production
- `PORT`: Server port (default 8000)

---

### 3. Response Router (`response_router.py`)

**Purpose**: Core orchestration and decision logic

**Initialization**:
```python
from response_router import ResponseRouter, get_response_router

# Singleton access
router = get_response_router()

# Or direct instantiation
router = ResponseRouter(knowledge_base_dir="knowledge_base")
```

**Main Method**: `process_question()`

```python
result = router.process_question(
    question="Berapa biaya pendaftaran santri baru?",
    user_id="123456789",
    platform="telegram"
)

print(result)
# ResponseResult(
#   success=True,
#   message="Biaya pendaftaran adalah...",
#   intent="biaya_pendidikan",
#   confidence=0.94,
#   confidence_level="HIGH",
#   knowledge_base_used=True,
#   llm_used=True,
#   error=None,
#   question_id=42
# )
```

**Processing Pipeline**:

```
1. Input Validation
   └─ Validate question string, user_id
   
2. Intent Classification (Guard 1)
   ├─ Call intent_classifier.predict()
   ├─ Get: intent, confidence, probabilities
   └─ Check confidence threshold
   
3. Load Knowledge Base
   ├─ Load {intent}.json file
   ├─ Parse JSON data
   └─ Handle missing files gracefully
   
4. Groq API Call (Guard 2)
   ├─ Build prompt with guardrails
   ├─ Include KB data in context
   ├─ Call Groq API
   └─ Handle timeouts/errors
   
5. Database Logging
   ├─ Create UserQuestion record
   ├─ Store question, intent, response
   ├─ Handle connection errors
   └─ Continue even if DB fails
   
6. Return Response
   └─ ResponseResult with all metadata
```

**Error Handling Strategy**:

```python
# Try full pipeline
try:
    # Full double guard
    response = self._process_with_groq(...)
except GroqError:
    # Fallback: Use KB without LLM
    response = self._process_without_groq(...)
except KBNotFound:
    # Fallback: Generic message
    response = self._generic_response(intent, confidence)
except Exception as e:
    # Last resort: Error message
    response = ResponseResult(success=False, ...)
```

**Confidence Levels**:
- `HIGH`: confidence ≥ 0.7 → Use full pipeline
- `MEDIUM`: 0.5 ≤ confidence < 0.7 → Use KB, cautious LLM
- `LOW`: confidence < 0.5 → Best guess, with disclaimer

**Knowledge Base Loading**:
```python
def _load_knowledge_base(self, intent: str) -> Dict:
    """Load knowledge base file for given intent"""
    kb_file = self.knowledge_base_dir / f"{intent}.json"
    
    if not kb_file.exists():
        # File not found, graceful fallback
        return {"intent": intent, "data": []}
    
    with open(kb_file, 'r', encoding='utf-8') as f:
        return json.load(f)
```

---

### 4. Intent Classifier (`intent_classifier.py`)

**Purpose**: Guard Layer 1 - Intent classification and context determination

**Initialization**:
```python
from intent_classifier import IntentClassifier, get_intent_classifier

# Singleton access (recommended)
classifier = get_intent_classifier()

# Direct instantiation
classifier = IntentClassifier(
    models_dir="models",
    confidence_threshold=0.7
)
```

**Model Files** (in `models/` directory):
- `vectorizer.pkl` - TF-IDF Vectorizer
- `model.pkl` - Logistic Regression Classifier  
- `label_encoder.pkl` - Intent label encoder

**Key Method**: `predict()`

```python
result = classifier.predict(
    question="Berapa biaya pendaftaran?"
)

# Returns IntentPrediction object
print(result)
# IntentPrediction(
#   intent='biaya_pendidikan',
#   confidence=0.94,
#   all_probabilities={
#     'biaya_pendidikan': 0.94,
#     'info_pendaftaran': 0.04,
#     'syarat_pendaftaran': 0.02,
#     ...
#   },
#   is_confident=True
# )
```

**Training Pipeline**:

The classifier is trained from:
1. **Training Data**: `data/intents_v2.csv`
2. **Training Script**: `notebooks/intent_classifier_training_executed_v2.ipynb`
3. **Algorithm**:
   - Vectorization: TF-IDF (max_features=1000, ngram_range=(1,2))
   - Classification: Logistic Regression
4. **Output**: Serialized models in `models/` directory

**Retraining Process**:
```bash
# 1. Prepare training data in data/intents_v2.csv
#    Format: question,intent (CSV with header)

# 2. Run training notebook
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb

# 3. Models are saved to models/ directory
# 4. Commit changes and deploy
```

**All Available Intents**:
```python
intents = classifier.get_all_intents()
# Returns list of all trained intent labels

# Example output:
[
    'biaya_pendidikan',
    'eskalasi_admin',
    'faq_umum',
    'info_pendaftaran',
    'kegiatan_harian',
    'kirim_dokumen',
    'link_formulir',
    'pendidikan_formal',
    'program_unggulan',
    'syarat_pendaftaran',
    'syariah_guard'
]
```

**Batch Prediction**:
```python
questions = [
    "Berapa biaya pendaftaran?",
    "Apa saja syaratnya?",
    "Kapan pembukaan pendaftaran?"
]

results = classifier.predict_batch(questions)
# Returns list of IntentPrediction objects
```

**Confidence Analysis**:
```python
# Access all probabilities for analysis
prediction = classifier.predict("Pertanyaan?")

if prediction.is_confident:
    # Use full response pipeline
    print(f"High confidence: {prediction.confidence}")
else:
    # Use degraded pipeline
    print(f"Low confidence: {prediction.confidence}")
    print(f"Runner-up: {sorted(...)[1]}")
```

---

### 5. Groq Client (`groq_client.py`)

**Purpose**: Guard Layer 2 - LLM bounded reasoning

**Initialization**:
```python
from groq_client import GroqClient, get_groq_client

# Singleton access (recommended)
client = get_groq_client()

# Direct instantiation
client = GroqClient()
# Requires: GROQ_API_KEY environment variable
```

**Configuration** (via environment variables):
- `GROQ_API_KEY` (required)
- `GROQ_MODEL` (default: "llama-3.3-70b-versatile")
- `GROQ_MAX_TOKENS` (default: 500)
- `GROQ_TEMPERATURE` (default: 0.3)

**Main Method**: `generate_response()`

```python
response = client.generate_response(
    question="Berapa biaya pendaftaran?",
    intent="biaya_pendidikan",
    confidence=0.94,
    knowledge_base_data={
        "intent": "biaya_pendidikan",
        "items": [
            {"biaya_daftar": "500.000 rupiah"},
            {"biaya_SPP": "1.500.000 per bulan"}
        ]
    }
)

print(response)
# GroqResponse(
#   success=True,
#   message="Biaya pendaftaran santri baru kami adalah...",
#   intent="biaya_pendidikan",
#   confidence=0.94,
#   error=None
# )
```

**System Prompt Design**:

The system prompt includes:

1. **Role Definition**:
   ```
   Anda adalah asisten chatbot untuk Penerimaan Santri Baru (PSB).
   Tugas Anda adalah menjawab pertanyaan dengan sopan dan informatif.
   ```

2. **Guardrails**:
   ```
   HARUS:
   - Gunakan HANYA data knowledge base yang disediakan
   - Pertahankan intent yang telah diklasifikasi
   - Gunakan bahasa sopan dan ramah
   - Jawab dalam konteks PSB Pondok Pesantren
   
   TIDAK BOLEH:
   - Mengubah intent dari pertanyaan
   - Menambahkan informasi di luar knowledge base
   - Menjawab di luar topik PSB
   - Membuat informasi baru
   ```

3. **Context**:
   ```
   Knowledge Base untuk intent "{intent}":
   {actual_kb_data_as_json}
   ```

4. **Expected Output Format**:
   ```json
   {
     "message": "Jawaban natural dalam bahasa Indonesia",
     "intent": "intent_dari_pertanyaan",
     "confidence": 0.94
   }
   ```

**API Details**:

- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Model**: `llama-3.3-70b-versatile` (customizable)
- **Auth**: Bearer token in `Authorization` header
- **Format**: OpenAI-compatible Chat API

**Request Format**:
```python
request = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    "temperature": 0.3,
    "max_tokens": 500,
    "top_p": 1
}
```

**Error Handling**:
```python
# Timeout handling
response = client.generate_response(...)  # 5s timeout

# API errors
try:
    response = client.generate_response(...)
except requests.exceptions.Timeout:
    # Return fallback without LLM
    return fallback_response
except requests.exceptions.RequestException as e:
    # Log error and return safe response
    logger.error(f"Groq API error: {e}")
    return safe_fallback
```

**Response Validation**:
```python
# Validates that:
# 1. Intent matches original intent (not changed)
# 2. Response is within safety guidelines
# 3. No hallucinated information
# 4. Proper JSON structure
```

---

### 6. Database (`database.py`)

**Purpose**: Persistent logging and analytics

**Setup**:
```python
from database import init_db, get_db_session, log_user_question

# Initialize database on startup
init_db()

# Get session for operations
session = get_db_session()
```

**Data Models**:

#### `UserQuestion`
```python
class UserQuestion(Base):
    __tablename__ = "user_questions"
    
    id: int              # Primary key
    user_id: str         # Telegram user ID
    platform: str        # "telegram", "web", etc.
    question: str        # Original user question
    intent: str          # Predicted intent
    confidence: float    # Confidence score (0-1)
    response: str        # Bot response
    timestamp: datetime  # When question was asked
    # Optional fields:
    feedback: str        # User feedback (if provided)
    is_correct: bool     # If intent was correct
```

**Logging Questions**:
```python
from database import log_user_question

question_id = log_user_question(
    user_id="123456789",
    platform="telegram",
    question="Berapa biaya pendaftaran?",
    intent="biaya_pendidikan",
    confidence=0.94,
    response="Biaya pendaftaran adalah...",
    username="user123"
)
# Returns: ID of logged question
```

**Database Connection**:

```python
# Production (Railway)
DATABASE_URL = os.getenv("DATABASE_URL")
# Format: postgresql://user:pass@host:port/db

# Development (local)
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
```

**Querying Data**:
```python
from database import SessionLocal
from database import UserQuestion

session = SessionLocal()

# Get all questions
all_questions = session.query(UserQuestion).all()

# Get questions for specific user
user_questions = session.query(UserQuestion)\
    .filter(UserQuestion.user_id == "123456789")\
    .all()

# Get questions by intent
intent_questions = session.query(UserQuestion)\
    .filter(UserQuestion.intent == "biaya_pendidikan")\
    .all()

# Statistics
high_conf = session.query(UserQuestion)\
    .filter(UserQuestion.confidence >= 0.7)\
    .count()

session.close()
```

**Analytics Queries**:
```python
# Intent distribution
from sqlalchemy import func
intent_counts = session.query(
    UserQuestion.intent,
    func.count(UserQuestion.id).label('count')
).group_by(UserQuestion.intent).all()

# Average confidence per intent
avg_confidence = session.query(
    UserQuestion.intent,
    func.avg(UserQuestion.confidence).label('avg_conf')
).group_by(UserQuestion.intent).all()

# Questions per day
daily_counts = session.query(
    func.date(UserQuestion.timestamp).label('date'),
    func.count(UserQuestion.id).label('count')
).group_by(func.date(UserQuestion.timestamp)).all()
```

---

## Data Classes

### IntentPrediction
```python
@dataclass
class IntentPrediction:
    intent: str                              # Predicted intent label
    confidence: float                        # Confidence score (0-1)
    all_probabilities: Dict[str, float]     # All intent probabilities
    is_confident: bool                       # True if confidence >= 0.7
```

### GroqResponse
```python
@dataclass
class GroqResponse:
    success: bool              # Whether API call succeeded
    message: str               # Response message
    intent: str                # Intent (should match input)
    confidence: float          # Confidence score
    error: Optional[str] = None  # Error message if failed
```

### ResponseResult
```python
@dataclass
class ResponseResult:
    success: bool                           # Overall success
    message: str                            # Final response message
    intent: str                             # Predicted intent
    confidence: float                       # Confidence score
    confidence_level: str                   # "HIGH", "MEDIUM", "LOW"
    knowledge_base_used: bool               # Was KB consulted?
    llm_used: bool                          # Was Groq API used?
    error: Optional[str] = None             # Error message if failed
    question_id: Optional[int] = None       # Database record ID
```

---

## Configuration

### Environment Variables

**Required** (must be set):
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Optional** (have defaults):
```
# Application
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
ENVIRONMENT=production             # production or development

# Groq API
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3

# Server
PORT=8000
WORKERS=4

# Intent Classifier
CLASSIFIER_CONFIDENCE_THRESHOLD=0.7

# Knowledge Base
KB_DIR=knowledge_base
```

### Local Development (.env)

```bash
# Copy and customize
cp .env.example .env

# Edit .env with your values
TELEGRAM_BOT_TOKEN=your_token_here
GROQ_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot_psb
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

---

## Component Dependencies

### Dependency Graph

```
FastAPI (app.py)
  ├─ TelegramBotHandler (telegram_bot.py)
  │  ├─ ResponseRouter (response_router.py)
  │  │  ├─ IntentClassifier (intent_classifier.py)
  │  │  │  ├─ scikit-learn
  │  │  │  ├─ joblib
  │  │  │  └─ numpy
  │  │  │
  │  │  ├─ GroqClient (groq_client.py)
  │  │  │  └─ requests
  │  │  │
  │  │  ├─ DatabaseSession (database.py)
  │  │  │  ├─ SQLAlchemy
  │  │  │  └─ psycopg2
  │  │  │
  │  │  └─ Knowledge Base (JSON files)
  │  │
  │  └─ requests (Telegram API calls)
  │
  ├─ Database (database.py)
  ├─ CORS Middleware
  └─ Logging
```

### Import Structure

```python
# Core orchestration
from response_router import get_response_router

# Sub-components (usually auto-initialized by router)
from intent_classifier import get_intent_classifier
from groq_client import get_groq_client
from database import init_db, get_db_session

# Models/Types
from response_router import ResponseResult, IntentPrediction
from groq_client import GroqResponse
```

### Loading Order

1. **Startup** (FastAPI):
   - Load environment variables (.env)
   - Configure logging
   - Initialize database engine
   - Load intent classifier models
   - Test Groq API connection
   - Initialize Telegram handler

2. **Request Processing**:
   - Receive Telegram update
   - Create response router session
   - Process through guards
   - Log to database
   - Return response

3. **Shutdown**:
   - Close database connections
   - Cleanup resources
   - Flush logs

---

## Best Practices

### Using Singleton Components
```python
# ✅ GOOD: Get singleton instance
classifier = get_intent_classifier()

# ❌ BAD: Create new instance every time
classifier = IntentClassifier()  # Loads models every time!
```

### Error Handling
```python
# ✅ GOOD: Try-except with fallback
try:
    response = groq_client.generate_response(...)
except Exception as e:
    logger.error(f"Groq error: {e}")
    response = kb_only_response()

# ❌ BAD: Let exception propagate
response = groq_client.generate_response(...)
```

### Logging
```python
# ✅ GOOD: Informative log messages
logger.info(f"Processing question from user {user_id}: {question[:50]}...")

# ❌ BAD: Vague log messages
logger.info("Processing")
```

### Database Sessions
```python
# ✅ GOOD: Use context manager
session = SessionLocal()
try:
    # Do work
finally:
    session.close()

# ✅ ALSO GOOD: With context manager
with SessionLocal() as session:
    # Do work
```

