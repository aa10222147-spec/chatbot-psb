# 📚 Chatbot PSB – Documentation Index

Panduan navigasi lengkap semua dokumentasi teknis sistem Chatbot PSB.

> **Sumber tunggal dokumentasi:** folder `chatbot-psb/doc/`  
> Folder `Doc/` (root workspace) sudah tidak aktif.

---

## 🚀 Quick Navigation

### Mulai dari Sini
- **[Quick Start Guide](QUICK_START.md)** — Setup dan jalankan dalam 5 menit
  - Instalasi, konfigurasi, testing, webhook Telegram

### 🏗️ Arsitektur & Desain
- **[System Overview](SYSTEM_OVERVIEW.md)** — Gambaran umum sistem, tujuan, komponen utama
- **[Architecture Guide](ARCHITECTURE.md)** — Diagram arsitektur lengkap (Mermaid), alur request, dependency
- **[Components Reference](COMPONENTS.md)** — Dokumentasi detail tiap komponen Python
- **[Data Flow Diagrams](DATA_FLOW.md)** — Diagram visual alur data
- **[System Flow](SYSTEM_FLOW.md)** — Alur sistem end-to-end lengkap

### 📡 API & Integrasi
- **[API Reference](API_REFERENCE.md)** — Dokumentasi REST API (endpoint, format, error codes)

### 🚀 Deployment & Operasi
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** — Deploy ke Railway, konfigurasi, monitoring

### 🛠️ Pengembangan
- **[Development Guide](DEVELOPMENT_GUIDE.md)** — Setup dev, standar kode, testing, debugging
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** — Pemecahan masalah umum

### 🤖 NLP & Model
- **[NLP Pipeline](NLP_PIPELINE.md)** — Pipeline klasifikasi intent: preprocessing, TF-IDF, LR, MNB
- **[Model Evaluation](MODEL_EVALUATION.md)** — Hasil evaluasi Logistic Regression vs Naive Bayes
- **[Dataset Description](DATASET_DESCRIPTION.md)** — Deskripsi dataset, distribusi intent, labeling

### 📋 Knowledge Base & LLM
- **[Knowledge Base Schema](KNOWLEDGE_BASE_SCHEMA.md)** — Skema JSON KB, field, legacy support
- **[Prompt Guardrails](PROMPT_GUARD.md)** — Aturan prompt Groq, allowed/forbidden, confidence strategy

### 📝 Laporan & Panduan Penulisan
- **[Outline Final](OUTLINE_FINAL.md)** — Struktur laporan skripsi (BAB I–VII)
- **[Writing Guideline](WRITING_GUIDELINE.md)** — Panduan gaya penulisan akademik
- **[Decision Log](DECISION_LOG.md)** — Catatan keputusan desain (tidak pakai RAG, pemilihan model)

---

## 📖 Navigasi Berdasarkan Use Case

### "Saya ingin setup bot secara lokal"
1. [Quick Start Guide](QUICK_START.md)
2. [Troubleshooting Guide](TROUBLESHOOTING.md) jika ada masalah

### "Saya ingin memahami cara kerja sistem"
1. [System Overview](SYSTEM_OVERVIEW.md) — gambaran besar
2. [Architecture Guide](ARCHITECTURE.md) — desain lengkap
3. [Data Flow Diagrams](DATA_FLOW.md) — visual alur data
4. [Components Reference](COMPONENTS.md) — detail per komponen

### "Saya ingin integrasi dengan API"
1. [API Reference](API_REFERENCE.md)
2. [Deployment Guide](DEPLOYMENT_GUIDE.md) — untuk mengetahui URL deployment

### "Saya ingin deploy ke produksi"
1. [Deployment Guide](DEPLOYMENT_GUIDE.md)
2. [Architecture Guide](ARCHITECTURE.md) — seksi deployment
3. [Troubleshooting Guide](TROUBLESHOOTING.md) — deployment issues

### "Saya ingin mengembangkan fitur"
1. [Quick Start Guide](QUICK_START.md) — setup lokal
2. [Development Guide](DEVELOPMENT_GUIDE.md)
3. [Components Reference](COMPONENTS.md) — referensi API komponen
4. [Troubleshooting Guide](TROUBLESHOOTING.md)

### "Saya ingin memahami NLP/model"
1. [NLP Pipeline](NLP_PIPELINE.md) — pipeline lengkap
2. [Model Evaluation](MODEL_EVALUATION.md) — hasil evaluasi LR vs MNB
3. [Dataset Description](DATASET_DESCRIPTION.md) — data training

### "Ada yang rusak"
1. [Troubleshooting Guide](TROUBLESHOOTING.md)
2. [Deployment Guide](DEPLOYMENT_GUIDE.md) — jika masalah deployment

---

## 🎓 Learning Path Berdasarkan Peran

### Pengguna Bot
- Langsung pakai di Telegram 😊

### Administrator Bot
1. [Quick Start Guide](QUICK_START.md)
2. [Troubleshooting Guide](TROUBLESHOOTING.md)
3. [Knowledge Base Schema](KNOWLEDGE_BASE_SCHEMA.md) — update konten KB
4. [Deployment Guide](DEPLOYMENT_GUIDE.md) — monitoring

