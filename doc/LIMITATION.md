# 🔮 Chatbot PSB - Limitations & Future Development

Dokumen ini menjelaskan keterbatasan teknis sistem chatbot PSB saat ini, **bukan sebagai kekurangan**, melainkan sebagai **ruang pengembangan** untuk iterasi selanjutnya.

---

## 📋 Ringkasan Keterbatasan

| Area | Status Saat Ini | Peluang Pengembangan |
|------|-----------------|---------------------|
| Bahasa | Bahasa Indonesia saja | Multi-bahasa (Arab, Inggris) |
| Platform | Telegram only | WhatsApp, Web Widget, Mobile App |
| Context | Single-turn conversation | Multi-turn dengan memory |
| Input | Teks saja | Voice, Image, Document |
| Knowledge | Static JSON files | Dynamic CMS-based KB |
| Learning | Manual retraining | Continuous learning |

---

## 🌐 1. Single Language Support

### Status Saat Ini
```
✅ Bahasa Indonesia (fully supported)
❌ Bahasa Arab
❌ Bahasa Inggris
❌ Bahasa Daerah
```

### Alasan Desain
- Target user utama adalah calon santri dan orang tua Indonesia
- Fokus pada kualitas satu bahasa terlebih dahulu
- Mengurangi kompleksitas model classification

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Multi-Language Support                                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ • Bahasa Arab untuk santri dari luar negeri                                         │
│ • Bahasa Inggris untuk international students                                       │
│ • Auto-detect language dan respond sesuai                                           │
│ • Multi-lingual Knowledge Base                                                       │
│                                                                                      │
│ Teknologi yang bisa digunakan:                                                       │
│ • Language detection (langdetect, fasttext)                                          │
│ • Multilingual embeddings (mBERT, XLM-R)                                             │
│ • Translation layer untuk KB                                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 2. Single Platform (Telegram Only)

### Status Saat Ini
```
✅ Telegram Bot (Webhook & Polling)
❌ WhatsApp Business API
❌ Website Chat Widget
❌ Mobile App Native
❌ Facebook Messenger
❌ Instagram DM
```

### Alasan Desain
- Telegram memiliki Bot API yang gratis dan mudah diimplementasi
- Tidak ada biaya per-message seperti WhatsApp Business API
- Cukup untuk MVP dan validasi konsep

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Multi-Platform Integration                                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                         │
│  │   Telegram   │     │   WhatsApp   │     │  Web Widget  │                         │
│  │     Bot      │     │   Business   │     │  (Embedded)  │                         │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘                         │
│         │                    │                    │                                  │
│         └────────────────────┴────────────────────┘                                  │
│                              │                                                       │
│                              ▼                                                       │
│                    ┌──────────────────┐                                              │
│                    │  Unified Message │                                              │
│                    │     Gateway      │                                              │
│                    └────────┬─────────┘                                              │
│                             │                                                        │
│                             ▼                                                        │
│                    ┌──────────────────┐                                              │
│                    │  Response Router │ ◄── Core logic tetap sama                   │
│                    └──────────────────┘                                              │
│                                                                                      │
│ Implementasi:                                                                        │
│ • Abstract messaging interface                                                       │
│ • Platform-specific adapters                                                         │
│ • Unified conversation storage                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💬 3. Single-Turn Conversation (No Memory)

### Status Saat Ini
```
✅ Menjawab pertanyaan individual
❌ Mengingat konteks percakapan sebelumnya
❌ Follow-up questions handling
❌ Referensi anaphora ("itu", "yang tadi")
```

### Contoh Keterbatasan
```
User: "Berapa biaya pendaftaran?"
Bot:  "Biaya pendaftaran adalah Rp 500.000..."

User: "Kalau yang bulanannya?"  ← Bot tidak tahu ini tentang biaya
Bot:  [Mungkin salah paham atau perlu klarifikasi]
```

