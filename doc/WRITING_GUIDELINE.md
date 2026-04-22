# Writing Guideline
## Laporan Chatbot Penerimaan Santri Baru (PSB)

Dokumen ini berisi pedoman penulisan laporan akademik untuk sistem Chatbot
Penerimaan Santri Baru (PSB). Pedoman ini wajib diikuti oleh seluruh penulis
(manusia maupun AI agent) agar laporan konsisten, ilmiah, dan dapat
dipertanggungjawabkan secara akademik.

---

## 1. Gaya Bahasa dan Nada Penulisan

- Gunakan **bahasa Indonesia formal dan akademik**
- Hindari bahasa percakapan, promosi, atau opini subjektif
- Gunakan kalimat deklaratif dan informatif
- Hindari kata-kata emosional seperti:
  - “sangat canggih”
  - “luar biasa”
  - “paling efektif”

Contoh yang benar:
> Sistem dirancang untuk membatasi akses LLM agar respons tetap terkendali.

Contoh yang salah:
> Sistem ini sangat canggih dan mampu menjawab semua pertanyaan dengan sempurna.

---

## 2. Sudut Pandang Penulisan

- Gunakan **orang ketiga** atau bentuk pasif
- Hindari penggunaan kata:
  - “kami”
  - “saya”
  - “penulis” (kecuali pada metodologi jika diperlukan)

Contoh yang dianjurkan:
> Penelitian ini bertujuan untuk merancang chatbot berbasis NLP dengan kontrol berlapis.

---

## 3. Konsistensi Terminologi

Gunakan istilah berikut secara konsisten di seluruh dokumen:

| Istilah Resmi | Keterangan |
|---------------|------------|
| Intent Classification Model | Model NLP untuk klasifikasi maksud pengguna |
| Confidence Score | Nilai probabilitas prediksi intent |
| Large Language Model (LLM) | Model generatif bahasa |
| Double Guard Architecture | Arsitektur dua lapis: model intent + LLM |
| Eskalasi Admin | Pengalihan ke admin manusia |
| Chatbot PSB | Chatbot Penerimaan Santri Baru |

⚠️ Jangan mengganti istilah dengan sinonim tidak resmi.

---

## 4. Aturan Khusus Arsitektur Sistem

- Sistem **WAJIB** dijelaskan sebagai:
  > Arsitektur Double Guard (Intent Classification + LLM)

- DILARANG:
  - Menyebut atau menjelaskan RAG sebagai bagian sistem
  - Menambahkan vector database, embedding retrieval, atau knowledge retriever

Jika RAG disebut, hanya boleh dalam konteks:
- Perbandingan
- Diskusi
- Saran pengembangan di masa depan

---

## 5. Penulisan Metodologi dan Teknis

- Jelaskan proses secara **deskriptif dan sistematis**
- Hindari pseudo-code berlebihan
- Diagram boleh dijelaskan secara naratif

Contoh:
> Setelah teks diproses melalui tahapan preprocessing, data direpresentasikan
menggunakan metode TF-IDF sebelum diklasifikasikan oleh model logistik regresi.

---

## 6. Penulisan Hasil dan Evaluasi

- Setiap metrik harus:
  - Dijelaskan maknanya
  - Diinterpretasikan dampaknya
- Hindari hanya menampilkan angka tanpa analisis

Contoh yang benar:
> Nilai F1-score menunjukkan bahwa model mampu menjaga keseimbangan antara
precision dan recall pada sebagian besar kelas intent.

---

## 7. Larangan Halusinasi Informasi

Penulis **TIDAK DIPERBOLEHKAN**:
- Menambahkan fitur yang tidak ada
- Mengasumsikan data yang tidak disebutkan
- Mengklaim performa tanpa dasar evaluasi

Jika informasi tidak tersedia, tuliskan sebagai:
> Keterbatasan sistem pada penelitian ini adalah …

---

## 8. Tujuan Akhir Penulisan

Laporan harus mencerminkan bahwa:
- Sistem dibangun dengan pendekatan ilmiah
- Keputusan desain dibuat secara sadar
- Penulis memahami trade-off arsitektur
- Sistem layak dievaluasi secara akademik

Dokumen ini bersifat **mengikat** bagi seluruh proses penulisan laporan.
