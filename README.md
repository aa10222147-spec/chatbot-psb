# Chatbot PSB – Penerimaan Santri Baru

Project ini adalah chatbot Telegram untuk layanan penerimaan santri baru di Pondok Pesantren Gemayasih. Arsitekturnya menggunakan pola Double Guard: intent classifier sebagai pengunci konteks, lalu Groq digunakan untuk merapikan jawaban berdasarkan knowledge base yang sudah ditentukan.

## Ringkasan Proyek

- Bot berjalan di Telegram
- Request masuk diproses melalui FastAPI
- Intent diprediksi dengan TF-IDF + Logistic Regression
- Knowledge base JSON menjadi satu-satunya sumber fakta
- Groq hanya digunakan untuk menulis ulang jawaban secara formal dan santun
- PostgreSQL digunakan sebagai logging bila tersedia
- Saat confidence rendah atau Groq gagal, sistem secara aman beralih ke fallback

## Fitur Utama

- Intent classification dengan model ML yang diload dari folder `models/`
- Knowledge base per intent di folder `knowledge_base/`
- Response routing melalui `response_router.py`
- Telegram webhook dan polling mode untuk kebutuhan lokal atau produksi
- Database logging untuk pertanyaan, intent, dan confidence
- Graceful degradation untuk kondisi API atau model tidak tersedia

## Arsitektur

```text
User
  ↓
Telegram Bot API
  ↓
FastAPI app / polling bot
  ↓
telegram_bot.py
  ↓
response_router.py
  ├─ intent_classifier.py   (Guard 1: klasifikasi intent)
  ├─ knowledge_base/*.json  (single source of truth)
  ├─ groq_client.py         (Guard 2: bounded reasoning)
  └─ database.py            (logging optional)
  ↓
Response dikirim kembali ke user
```

## Struktur Folder

```text
chatbot-psb/
├── app.py                 # FastAPI webhook + health check
├── app_polling.py         # Long polling untuk dev lokal
├── telegram_bot.py        # Handler update Telegram
├── response_router.py     # Orchestrator utama
├── intent_classifier.py   # Guard 1: TF-IDF + Logistic Regression
├── groq_client.py         # Guard 2: Groq bounded reasoning
├── database.py            # Koneksi/log database PostgreSQL
├── init_database.py       # Inisialisasi tabel DB
├── admin_labeling.py      # Labeling manual untuk data training
├── export_training_data.py# Export data untuk retraining
├── generate_gd_report.py # Generate laporan / analisis
├── knowledge_base/        # Data fakta per intent
├── models/                # Model bundle terlatih
├── data/                  # Dataset dan export
├── notebooks/             # Notebook eksperimen training
├── tests/                 # Pytest coverage
├── .env.example           # Contoh konfigurasi env
├── requirements.txt        # Dependency produksi
├── requirements-dev.txt    # Dependency pengembangan/testing
├── requirements-minimal.txt
├── Procfile               # Deploy Railway
├── railway.json           # Konfigurasi Railway
├── runtime.txt            # Versi runtime Python
├── pytest.ini             # Konfigurasi pytest
├── .gitignore
├── LICENSE
├── README.md
└── .env                   # Local secret, tidak dipush
```

## Prasyarat

- Python 3.10+ (direkomendasikan 3.11)
- Telegram Bot Token dari @BotFather
- Groq API Key dari Groq Console
- PostgreSQL optional untuk logging dan admin tools

## Setup Awal

```bash
cd chatbot-psb
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit file `.env` dan isi variabel berikut:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3
WEBHOOK_URL=https://your-domain.com/webhook
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=
ALLOW_MOCK_CLASSIFIER=false
```

## Menjalankan Bot

### Mode lokal dengan polling

```bash
python app_polling.py
```

Ini cocok untuk development lokal karena bot akan polling update Telegram secara berkala.

### Mode produksi dengan webhook

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Pastikan `WEBHOOK_URL` dan environment server sudah benar saat deploy.

## Database

Jika `DATABASE_URL` tersedia, system akan mencoba inisialisasi database pada startup. Jika tidak, bot tetap dapat berjalan dengan mode degradasi.

Untuk inisialisasi tabel secara manual:

```bash
python init_database.py
```

## Endpoint Penting

- `GET /` — informasi service
- `GET /health` — health check
- `POST /webhook` — webhook Telegram
- `GET /webhook/info` — debug webhook

## Command Telegram

Bot menyediakan command berikut:

- `/start`
- `/help`
- `/status`
- `/about`

## Model dan Guardrails

Intent classifier memuat model dari `models/`. Jika bundle model valid tidak tersedia, aplikasi dapat diblokir di production agar tidak berjalan dengan prediksi yang tidak valid, kecuali `ALLOW_MOCK_CLASSIFIER=true` secara eksplisit untuk demo/development.

Groq client memiliki aturan keras:

- hanya menggunakan knowledge base
- tidak boleh menambah fakta baru
- tidak boleh mengganti intent yang sudah diprediksi
- hanya memperhalus bahasa, bukan menggantikan logika sistem

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

## Catatan Deployment

Project ini siap untuk deploy di Railway dengan `Procfile` dan `railway.json` yang sudah disediakan. Environment variable `DATABASE_URL` akan otomatis terisi saat PostgreSQL service terhubung.

## Lisensi

Project ini menggunakan lisensi MIT. Lihat file `LICENSE` untuk detail lengkap.

---

Made with care for Islamic education and operational chatbot workflows.

