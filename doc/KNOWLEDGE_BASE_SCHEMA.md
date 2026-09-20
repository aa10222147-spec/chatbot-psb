# Chatbot PSB – Knowledge Base Schema

> Single source of truth untuk fakta yang boleh disampaikan ke user.  
> Implementasi loader: `response_router.py` `_load_knowledge_base()`.  
> Formatter LLM: `groq_client.py` `_format_new_kb()` / `_format_legacy_kb()`.

---

## 1. Principles

| Principle | Rule |
|-----------|------|
| **Atomicity** | Satu intent = satu file `{intent}.json` |
| **Authority** | Fakta hanya dari KB, bukan dari LLM |
| **Consistency** | Nama file harus sama dengan label classifier |
| **Legacy** | Format lama `answers[]` masih di-wrap menjadi `qa_pairs` |

---

## 2. Directory (aktual)

```
chatbot-psb/knowledge_base/
├── info_pendaftaran.json
├── syarat_pendaftaran.json
├── biaya_pendidikan.json
├── program_unggulan.json
├── pendidikan_formal.json
├── kegiatan_harian.json
├── link_formulir.json
├── kirim_dokumen.json
├── faq_umum.json
└── eskalasi_admin.json
```

---

## 3. Production Schema

Format yang dipakai file KB saat ini:

```json
{
  "intent": "info_pendaftaran",
  "description": "Informasi jadwal dan alur pendaftaran santri baru",
  "core_facts": {
    "gelombang_1_start": "15 Januari  2026",
    "link_pendaftaran": "https://ponpesgemayasih.com/daftar"
  },
  "qa_pairs": [
    {
      "q": "Kapan pendaftaran dibuka?",
      "a": "Pendaftaran dibuka dalam 2 gelombang: ..."
    }
  ],
  "quick_answers": {
    "gelombang_1": "15 Januari 2026 - 28 Februari 2026"
  }
}
```

### Field

| Field | Type | Required | Keterangan |
|-------|------|----------|------------|
| `intent` | string | ya | Harus sama dengan stem nama file |
| `description` | string | ya | Ringkasan topik (masuk prompt sebagai TOPIK) |
| `core_facts` | object | ya | Fakta atomik (angka, tanggal, tautan, kontak) |
| `qa_pairs` | array | ya | Contoh Q&A; Groq hanya menyertakan **maksimal 5** pasangan pertama |
| `qa_pairs[].q` / `.a` | string | ya | Pertanyaan dan jawaban template |
| `quick_answers` | object | opsional | Jawaban singkat |

Loader juga menerima kunci lama `question`/`answer` pada pasangan Q&A.

---

## 4. Legacy Schema (masih didukung)

Jika file berisi `answers` (bukan `core_facts` / `qa_pairs`), router membungkusnya:

```json
{
  "intent": "faq_umum",
  "answers": [
    { "id": "faq-001", "text": "...", "tags": ["lokasi"] }
  ]
}
```

Hasil load: `{"qa_pairs": [...], "_legacy": true}`.

List JSON mentah juga di-wrap sebagai `qa_pairs`.

---

## 6. Bagaimana KB masuk ke LLM

`GroqClient._format_new_kb` merangkai teks:

1. `TOPIK:` dari `description`
2. `FAKTA INTI` dari setiap key-value `core_facts`
3. `CONTOH JAWABAN` dari 5 `qa_pairs` pertama
4. `JAWABAN SINGKAT` dari `quick_answers`

Hanya satu file intent yang dimuat per permintaan.

---

## 7. Operational Rules

- Ubah fakta di JSON, jangan di prompt.
- Intent baru membutuhkan: file KB, label di dataset, retraining, dan bundle `.pkl` baru.
- Fallback Groq (`_generate_fallback_response`) masih mengasumsikan daftar entri dengan field `text`. Format produksi adalah dict `core_facts`; jika Groq gagal, pesan fallback bisa kosong kecuali ada path legacy. Perilaku yang diharapkan: degrade ke teks KB atau arahkan ke admin.