### Alasan Desain
- Menyederhanakan arsitektur untuk MVP
- Mengurangi kompleksitas state management
- Menghemat token LLM (tidak perlu kirim history)

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Conversational Memory & Context Tracking                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│ Session-Based Memory:                                                                │
│ ┌─────────────────────────────────────────────────────────────────┐                 │
│ │ Session ID: user_12345_20260103                                 │                 │
│ │ ┌─────────────────────────────────────────────────────────────┐ │                 │
│ │ │ Turn 1: Q: "Berapa biaya pendaftaran?"                      │ │                 │
│ │ │         A: "Biaya pendaftaran Rp 500.000..."                │ │                 │
│ │ │         Intent: biaya_pendidikan                            │ │                 │
│ │ ├─────────────────────────────────────────────────────────────┤ │                 │
│ │ │ Turn 2: Q: "Kalau yang bulanannya?"                         │ │                 │
│ │ │         Context: biaya_pendidikan (inherited)               │ │                 │
│ │ │         A: "SPP bulanan adalah Rp 1.500.000..."             │ │                 │
│ │ └─────────────────────────────────────────────────────────────┘ │                 │
│ └─────────────────────────────────────────────────────────────────┘                 │
│                                                                                      │
│ Teknologi:                                                                           │
│ • Redis untuk session storage (TTL-based)                                            │
│ • Sliding window context (last N turns)                                              │
│ • Coreference resolution untuk pronouns                                              │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎤 4. Text-Only Input

### Status Saat Ini
```
✅ Pesan teks
❌ Voice message → text (Speech-to-Text)
❌ Image/foto dokumen
❌ File attachment (PDF, etc.)
❌ Location sharing
```

### Alasan Desain
- Text adalah format paling reliable untuk NLP
- Voice/image processing memerlukan infrastruktur tambahan
- Fokus pada core functionality terlebih dahulu

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Multi-Modal Input Processing                                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│ ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐               │
│ │   Teks     │    │   Voice    │    │   Image    │    │   File     │               │
│ │   Input    │    │   Message  │    │   (Foto)   │    │   (PDF)    │               │
│ └─────┬──────┘    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘               │
│       │                 │                 │                 │                        │
│       │                 ▼                 ▼                 ▼                        │
│       │          ┌────────────┐    ┌────────────┐    ┌────────────┐               │
│       │          │  Whisper   │    │   OCR /    │    │   PDF      │               │
│       │          │    STT     │    │  Vision AI │    │   Parser   │               │
│       │          └─────┬──────┘    └─────┬──────┘    └─────┬──────┘               │
│       │                │                 │                 │                        │
│       └────────────────┴────────┬────────┴─────────────────┘                        │
│                                 │                                                    │
│                                 ▼                                                    │
│                        ┌──────────────────┐                                          │
│                        │  Unified Text    │                                          │
│                        │  Processing      │                                          │
│                        └────────┬─────────┘                                          │
│                                 │                                                    │
│                                 ▼                                                    │
│                        ┌──────────────────┐                                          │
│                        │  Response Router │                                          │
│                        └──────────────────┘                                          │
│                                                                                      │
│ Use Cases:                                                                           │
│ • Voice message untuk user yang kesulitan mengetik                                   │
│ • Upload foto KTP/KK untuk verifikasi dokumen                                        │
│ • Kirim bukti transfer pembayaran                                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 5. Static Knowledge Base

### Status Saat Ini
```
✅ JSON files di folder knowledge_base/
✅ Update manual oleh developer
❌ Admin dashboard untuk edit KB
❌ Version control untuk KB changes
❌ Real-time sync dengan sumber data
```

