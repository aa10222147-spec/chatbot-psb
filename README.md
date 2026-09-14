# Chatbot PSB – Penerimaan Santri Baru

**Version:** 1.2  
**Platform:** Telegram  
**Architecture:** Double Guard (Intent Classifier + LLM Reasoning)  
**Last updated:** September 2026

Chatbot NLP untuk Penerimaan Santri Baru (PSB) Pondok Pesantren Gemayasih.  
Intent classification mengunci konteks; Groq hanya merangkai bahasa dari knowledge base JSON.

---

## Fitur Utama

- ✅ **Intent Classification** – TF-IDF + Logistic Regression (`intent_classifier.py`)
- ✅ **Knowledge Base** – JSON per intent, single source of truth (`knowledge_base/`)
- ✅ **LLM Bounded Reasoning** – Groq API, hanya merangkai bahasa (`groq_client.py`)
- ✅ **Double Guard Architecture** – mencegah hallucination
- ✅ **Telegram Bot** – webhook (produksi) & polling (dev)
- ✅ **PostgreSQL Logging** – catat pertanyaan, intent, confidence (`database.py`)
- ✅ **Admin Tools** – labeling & export dataset retraining
- ✅ **Graceful Fallback** – jika confidence rendah, KB hilang, atau Groq gagal

---

## Arsitektur

```
User → Telegram Bot API
  ↓
FastAPI webhook (app.py)  atau  polling (app_polling.py)
  ↓
telegram_bot.py
  ↓
response_router.py
  ├─ Guard 1: intent_classifier.py  (TF-IDF + Logistic Regression)
  ├─ knowledge_base/{intent}.json   (sumber fakta)
  ├─ Guard 2: groq_client.py        (bounded LLM)
  └─ database.py                    (logging, best-effort)
  ↓
Response → User
```

---

## Quick Start

### Prasyarat

- Python 3.11
- Telegram Bot Token (dari [@BotFather](https://t.me/BotFather))
- Groq API Key (dari [console.groq.com](https://console.groq.com))
- PostgreSQL (opsional — bot tetap menjawab jika DB tidak tersedia)

### Instalasi

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate         # Linux/Mac
# venv\Scripts\activate          # Windows

# 2. Install dependensi
pip install -r requirements.txt         # produksi
# pip install -r requirements-dev.txt  # + pytest, black, jupyter

# 3. Konfigurasi
cp .env.example .env
# Edit .env: isi TELEGRAM_BOT_TOKEN dan GROQ_API_KEY

# 4. (Opsional) Inisialisasi database
python init_database.py

# 5. Jalankan (development)
python app_polling.py

# atau (produksi / FastAPI dengan webhook/ngrok)
# uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Environment Variables

**Wajib:** `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`

| Variable | Default | Keterangan |
|----------|---------|------------|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model Groq |
| `GROQ_MAX_TOKENS` | `500` | |
| `GROQ_TEMPERATURE` | `0.3` | |
| `WEBHOOK_URL` | – | URL publik `/webhook` |
| `ENVIRONMENT` | `production` | `development` mengaktifkan debug endpoints |
| `DATABASE_URL` | – | PostgreSQL (Railway inject) |
| `ALLOW_MOCK_CLASSIFIER` | `false` | `true` hanya untuk demo tanpa `.pkl` |

---

## Struktur Project

```
chatbot-psb/
├── app.py                      # FastAPI: webhook, /health, debug (dev)
├── app_polling.py              # Long polling untuk localhost
├── telegram_bot.py             # Handler pesan Telegram
├── response_router.py          # Orchestrator Double Guard
├── intent_classifier.py        # Guard 1
├── groq_client.py              # Guard 2 + prompt runtime
├── database.py                 # ORM + logging PostgreSQL
├── init_database.py            # Buat tabel
├── admin_labeling.py           # Review & koreksi intent
├── export_training_data.py     # Export CSV retraining
├── utils/prompt_builder.py     # Spesifikasi prompt (tidak di-import pipeline)
├── knowledge_base/             # 11 file JSON intent
├── models/                     # Bundle v2: vectorizer_2.pkl, lr_intent_model_2.pkl, label_encoder_2.pkl
├── data/intents_v2.csv         # Dataset training (~1.066 baris)
├── notebooks/                  # Training & evaluasi
├── tests/                      # Pytest
├── Procfile / railway.json / runtime.txt
└── requirements.txt
```

---

## Perintah Bot

`/start` &nbsp; `/help` &nbsp; `/status` &nbsp; `/about`

---

## Endpoint HTTP

| Method | Path | Keterangan |
|--------|------|------------|
| `GET` | `/` | Info layanan |
| `GET` | `/health` | Health check (Railway) |
| `POST` | `/webhook` | Update Telegram |
| `GET` | `/webhook/info` | Debug webhook |
| `GET/POST` | `/debug/*` | Hanya `ENVIRONMENT=development` |

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Dokumentasi Lengkap

Semua dokumentasi teknis ada di folder [`doc/`](doc/):

| Dokumen | Isi |
|---------|-----|
| [DOCUMENTATION_INDEX.md](doc/DOCUMENTATION_INDEX.md) | Indeks & navigasi |
| [QUICK_START.md](doc/QUICK_START.md) | Setup 5 menit |
| [ARCHITECTURE.md](doc/ARCHITECTURE.md) | Diagram arsitektur |
| [SYSTEM_OVERVIEW.md](doc/SYSTEM_OVERVIEW.md) | Overview sistem |
| [COMPONENTS.md](doc/COMPONENTS.md) | Referensi komponen |
| [API_REFERENCE.md](doc/API_REFERENCE.md) | Endpoint REST |
| [DEPLOYMENT_GUIDE.md](doc/DEPLOYMENT_GUIDE.md) | Deploy ke Railway |
| [DEVELOPMENT_GUIDE.md](doc/DEVELOPMENT_GUIDE.md) | Panduan developer |
| [TROUBLESHOOTING.md](doc/TROUBLESHOOTING.md) | Pemecahan masalah |
| [NLP_PIPELINE.md](doc/NLP_PIPELINE.md) | Pipeline NLP detail |
| [MODEL_EVALUATION.md](doc/MODEL_EVALUATION.md) | Hasil evaluasi model |
| [KNOWLEDGE_BASE_SCHEMA.md](doc/KNOWLEDGE_BASE_SCHEMA.md) | Skema KB JSON |
| [PROMPT_GUARD.md](doc/PROMPT_GUARD.md) | Guardrail LLM |
| [DATASET_DESCRIPTION.md](doc/DATASET_DESCRIPTION.md) | Deskripsi dataset |
| [OUTLINE_FINAL.md](doc/OUTLINE_FINAL.md) | Outline laporan skripsi |
| [WRITING_GUIDELINE.md](doc/WRITING_GUIDELINE.md) | Panduan penulisan |
| [DECISION_LOG.md](doc/DECISION_LOG.md) | Log keputusan desain |

---

*Made with ❤️ for Islamic Education*
