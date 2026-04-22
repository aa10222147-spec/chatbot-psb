# Chatbot PSB - Penerimaan Santri Baru

**Version:** 1.0.0  
**Platform:** Telegram  
**Architecture:** Double Guard (Intent Classifier + LLM Reasoning)

Chatbot berbasis NLP untuk Penerimaan Santri Baru (PSB) Pondok Pesantren menggunakan Intent Classification dan bounded LLM reasoning.

---

## 📋 Fitur Utama

- ✅ **Intent Classification**: TF-IDF + Logistic Regression
- ✅ **Knowledge Base**: File-based JSON (Single Source of Truth)
- ✅ **LLM Integration**: Groq API untuk bounded reasoning
- ✅ **Double Guard Architecture**: Mencegah hallucination
- ✅ **Telegram Bot**: Interface user-friendly
- ✅ **Stateless Design**: Tanpa database persistence
- ✅ **Production-Ready**: Logging, error handling, monitoring

---

## 🏗️ Arsitektur

```
User → Telegram Bot API
  ↓
FastAPI Backend (app.py)
  ↓
Intent Classifier (Guard 1) ← PRIMARY DECISION MAKER
  ↓
Knowledge Base (JSON files)
  ↓
Groq API (Guard 2) ← BOUNDED REASONING
  ↓
Response → User
```

**Control Layers:**
1. **Intent Classifier** → Context control
2. **Knowledge Base Schema** → Factual control
3. **Prompt Guard** → LLM behavior control

---

## 📦 Instalasi

### Prerequisites

- Python 3.10 atau lebih tinggi
- Telegram Bot Token (dari [@BotFather](https://t.me/BotFather))
- Groq API Key (dari [console.groq.com](https://console.groq.com))

### Quick Start

1. **Clone repository**
```bash
cd chatbot-psb
```

2. **Setup Python virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
# Production
pip install -r requirements.txt

# Development (includes testing tools)
pip install -r requirements-dev.txt

# Minimal (core only)
pip install -r requirements-minimal.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env dengan credentials Anda
```

5. **Setup Knowledge Base**
```bash
# Isi file JSON di folder knowledge_base/
# Format: sesuai doc/KNOWLEDGE_BASE_SCHEMA.md
```

6. **Run application**
```bash
# Development
python app.py

# Production
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## ⚙️ Konfigurasi

### Environment Variables (.env)

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Groq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3

# Webhook (for deployment)
WEBHOOK_URL=https://your-app-url.com/webhook

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production  # or development
```

---

## 📁 Struktur Project

```
chatbot-psb/
├── app.py                      # Entry point & FastAPI webhook
├── telegram_bot.py             # Telegram message handler
├── response_router.py          # Core decision & routing logic
├── intent_classifier.py        # NLP model inference
├── groq_client.py              # Groq API client
├── utils/
│   └── prompt_builder.py       # Prompt construction with guardrails
├── models/
│   ├── intent_model.pkl        # Trained intent classifier
│   ├── vectorizer.pkl          # TF-IDF vectorizer
│   └── label_encoder.pkl       # Label encoder
├── knowledge_base/
│   ├── info_pendaftaran.json
│   ├── syarat_pendaftaran.json
│   ├── biaya_pendidikan.json
│   └── faq_umum.json
├── requirements.txt            # Python dependencies
├── requirements-minimal.txt    # Minimal dependencies
├── requirements-dev.txt        # Development dependencies
└── .env.example                # Environment template
```

---

## 🚀 Deployment

### Railway / Render

1. Push code ke GitHub
2. Connect repository di Railway/Render
3. Set environment variables
4. Deploy!

### Docker (Coming Soon)

```bash
docker build -t chatbot-psb .
docker run -p 8000:8000 --env-file .env chatbot-psb
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=.

# Specific test
pytest tests/test_intent_classifier.py
```

---

## 📚 Dokumentasi

Lihat folder `doc/` untuk dokumentasi lengkap:

- `SYSTEM_OVERVIEW.md` - Arsitektur sistem
- `ARCHITECTURE.md` - Diagram arsitektur
- `KNOWLEDGE_BASE_SCHEMA.md` - Schema knowledge base
- `PROMPT_GUARD.md` - Guardrails LLM
- `PRD & ARSITEKTUR TEKNIS.md` - Requirements teknis

---

## 🔧 Development

### Setup Development Environment

```bash
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

---

## 📞 Bot Commands

- `/start` - Pesan selamat datang
- `/help` - Bantuan penggunaan
- `/status` - Status sistem
- `/about` - Tentang chatbot

---

## 🔒 Keamanan

- ✅ Tidak ada hallucination LLM (bounded reasoning)
- ✅ Knowledge base sebagai satu-satunya sumber fakta
- ✅ Intent classification sebagai primary decision maker
- ✅ Prompt guardrails ketat
- ✅ Error handling lengkap

---

## 📊 Monitoring

### Health Check Endpoints

- `GET /` - System info
- `GET /health` - Health status
- `GET /webhook/info` - Webhook config

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📝 License

[Specify your license here]

---

## 👥 Tim Pengembang

Tim IT Pondok Pesantren

---

## 📧 Kontak

Untuk informasi lebih lanjut, hubungi:
- Email: info@pesantren.example.com
- Telegram: [@admin_pesantren](https://t.me/admin_pesantren)

---

**Made with ❤️ for Islamic Education**