### Alasan Desain
- Simplicty - JSON mudah dibaca dan diedit
- Version control via Git
- Tidak memerlukan database tambahan

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Dynamic Knowledge Base Management System                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│ │                         KB Admin Dashboard                                       │ │
│ │ ┌─────────────────────────────────────────────────────────────────────────────┐ │ │
│ │ │  📝 Edit Intent: biaya_pendidikan                              [Save] [↩️]  │ │ │
│ │ ├─────────────────────────────────────────────────────────────────────────────┤ │ │
│ │ │  Core Facts:                                                                │ │ │
│ │ │  ┌─────────────────────────────────────────────────────────────────────┐   │ │ │
│ │ │  │ biaya_pendaftaran: Rp 500.000 ──────────────────────── [Edit] [🗑️] │   │ │ │
│ │ │  │ spp_bulanan: Rp 1.500.000 ──────────────────────────── [Edit] [🗑️] │   │ │ │
│ │ │  │ + Add new fact ─────────────────────────────────────────────── [➕] │   │ │ │
│ │ │  └─────────────────────────────────────────────────────────────────────┘   │ │ │
│ │ └─────────────────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ Features:                                                                            │
│ • Web-based admin panel untuk staff non-teknis                                       │
│ • Audit trail untuk setiap perubahan                                                 │
│ • Preview changes sebelum publish                                                    │
│ • Rollback ke versi sebelumnya                                                       │
│ • Sync dengan sistem informasi pesantren                                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 6. Manual Model Retraining

### Status Saat Ini
```
✅ Logging questions ke database
✅ Admin labeling tool untuk koreksi intent
✅ Export training data script
❌ Automatic retraining pipeline
❌ A/B testing untuk model baru
❌ Performance monitoring dashboard
```

### Alasan Desain
- Human-in-the-loop untuk quality control
- Menghindari model drift tanpa pengawasan
- Retraining memerlukan validasi manual

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: MLOps Pipeline for Continuous Learning                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│         Production                    Training Pipeline                              │
│     ┌──────────────┐              ┌──────────────────────┐                          │
│     │   Chatbot    │              │   Model Training     │                          │
│     │   (Live)     │              │   Environment        │                          │
│     └──────┬───────┘              └──────────┬───────────┘                          │
│            │                                 │                                       │
│            ▼                                 ▼                                       │
│     ┌──────────────┐              ┌──────────────────────┐                          │
│     │   Log User   │────────────▶│   Labeled Dataset    │                          │
│     │   Questions  │   Weekly     │   (Auto-augmented)   │                          │
│     └──────────────┘   Export     └──────────┬───────────┘                          │
│                                              │                                       │
│                                              ▼                                       │
│     ┌──────────────┐              ┌──────────────────────┐                          │
│     │   A/B Test   │◀─────────────│   Train New Model    │                          │
│     │   (Shadow)   │   Deploy     │   (Automated)        │                          │
│     └──────┬───────┘              └──────────────────────┘                          │
│            │                                                                         │
│            ▼                                                                         │
│     ┌──────────────┐                                                                 │
│     │  Compare     │                                                                 │
│     │  Performance │──▶ If better ──▶ Promote to Production                         │
│     └──────────────┘                                                                 │
│                                                                                      │
│ Components:                                                                          │
│ • Automated data pipeline (Airflow/Prefect)                                          │
│ • Experiment tracking (MLflow/Weights & Biases)                                      │
│ • Model registry dengan versioning                                                   │
│ • Shadow deployment untuk A/B testing                                                │
│ • Alerting untuk model degradation                                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 7. No Semantic Search (RAG)

### Status Saat Ini
```
✅ Intent classification → Load exact KB file
❌ Semantic similarity search across KB
❌ Vector embeddings untuk documents
❌ Hybrid search (keyword + semantic)
```

### Alasan Desain Saat Ini
- Domain tertutup dengan intent yang jelas
- TF-IDF + Logistic Regression sudah cukup akurat (94%+)
- Menghindari over-engineering untuk use case sederhana
- Lebih hemat resource dan latency