### DevOps / System Administrator
1. [Architecture Guide](ARCHITECTURE.md)
2. [Deployment Guide](DEPLOYMENT_GUIDE.md)
3. [Troubleshooting Guide](TROUBLESHOOTING.md)

### Backend Developer
1. [Quick Start Guide](QUICK_START.md)
2. [System Overview](SYSTEM_OVERVIEW.md)
3. [Architecture Guide](ARCHITECTURE.md)
4. [Components Reference](COMPONENTS.md)
5. [Development Guide](DEVELOPMENT_GUIDE.md)
6. [API Reference](API_REFERENCE.md)

### Data Scientist / ML Engineer
1. [NLP Pipeline](NLP_PIPELINE.md)
2. [Model Evaluation](MODEL_EVALUATION.md)
3. [Dataset Description](DATASET_DESCRIPTION.md)
4. [Development Guide](DEVELOPMENT_GUIDE.md) — seksi retraining
5. Jupyter notebook di `notebooks/`

### Reviewer Skripsi / Akademik
1. [Outline Final](OUTLINE_FINAL.md)
2. [Writing Guideline](WRITING_GUIDELINE.md)
3. [System Overview](SYSTEM_OVERVIEW.md)
4. [NLP Pipeline](NLP_PIPELINE.md)
5. [Model Evaluation](MODEL_EVALUATION.md)

---

## 📁 Struktur Folder `doc/`

```
chatbot-psb/doc/
├── DOCUMENTATION_INDEX.md      ← File ini — navigasi utama
│
├── Arsitektur & Desain
│   ├── SYSTEM_OVERVIEW.md      ← Overview sistem (Sep 2026)
│   ├── ARCHITECTURE.md         ← Diagram Mermaid arsitektur
│   ├── COMPONENTS.md           ← Referensi komponen Python
│   ├── DATA_FLOW.md            ← Diagram alur data
│   └── SYSTEM_FLOW.md          ← Alur sistem end-to-end
│
├── API & Integrasi
│   └── API_REFERENCE.md        ← REST API docs
│
├── Deployment & Operasi
│   ├── DEPLOYMENT_GUIDE.md     ← Railway, monitoring
│   ├── QUICK_START.md          ← 5-menit setup
│   └── TROUBLESHOOTING.md      ← Pemecahan masalah
│
├── Pengembangan
│   └── DEVELOPMENT_GUIDE.md    ← Contributing, kode standar
│
├── NLP & Model
│   ├── NLP_PIPELINE.md         ← Pipeline klasifikasi intent
│   ├── MODEL_EVALUATION.md     ← Evaluasi LR vs MNB
│   └── DATASET_DESCRIPTION.md ← Dataset training
│
├── Knowledge Base & LLM
│   ├── KNOWLEDGE_BASE_SCHEMA.md ← Skema JSON KB
│   └── PROMPT_GUARD.md          ← Guardrail prompt Groq
│
└── Laporan & Panduan
    ├── OUTLINE_FINAL.md        ← Outline skripsi (BAB I–VII)
    ├── WRITING_GUIDELINE.md    ← Panduan penulisan akademik
    └── DECISION_LOG.md         ← Keputusan desain
```

---

## ⚡ Quick Reference

### Environment Variables

```bash
# WAJIB
TELEGRAM_BOT_TOKEN=...
GROQ_API_KEY=...

# OPSIONAL (ada default)
LOG_LEVEL=INFO
ENVIRONMENT=production           # atau development
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3
DATABASE_URL=...                 # PostgreSQL (Railway inject)
ALLOW_MOCK_CLASSIFIER=false      # true hanya untuk demo
```

### Perintah Umum

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Development
python app_polling.py            # polling lokal
pytest tests/ -v
black .
flake8 .

# Database & Training
python init_database.py
python export_training_data.py
python admin_labeling.py

# Produksi
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### File Kunci

| File | Fungsi |
|------|--------|
| `app.py` | FastAPI entry point (webhook) |
| `app_polling.py` | Long polling (dev) |
| `response_router.py` | Orchestrator Double Guard |
| `intent_classifier.py` | Guard 1 — klasifikasi intent |
| `groq_client.py` | Guard 2 — bounded LLM |
| `database.py` | PostgreSQL logging |
| `telegram_bot.py` | Handler Telegram |
| `knowledge_base/` | 11 file JSON (sumber fakta) |
| `models/` | Bundle v2: `vectorizer_2.pkl`, `lr_intent_model_2.pkl`, `label_encoder_2.pkl` |

---

### Konsep Kunci

**Double Guard Architecture**
- Guard 1 (Intent Classifier): ML klasik, menentukan ruang jawaban
- Guard 2 (Groq LLM): hanya merangkai bahasa, tidak mengubah fakta
- Mengapa? Mencegah hallucination sambil mempertahankan kualitas bahasa

**Confidence Policy**
- `< 0.30` → fallback tanpa LLM
- `0.30–<0.70` → KB + Groq dengan instruksi hati-hati
- `≥ 0.70` → alur normal

**Knowledge Base**
- Satu-satunya sumber fakta, file JSON per intent
- Tidak pernah berubah saat percakapan berlangsung
- Ubah fakta di JSON, bukan di prompt

---

**Mulai dari [Quick Start Guide](QUICK_START.md) atau [System Overview](SYSTEM_OVERVIEW.md).**

*Last Updated: September 2026*
