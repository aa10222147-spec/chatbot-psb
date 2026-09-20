# 🏗️ Chatbot PSB - Complete Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Double Guard Architecture](#double-guard-architecture)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Patterns](#design-patterns)
7. [Security & Safety](#security--safety)
8. [Deployment Architecture](#deployment-architecture)

---

## System Overview

**Chatbot PSB** is an intelligent conversational chatbot designed for **Penerimaan Santri Baru (PSB)** - Student Admission for Islamic Boarding School - using a hybrid NLP architecture with dual guard layers.

### Key Characteristics

- **Intent-Based**: Uses machine learning for intent classification
- **Hybrid Approach**: Combines classical NLP with modern LLM reasoning
- **Knowledge-Driven**: All responses grounded in curated knowledge base
- **Double Guard**: Prevents hallucination through layered decision making
- **Production-oriented**: logging PostgreSQL, FastAPI healthcheck; jawaban tetap single-turn (tanpa memori percakapan)
- **Platform**: Telegram Bot API (webhook + polling support)

---

## Double Guard Architecture

The **Double Guard Architecture** is the core innovation that ensures safe, accurate responses while preventing hallucination.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    USER QUERY (Telegram)                             │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  TELEGRAM BOT HANDLER   │
                    │  (Message Extraction)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │    RESPONSE ROUTER (Orchestrator)       │
                    │    (Central Control & Pipeline)         │
                    └─────────┬──────────────────┬────────────┘
                              │                  │
                    ┌─────────▼──────────┐  ┌───▼────────────────┐
                    │ GUARD LAYER 1      │  │   GUARD LAYER 2    │
                    │ Intent Classifier  │  │   LLM (Groq)       │
                    │                    │  │   Bounded Reasoning│
                    │ • TF-IDF Vector    │  │                    │
                    │ • Logistic Regr.   │  │ • Refine Language  │
                    │ • Returns: Intent  │  │ • Validate Intent  │
                    │   + Confidence     │  │ • Within KB scope  │
                    └─────────┬──────────┘  └───┬────────────────┘
                              │                  │
                    ┌─────────▼──────────────────▼──────┐
                    │  KNOWLEDGE BASE (Single Source)   │
                    │  - biaya_pendidikan.json          │
                    │  - info_pendaftaran.json          │
                    │  - syarat_pendaftaran.json        │
                    │  - ... (10 JSON files total)      │
                    └─────────┬──────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  DATABASE (LoggDB) │
                    │  • User Questions  │
                    │  • Responses       │
                    │  • Feedback        │
                    └────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   RESPONSE BACK    │
                    │   to Telegram User │
                    └────────────────────┘
```

### Guard Layer 1: Intent Classification

**Role**: PRIMARY decision maker - Context controller

```
INPUT: "Berapa biaya pendaftaran santri baru?"
  │
  ├─ TF-IDF Vectorization
  │   └─ Convert text to numerical features
  │
  ├─ Logistic Regression Classification
  │   └─ Predict intent with probability
  │
OUTPUT: {
  "intent": "biaya_pendidikan",
  "confidence": 0.94,
  "all_probabilities": {
    "biaya_pendidikan": 0.94,
    "info_pendaftaran": 0.04,
    "syarat_pendaftaran": 0.02
  }
}
```

**Characteristics**:
- Runs FIRST before any LLM interaction
- Determines the answer space (knowledge base file to use)
- Provides confidence score for validation
- Works with low-confidence fallback (demo mode)
- Fully deterministic and explainable

### Guard Layer 2: LLM Bounded Reasoning

**Role**: SECONDARY refinement - Language improvement only

```
INPUT: {
  "question": "Berapa biaya pendaftaran santri baru?",
  "intent": "biaya_pendidikan",
  "confidence": 0.94,
  "kb_data": { /* JSON data from knowledge base */ }
}
  │
  ├─ System Prompt (Strict Guardrails)
  │   ├─ Don't change intent
  │   ├─ Only use provided KB data
  │   ├─ Maintain polite tone
  │   ├─ Don't answer outside PSB domain
  │   └─ Don't make up information
  │
  ├─ LLaMA 3.3 70B Versatile Processing
  │   └─ Refine response for natural language
  │
OUTPUT: {
  "success": true,
  "message": "Biaya pendaftaran santri baru kami adalah...",
  "intent": "biaya_pendidikan",
  "confidence": 0.94
}
```

**Characteristics**:
- Acts ONLY as language refinement layer
- Cannot modify intent predicted by Guard 1
- Cannot add information beyond knowledge base
- Cannot answer questions outside PSB domain
- Has strict token limits (500 max)
- Low temperature (0.3) for consistency

### Why Double Guard?

| Aspect | Guard 1 Only | Guard 2 Only | Double Guard |
|--------|-------------|------------|--------------|
| **Intent Accuracy** | ✅ Excellent | ❌ Unreliable | ✅ Excellent |
| **Language Quality** | ❌ Robotic | ✅ Natural | ✅ Natural |
| **Hallucination Risk** | ❌ Low | ⚠️ High | ✅ Very Low |
| **Interpretability** | ✅ Clear | ❌ Black box | ✅ Clear |
| **Response Speed** | ✅ Fast | ⚠️ Slower | ✅ Balanced |

---

## System Components

### 1. Telegram Bot Handler (`telegram_bot.py`)

**Responsibility**: Integration with Telegram Bot API

```
Component: TelegramBotHandler
├─ Dependencies: requests (Telegram Bot HTTP API)
├─ Methods:
│  ├─ __init__(): Initialize with TELEGRAM_BOT_TOKEN
│  ├─ process_update(): Handle webhook/polling updates
│  ├─ send_message(): Send message to user
│  ├─ send_error(): Send error message
│  └─ handle_command(): Process /start, /help, etc.
└─ Interfaces: FastAPI webhook, polling loop
```

**Input**: Telegram Update JSON
**Output**: Telegram sendMessage API call

**Key Environment Variables**:
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather

### 2. FastAPI Application (`app.py`)

**Responsibility**: Web server and webhook handling

```
Component: FastAPI App
├─ Endpoints:
│  ├─ GET /: Info layanan & status
│  ├─ POST /webhook: Telegram webhook endpoint
│  ├─ GET /health: Health check (liveness probe)
│  ├─ GET /webhook/info: Debug webhook config
│  └─ /debug/*: Test endpoints (development only)
├─ Middleware:
│  ├─ CORS handling
│  └─ Error handling (404, 500)
└─ Lifecycle:
   ├─ startup: Validate env vars, init database, init bot handler
   └─ shutdown: Log shutdown
```

**Deployment Modes**:
- **Development**: `python app_polling.py` (polling, tanpa URL publik)
- **Production**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 3. Response Router (`response_router.py`)

**Responsibility**: Core orchestration and pipeline

```
Component: ResponseRouter
├─ State: Intent Classifier, Groq Client, Knowledge Base
├─ Main Method: process_question()
│  ├─ Step 1: Classify intent (Guard 1)
│  ├─ Step 2: Load knowledge base
│  ├─ Step 3: Call Groq API (Guard 2)
│  ├─ Step 4: Log to database
│  └─ Step 5: Return ResponseResult
└─ Fallback Handling: Graceful degradation on errors
```

**Processing Pipeline**:
```
Question
  ↓
1. Intent Classification (Guard 1)
  │ └─ Confidence check
  │
2. Load Knowledge Base by Intent
  │ └─ File not found handling
  │
3. Build Groq Prompt
  │ └─ Constraint enforcement
  │
4. Call Groq API (Guard 2)
  │ └─ Timeout/error handling
  │
5. Database Logging
  │ └─ Async logging
  │
6. Return Response
  └─ Success or error response
```

### 4. Intent Classifier (`intent_classifier.py`)

**Responsibility**: Guard Layer 1 - Intent prediction

```
Component: IntentClassifier
├─ Models (Pre-trained, serialized as .pkl):
│  ├─ vectorizer: TF-IDF Vectorizer
│  ├─ model: Logistic Regression Classifier
│  └─ label_encoder: Intent label encoder
├─ Methods:
│  ├─ predict(): Single prediction
│  ├─ get_all_intents(): List available intents
│  └─ confidence_threshold: Default 0.70
└─ Input: User question (string)
   Output: IntentPrediction (intent, confidence, probabilities)
```

**Training Data**:
- Source: `data/intents_v2.csv`
- Algorithm: TF-IDF + Logistic Regression
- Training notebook: `notebooks/intent_classifier_training_executed_v2.ipynb`

**Available Intents** (from knowledge_base/ JSON files):
```
1. biaya_pendidikan - Education costs
2. eskalasi_admin - Admin escalation
3. faq_umum - General FAQ
4. info_pendaftaran - Registration info
5. kegiatan_harian - Daily activities
6. kirim_dokumen - Document submission
7. link_formulir - Form links
8. pendidikan_formal - Formal education
9. program_unggulan - Featured programs
10. syarat_pendaftaran - Registration requirements
```

### 5. Groq Client (`groq_client.py`)

**Responsibility**: Guard Layer 2 - LLM bounded reasoning

```
Component: GroqClient
├─ API:
│  ├─ Endpoint: https://api.groq.com/openai/v1/chat/completions
│  ├─ Model: llama-3.3-70b-versatile
│  ├─ Max Tokens: 500
│  └─ Temperature: 0.3 (low for consistency)
├─ Methods:
│  ├─ generate_response(): Main processing
│  └─ _build_system_prompt(): Guardrails
└─ Error Handling:
   ├─ API timeout
   ├─ Rate limiting
   └─ Invalid responses
```

**System Prompt Structure**:
```
1. Role Definition
   └─ "Anda adalah asisten chatbot untuk PSB..."

2. Guardrails (System Prompt)
   ├─ HARUS menggunakan knowledge base SAJA
   ├─ TIDAK BOLEH mengubah intent
   ├─ TIDAK BOLEH menambah informasi baru
   ├─ TIDAK BOLEH menjawab di luar PSB
   └─ HARUS sopan dan ramah

3. User Prompt
   ├─ Konteks: intent, confidence score, pertanyaan user
   ├─ Knowledge Base resmi (core_facts, qa_pairs, quick_answers)
   └─ Instruksi confidence-aware (berbeda per level)

Catatan: Output adalah teks natural (bukan JSON).
```

### 6. Knowledge Base System

**Responsibility**: Single source of truth for all facts

```
Structure: knowledge_base/ directory
├─ File-based JSON (One file per intent)
├─ Schema: { "intent": "...", "description": "...", "items": [...] }
├─ Size: ~10 JSON files (see KNOWLEDGE_BASE_SCHEMA.md)
└─ Update: Manual curation (no dynamic training)

Files:
├─ biaya_pendidikan.json
├─ eskalasi_admin.json
├─ faq_umum.json
├─ info_pendaftaran.json
├─ kegiatan_harian.json
├─ kirim_dokumen.json
├─ link_formulir.json
├─ pendidikan_formal.json
├─ program_unggulan.json
├─ syarat_pendaftaran.json
```

### 7. Database (`database.py`)

**Responsibility**: Persistent logging and analytics

```
Component: SQLAlchemy ORM
├─ Engine: PostgreSQL
├─ Tables:
│  ├─ user_questions
│  │  ├─ id: Primary key
│  │  ├─ user_id: Telegram user ID
│  │  ├─ question: Original user question
│  │  ├─ intent: Predicted intent
│  │  ├─ confidence: Confidence score
│  │  ├─ response: System response
│  │  ├─ timestamp: When question was asked
│  │  └─ platform: Source platform
│  └─ (extensible for feedback, corrections, etc.)
└─ Deployment: Railway PostgreSQL
```

**Connection Methods**:
- **Production**: `DATABASE_URL` environment variable (Railway)
- **Development**: Individual env vars (DB_HOST, DB_USER, etc.)

---

## Data Flow

### Complete Request-Response Flow

```
1. USER SENDS MESSAGE (Telegram)
   └─ Text message via Telegram app

2. TELEGRAM API WEBHOOK
   └─ FastAPI receives POST /webhook

3. TELEGRAM BOT HANDLER
   ├─ Extract: chat_id, user_id, message_text, username
   └─ Pass to Response Router

4. RESPONSE ROUTER ORCHESTRATION
   │
   ├─ Step 1: Intent Classification (Guard 1)
   │  │
   │  └─ Call intent_classifier.predict()
   │     ├─ TF-IDF Vectorization
   │     ├─ Logistic Regression inference
   │     └─ Return: intent, confidence, probabilities
   │
   ├─ Step 2: Knowledge Base Loading
   │  │
   │  └─ Load {intent}.json from knowledge_base/
   │     └─ Return: KB data structure
   │
   ├─ Step 3: Groq API Call (Guard 2)
   │  │
   │  └─ Call groq_client.generate_response()
   │     ├─ Build system prompt with guardrails
   │     ├─ Add KB data to context
   │     ├─ Send to Groq API
   │     └─ Receive refined response
   │
   ├─ Step 4: Database Logging
   │  │
   │  └─ Log to user_questions table
   │     ├─ Store question, intent, confidence
   │     ├─ Store response, timestamp
   │     └─ Store user_id, platform
   │
   └─ Step 5: Return Response
      └─ ResponseResult object

5. TELEGRAM BOT RESPONSE
   ├─ Format response with markdown
   ├─ Send via sendMessage API
   └─ Handle send errors

6. USER RECEIVES MESSAGE (Telegram)
   └─ Message displayed in chat
```

### Confidence-Based Flow Control

```
High Confidence (≥ 0.70 / CONFIDENCE_THRESHOLD)
  └─ Guard 1 + KB + Guard 2 (LLM)
     └─ Jawab percaya diri

Medium Confidence (0.30 ≤ conf < 0.70)
  ├─ Guard 1 + KB + Guard 2 (LLM tetap dipanggil)
  └─ Groq menerima instruksi hati-hati berdasarkan range:
       < 0.50: disclaimer + saran konfirmasi ke admin
       0.50-0.70: jawab hati-hati + sarankan konfirmasi

Low Confidence (< 0.30)
  ├─ TIDAK memanggil KB atau Groq
  └─ Langsung fallback: "belum cukup yakin"
     + arahkan ke admin + log ke DB
```

### Error Handling Flow

```
At any step, if error occurs:
│
├─ Groq API Error
│  └─ Fall back to KB response without LLM
│
├─ KB File Not Found
│  └─ Return "I couldn't find information about..."
│
├─ Intent Classifier Error
│  └─ Return "I'm not sure about your question..."
│
└─ Database Error
   └─ Log to filesystem (fallback)
      ├─ Continue responding to user
      └─ Alert admin via logs
```

---

## Technology Stack

### Core Framework
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Server** | FastAPI | ≥0.104.0 | REST API, webhooks |
| **ASGI Server** | Uvicorn | ≥0.24.0 | Production server |
| **Async** | Python asyncio | Built-in | Async operations |

### Machine Learning
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Vectorization** | scikit-learn (TF-IDF) | ≥1.3.0 | Text to vectors |
| **Classification** | scikit-learn (LogReg) | ≥1.3.0 | Intent prediction |
| **Numerical** | NumPy | ≥1.24.0 | Array operations |
| **Math** | SciPy | ≥1.11.0 | Statistical functions |
| **Serialization** | joblib | ≥1.3.0 | Model persistence |

### API Integration
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Telegram Bot** | requests | ≥2.31.0 | HTTP calls to Telegram Bot API |
| **Groq API** | requests | ≥2.31.0 | LLM API calls (sync HTTP) |
| **httpx** | httpx | ≥0.25.0 | Ada di requirements (unused direct import) |
| **aiohttp** | aiohttp | ≥3.9.0 | Ada di requirements (unused direct import) |

### Database
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **ORM** | SQLAlchemy | ≥2.0.0 | Database abstraction |
| **Driver** | psycopg2 | ≥2.9.0 | PostgreSQL adapter |
| **Database** | PostgreSQL | 13+ | Data persistence |

### Configuration
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Environment** | python-dotenv | ≥1.0.0 | .env file loading |
| **Pydantic** | pydantic | ≥2.0.0 | Schema validation (FastAPI dep) |
| **Typing** | typing-extensions | ≥4.8.0 | Type hints |

### Development & Testing
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Testing** | pytest | ≥7.0.0 | Unit testing |
| **Fixtures** | pytest-fixtures | Built-in | Test fixtures |
| **Code Quality** | black | ≥23.0.0 | Code formatting |
| **Linting** | flake8 | ≥6.0.0 | Code linting |

---

## Design Patterns

### 1. Singleton Pattern (Component Initialization)

```python
# intent_classifier.py
_classifier_instance = None

def get_intent_classifier():
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance
```

**Purpose**: Ensure single instance of expensive-to-initialize components

### 2. Pipeline Pattern (Response Router)

```python
def process_question(self, question: str) -> ResponseResult:
    # Step 1: Intent Classification
    prediction = self.intent_classifier.predict(question)
    
    # Step 2: Knowledge Base Loading
    kb_data = self._load_knowledge_base(prediction.intent)
    
    # Step 3: LLM Reasoning
    response = self.groq_client.generate_response(...)
    
    # Step 4: Database Logging
    self._log_to_database(...)
    
    # Step 5: Return
    return ResponseResult(...)
```

**Purpose**: Orchestrate multi-step process with clear separation of concerns

### 3. Strategy Pattern (Error Handling)

```python
# Different strategies for different errors
if groq_error:
    # Strategy 1: Use KB directly without LLM
    return kb_response
elif kb_not_found:
    # Strategy 2: Use intent classifier message
    return classifier_message
elif classifier_error:
    # Strategy 3: Generic fallback
    return generic_message
```

**Purpose**: Graceful degradation with multiple fallback strategies

### 4. Factory Pattern (Configuration)

```python
# Centralized initialization
def get_response_router():
    return ResponseRouter(
        knowledge_base_dir=os.getenv("KB_DIR", "knowledge_base")
    )
```

**Purpose**: Centralized component creation and configuration

### 5. Data Class Pattern (Type Safety)

```python
@dataclass
class IntentPrediction:
    intent: str
    confidence: float
    all_probabilities: Dict[str, float]
    is_confident: bool

@dataclass
class ResponseResult:
    success: bool
    message: str
    intent: str
    confidence: float
    # ... etc
```

**Purpose**: Strong typing and data structure validation

---

## Security & Safety

### 1. Intent Guardrails

```
Guard 1: Intent Classification
  ├─ Constrain answer space to knowledge base
  ├─ Prevent model from hallucinating intents
  ├─ Provide confidence scores for validation
  └─ Fail gracefully with low-confidence fallback
```

### 2. Knowledge Base Isolation

```
Guard 2: LLM Reasoning
  ├─ System prompt enforces KB-only responses
  ├─ Strict prompt guards:
  │  ├─ Can ONLY use provided KB data
  │  ├─ CANNOT modify predicted intent
  │  ├─ CANNOT answer outside PSB domain
  │  ├─ CANNOT make up facts
  │  └─ CANNOT break character/instructions
  ├─ Low temperature (0.3) for consistency
  └─ Token limit (500) prevents long hallucinations
```

### 3. API Security

```
Telegram Integration
  ├─ HTTPS webhook (enforced by Telegram)
  ├─ Bot token validation (Telegram API)
  └─ Chat ID verification before sending

Groq API
  ├─ API key from environment (never hardcoded)
  ├─ Rate limiting (Groq's rate limits)
  └─ Timeout protection (30s timeout di requests.post)

Database
  ├─ Connection via environment variables
  ├─ Prepared statements (SQLAlchemy ORM)
  └─ No hardcoded credentials
```

### 4. Input Validation

```python
# Response Router
def process_question(self, question: str, user_id: str):
    # Validate input
    if not question or not isinstance(question, str):
        raise ValueError("Invalid question")
    
    if not user_id:
        user_id = "anonymous"
    
    # Truncate for safety
    question = question[:1000]
```

### 5. Error Handling

```
Exceptions
  ├─ Log with full traceback
  ├─ Send user-friendly message
  ├─ Don't expose internal details
  ├─ Implement circuit breaker for APIs
  └─ Monitor and alert on repeated failures
```

---

## Deployment Architecture

### Local Development

```
Developer Machine
  ├─ Python virtual environment
  ├─ PostgreSQL (SQLAlchemy; DATABASE_URL atau DB_HOST/…)
  ├─ FastAPI development server (auto-reload)
  ├─ Telegram Bot (webhook via ngrok or polling)
  └─ Environment: .env.example → .env
```

### Production (Railway)

```
Railway.app Deployment
  ├─ Runtime: Python 3.11 (dari runtime.txt)
  ├─ Build: Nixpacks (deteksi otomatis, tanpa Dockerfile)
  ├─ Dependencies: requirements.txt
  ├─ Environment: Railway environment variables
  ├─ Database: Railway PostgreSQL addon (DATABASE_URL inject otomatis)
  ├─ Server: Uvicorn via Procfile
  │    → web: uvicorn app:app --host 0.0.0.0 --port $PORT
  ├─ Port: $PORT (Railway assigns dynamically)
  └─ Webhook: WEBHOOK_URL env var → Telegram setWebhook
```

### Configuration Management

```
Environment Variables (Railway)
  ├─ TELEGRAM_BOT_TOKEN
  ├─ GROQ_API_KEY
  ├─ DATABASE_URL (auto-provided by Railway)
  ├─ LOG_LEVEL
  ├─ ENVIRONMENT (production/development)
  ├─ GROQ_MODEL
  ├─ GROQ_MAX_TOKENS
  ├─ GROQ_TEMPERATURE
  └─ (others as needed)

Files
  ├─ Procfile (web: uvicorn app:app --host 0.0.0.0 --port $PORT)
  ├─ runtime.txt (python-3.11.0)
  ├─ railway.json (Railway deployment config)
  └─ .env (local development only, never committed)
```

### Monitoring & Logging

```
Application Logging
  ├─ Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
  ├─ Level: INFO (production), DEBUG (development)
  ├─ Destination: stdout (Railway logs)
  └─ Components: Each module has logger = logging.getLogger(__name__)

Health Checks
  └─ GET /health (FastAPI liveness — cek bot_handler, db, env)

Database Monitoring
  ├─ Questions logged per day
  ├─ Intent distribution
  ├─ Confidence score trends
  └─ Error rate tracking
```

---

## Integration Points

### External APIs

```
1. Telegram Bot API
   ├─ Endpoint: https://api.telegram.org/bot{TOKEN}/
   ├─ Methods: getUpdates, sendMessage
   ├─ Mode: Webhook (production) or Polling (dev)
   └─ Authentication: Bot token

2. Groq API
   ├─ Endpoint: https://api.groq.com/openai/v1/chat/completions
   ├─ Model: llama-3.3-70b-versatile
   ├─ Auth: API key in Authorization header
   └─ Rate Limit: Depends on plan

3. PostgreSQL Database
   ├─ Connection: SQLAlchemy
   ├─ Protocol: PSQL wire protocol
   └─ URL format: postgresql://user:pass@host:port/db
```

### Internal Pipelines

```
1. Intent Classification Pipeline
   Text Input → TF-IDF → Logistic Regression → Intent Label

2. Response Generation Pipeline
   Question + Intent + KB → Groq Prompt → LLM → Response

3. Data Logging Pipeline
   Question → DB Model → SQLAlchemy Session → PostgreSQL
```

---

## Summary

The **Double Guard Architecture** provides:

✅ **Safety**: Two independent decision layers prevent hallucination  
✅ **Accuracy**: Intent classification grounds responses in reality  
✅ **Quality**: LLM refinement ensures natural language  
✅ **Maintainability**: Clear separation of concerns  
✅ **Scalability**: Instance FastAPI dapat di-scale; state percakapan tidak dipakai untuk jawaban. Logging bergantung pada PostgreSQL.  
✅ **Observability**: Comprehensive logging and database tracking  

This architecture represents a balance between the deterministic reliability of classical NLP and the language quality of modern LLMs.