### Kapan RAG Dibutuhkan?
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ RAG mungkin diperlukan jika:                                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ • Knowledge Base menjadi sangat besar (100+ dokumen)                                 │
│ • Pertanyaan user sangat variatif dan tidak bisa dikategorikan                       │
│ • Ada kebutuhan search across multiple intents                                       │
│ • User bertanya dengan bahasa yang sangat informal/slang                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Hybrid Intent Classification + RAG                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│                            USER QUESTION                                             │
│                                  │                                                   │
│                    ┌─────────────┴─────────────┐                                     │
│                    ▼                           ▼                                     │
│           ┌────────────────┐         ┌────────────────┐                             │
│           │ Intent         │         │ Vector Search  │                             │
│           │ Classifier     │         │ (Embeddings)   │                             │
│           └───────┬────────┘         └───────┬────────┘                             │
│                   │                          │                                       │
│                   ▼                          ▼                                       │
│           ┌────────────────┐         ┌────────────────┐                             │
│           │ Primary KB     │         │ Top-K Similar  │                             │
│           │ (by intent)    │         │ Chunks         │                             │
│           └───────┬────────┘         └───────┬────────┘                             │
│                   │                          │                                       │
│                   └──────────┬───────────────┘                                       │
│                              ▼                                                       │
│                    ┌────────────────┐                                                │
│                    │ Merge & Rank   │                                                │
│                    │ (Re-ranking)   │                                                │
│                    └───────┬────────┘                                                │
│                            │                                                         │
│                            ▼                                                         │
│                    ┌────────────────┐                                                │
│                    │ LLM Generate   │                                                │
│                    │ Response       │                                                │
│                    └────────────────┘                                                │
│                                                                                      │
│ Teknologi:                                                                           │
│ • Embedding model: sentence-transformers (Indonesian)                                │
│ • Vector DB: Pinecone, Weaviate, atau Qdrant                                         │
│ • Reranker: Cross-encoder untuk precision                                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 8. Limited Analytics

### Status Saat Ini
```
✅ Log setiap pertanyaan ke database
✅ Basic metrics (intent, confidence, success)
❌ Real-time analytics dashboard
❌ User journey tracking
❌ Sentiment analysis
❌ Conversion funnel (tanya → daftar)
```

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Comprehensive Analytics Dashboard                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│ │  📊 Chatbot Analytics Dashboard                              [Today ▼] [Export] │ │
│ │ ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐       │ │
│ │ │ Total Questions │ Avg Confidence  │ Success Rate    │ Unique Users    │       │ │
│ │ │     1,234       │     87.5%       │     94.2%       │      456        │       │ │
│ │ │    ↑ 12%        │    ↑ 2.3%       │    ↑ 1.5%       │    ↑ 8%         │       │ │
│ │ └─────────────────┴─────────────────┴─────────────────┴─────────────────┘       │ │
│ │                                                                                  │ │
│ │ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐         │ │
│ │ │ Intent Distribution             │ │ Hourly Traffic                  │         │ │
│ │ │ ████████████ biaya (35%)       │ │ ▁▂▃▅▇█▇▅▃▂▁▁▁▂▃▅▇█▇▅▃▂▁       │         │ │
│ │ │ ██████████ pendaftaran (30%)   │ │ 00  04  08  12  16  20  24      │         │ │
│ │ │ ██████ syarat (18%)            │ │                                  │         │ │
│ │ │ ████ program (12%)             │ │                                  │         │ │
│ │ │ ██ lainnya (5%)                │ │                                  │         │ │
│ │ └─────────────────────────────────┘ └─────────────────────────────────┘         │ │
│ │                                                                                  │ │
│ │ ┌─────────────────────────────────────────────────────────────────────┐         │ │
│ │ │ Low Confidence Questions (Needs Review)                              │         │ │
│ │ │ ┌──────────────────────────────────────────────────────────────┐    │         │ │
│ │ │ │ "gmn cara daftar online ya?" - Conf: 45% - Intent: ?         │    │         │ │
│ │ │ │ "bs cicil ga spp nya" - Conf: 38% - Intent: biaya?           │    │         │ │
│ │ │ └──────────────────────────────────────────────────────────────┘    │         │ │
│ │ └─────────────────────────────────────────────────────────────────────┘         │ │
│ └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ Metrics to Track:                                                                    │
│ • User satisfaction (thumbs up/down after response)                                  │
│ • Time to resolution                                                                 │
│ • Escalation rate to admin                                                           │
│ • Intent confusion matrix                                                            │
│ • Peak usage hours                                                                   │
│ • User retention (returning users)                                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 9. No User Authentication

