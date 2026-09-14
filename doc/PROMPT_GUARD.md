# Chatbot PSB – Prompt Guardrails

**Version:** 1.2  
**Last Updated:** September 2026  

Dokumen ini adalah kontrak perilaku LLM. **Prompt yang benar-benar dikirim ke Groq** diimplementasikan di `chatbot-psb/groq_client.py`. Modul `utils/prompt_builder.py` berisi spesifikasi serupa tetapi **tidak dipakai** pipeline produksi (tidak ada import).

---

## 1. LLM Role

LLM = **bounded reasoning dan language refinement**.

Bukan primary decision maker, bukan pemilih intent, bukan sumber fakta baru.

---

## 2. Mandatory Input

Setiap pemanggilan Groq menerima:

- Pertanyaan user
- Intent prediksi
- Confidence score
- Isi satu file KB intent tersebut

Tidak boleh: query mentah tanpa klasifikasi, multi-intent, atau gabungan beberapa file KB.

---

## 3. Runtime System Prompt (`groq_client.py`)

Ringkasan aturan yang dikirim (Bahasa Indonesia):

1. Hanya gunakan informasi dari Knowledge Base
2. Jangan menambah informasi atau asumsi
3. Jangan mengubah intent
4. Hanya perbaiki bahasa agar natural dan sopan
5. Jika fakta tidak ada di KB, katakan jujur
6. Jawab hanya topik PSB pondok
7. Jika di luar topik, arahkan ke admin
8. Pertahankan angka dan persyaratan persis seperti KB

---

## 4. Runtime User Prompt

Struktur:

```
INFORMASI KONTEKS:
- Intent yang diprediksi: {intent}
- Confidence score: {confidence}
- Pertanyaan user: "{question}"

KNOWLEDGE BASE RESMI:
{formatted_kb}

{confidence_instruction}

TUGAS ANDA:
- Jawab berdasarkan Knowledge Base
- Gunakan HANYA informasi di Knowledge Base
- Pertahankan angka dan detail PERSIS
```

### Confidence instruction (GroqClient)

| Confidence | Instruksi ke LLM |
|------------|------------------|
| `< 0.50` | Cek relevansi vs intent; jika relevan: disclaimer + jawab KB + sarankan admin; jika tidak relevan: arahkan admin tanpa detail |
| `0.50`–`< 0.70` | Jawab hati-hati, pertimbangkan konfirmasi admin |
| `≥ 0.70` | Jawab percaya diri dari KB |

Router **tidak memanggil Groq** jika confidence `< 0.30`. Bandingkan dengan `PromptBuilder` yang punya ambang 0.3 / 0.5 / 0.7 tetapi tidak aktif di runtime.

---

## 5. Allowed / Forbidden

**Boleh:** merangkai ulang, nada sopan, disclaimer, sarankan admin.

**Dilarang:** angka/tanggal/syarat baru, menggabung intent lain, chat bebas, mengganti intent, mengisi fakta yang tidak ada.

---

## 6. API Call Parameters

Dari environment / default:

- `GROQ_MODEL` default `llama-3.3-70b-versatile`
- `temperature` default `0.3`
- `max_tokens` default `500`
- `top_p` `0.9`
- timeout HTTP 30 detik

---

## 7. Relationship

1. Intent model → kontrol konteks  
2. KB schema → kontrol fakta  
3. Prompt di `groq_client.py` → kontrol perilaku LLM  

Jika kode dan dokumen ini berbeda, **kode `groq_client.py` yang berlaku**.
