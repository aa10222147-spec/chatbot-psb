# Chatbot PSB - Penerimaan Santri Baru

**Version:** 1.2  
**Platform:** Telegram  
**Architecture:** Double Guard (Intent Classifier + LLM Reasoning)  
**Last aligned with code:** September 2026

Chatbot NLP untuk Penerimaan Santri Baru Pondok Pesantren Gemayasih. Intent classification mengunci konteks; Groq hanya merangkai bahasa dari knowledge base JSON.

Dokumentasi folder ini menjelaskan implementasi di root `chatbot-psb/`. Ini adalah satu-satunya lokasi dokumentasi teknis yang aktif.

---

## Fitur yang benar-benar ada di kode

- Intent classification: TF-IDF + Logistic Regression (`intent_classifier.py`)
- Knowledge base JSON, 11 intent (`knowledge_base/`)
- Groq API bounded reasoning (`groq_client.py`)
- Telegram via HTTP `requests` (`telegram_bot.py`)
- Webhook FastAPI (`app.py`) dan polling lokal (`app_polling.py`)
- PostgreSQL logging (`database.py`) — **bukan** sistem tanpa database
- Admin labeling & export dataset (`admin_labeling.py`, `export_training_data.py`)
- Fallback jika confidence `< 0.30`, KB hilang, atau Groq gagal

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
  ├─ Guard 1: intent_classifier.py
  ├─ knowledge_base/{intent}.json
  ├─ Guard 2: groq_client.py
  └─ database.py (log, best-effort)
  ↓
Response → User
```

**Lapisan kontrol:** classifier (konteks) → skema KB (fakta) → prompt Groq (perilaku) → policy confidence (routing).

---

## Instalasi singkat

Prasyarat: Python 3.10+ (Railway memakai 3.11), token Telegram, kunci Groq, PostgreSQL untuk logging (opsional agar bot tetap menjawab).

```bash
cd chatbot-psb
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt          # production
# pip install -r requirements-dev.txt    # + pytest, black, jupyter
cp .env.example .env                     # isi token & API key
python init_database.py                  # jika PostgreSQL tersedia
python app_polling.py                    # dev tanpa URL publik
# atau: python app.py                    # FastAPI + webhook/ngrok
```

Produksi: `uvicorn app:app --host 0.0.0.0 --port $PORT` (lihat `Procfile`, `railway.json`).

---

## Environment

Wajib: `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`.

Opsional: `GROQ_MODEL` (default `llama-3.3-70b-versatile`), `GROQ_MAX_TOKENS`, `GROQ_TEMPERATURE`, `WEBHOOK_URL`, `HOST`, `PORT`, `ENVIRONMENT`, `LOG_LEVEL`, `DATABASE_URL` atau `DB_*`, `ALLOW_MOCK_CLASSIFIER`.

---

## Struktur project (aktual)

```
chatbot-psb/
├── app.py
├── app_polling.py
├── telegram_bot.py
├── response_router.py
├── intent_classifier.py
├── groq_client.py
├── database.py
├── init_database.py
├── admin_labeling.py
├── export_training_data.py
├── utils/prompt_builder.py      # tidak di-import pipeline
├── knowledge_base/              # 11 JSON
├── models/                      # v2: vectorizer_2.pkl, lr_intent_model_2.pkl, label_encoder_2.pkl
├── data/intents_v2.csv
├── notebooks/
├── tests/                       # pytest; folder di-.gitignore
├── requirements.txt
├── Procfile
├── railway.json
└── runtime.txt                  # python-3.11
```

Tidak ada Dockerfile di repo saat ini.

---

## Perintah bot

`/start` `/help` `/status` `/about`

---

## Endpoint HTTP

- `GET /` — info layanan
- `GET /health` — healthcheck Railway
- `POST /webhook` — update Telegram
- `GET /webhook/info` — debug webhook
- `/debug/*` — hanya jika `ENVIRONMENT=development`

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Indeks dokumen

Mulai dari [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) untuk navigasi lengkap semua dokumentasi.

> **Catatan:** Folder `Doc/` di root workspace sudah tidak aktif. Semua dokumentasi ada di folder ini (`chatbot-psb/doc/`).