### Status Saat Ini
```
✅ Track user by Telegram chat_id
❌ Persistent user profiles
❌ Registration status tracking
❌ Personalized responses
❌ Role-based access (admin vs user)
```

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: User Profile & Personalization                                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│ User Profile:                                                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│ │ User ID: telegram_12345                                                          │ │
│ │ Name: Ahmad                                                                      │ │
│ │ Status: Calon Santri                                                             │ │
│ │ Registration Progress: ▓▓▓▓▓▓▓░░░ 70%                                           │ │
│ │ ┌─────────────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ ✅ Mengisi formulir                                                          │ │ │
│ │ │ ✅ Upload dokumen                                                             │ │ │
│ │ │ ✅ Pembayaran pendaftaran                                                     │ │ │
│ │ │ ⏳ Tes seleksi (pending)                                                      │ │ │
│ │ │ ○  Pengumuman                                                                 │ │ │
│ │ └─────────────────────────────────────────────────────────────────────────────┘ │ │
│ │ Interests: [program_tahfidz] [smp]                                               │ │
│ └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│ Personalized Response:                                                               │
│ "Halo Ahmad! Berdasarkan progress pendaftaran Anda, langkah selanjutnya adalah       │
│  mengikuti tes seleksi pada tanggal 15 Januari 2026. Apakah ada yang ingin           │
│  ditanyakan tentang persiapan tes?"                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 10. Single LLM Provider

### Status Saat Ini
```
✅ Groq API (LLaMA 3.3 70B)
❌ Fallback ke provider lain
❌ Load balancing antar provider
❌ Cost optimization routing
```

### Alasan Desain
- Groq sangat cepat (lowest latency)
- Free tier cukup untuk development
- Simplicity - satu provider lebih mudah di-maintain

### Ruang Pengembangan
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FUTURE: Multi-Provider LLM Gateway                                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│      ┌─────────────────────────────────────────────────────────────────────────┐    │
│      │                         LLM Gateway                                      │    │
│      │ ┌─────────────────────────────────────────────────────────────────────┐ │    │
│      │ │ Routing Logic:                                                       │ │    │
│      │ │ • Primary: Groq (fast, cheap)                                        │ │    │
│      │ │ • Fallback 1: OpenAI GPT-4 (if Groq down)                            │ │    │
│      │ │ • Fallback 2: Anthropic Claude (if both down)                        │ │    │
│      │ │ • Local: Ollama (offline fallback)                                   │ │    │
│      │ └─────────────────────────────────────────────────────────────────────┘ │    │
│      └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│ Benefits:                                                                            │
│ • 99.9% uptime dengan multiple fallbacks                                             │
│ • Cost optimization (route simple queries ke model murah)                            │
│ • A/B testing model baru tanpa downtime                                              │
│ • Compliance (some data can only use local models)                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 Development Priority Matrix

| Fitu | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Multi-turn conversation | 🔥 High | Medium | **P1** |
| WhatsApp integration | 🔥 High | Medium | **P1** |
| Analytics dashboard | Medium | Medium | **P2** |
| KB admin panel | Medium | Medium | **P2** |
| Voice input (STT) | Medium | High | **P3** |
| Multi-language | Low | High | **P4** |
| RAG implementation | Low | High | **P4** |
| User profiles | Low | Medium | **P4** |

---

## ✅ Kesimpulan

Keterbatasan-keterbatasan di atas **bukanlah bug atau kekurangan desain**, melainkan **keputusan arsitektur yang disengaja** untuk memprioritaskan:

1. **Simplicity** - Sistem yang simple lebih mudah di-maintain
2. **Speed to Market** - MVP yang berfungsi lebih baik dari fitur sempurna yang tidak pernah selesai
3. **Scalability** - Arsitektur modular memungkinkan penambahan fitur tanpa rewrite
4. **Cost Efficiency** - Fokus resource pada fitur yang memberikan value tertinggi

Setiap keterbatasan memiliki **jalur pengembangan yang jelas** dan dapat diimplementasi sesuai kebutuhan dan prioritas bisnis.

---

*Dokumen ini diperbarui: 3 Januari 2026*
