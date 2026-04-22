# Outline Final Laporan
## Chatbot Penerimaan Santri Baru (PSB)

Outline ini merupakan struktur final laporan tertulis dan wajib diikuti
secara konsisten. Setiap bab memiliki tujuan akademik yang jelas dan saling
berkaitan.

---

## BAB I – Pendahuluan dan Permasalahan

### 1.1 Latar Belakang
- Konteks penggunaan chatbot dalam layanan informasi pendidikan
- Tantangan penggunaan LLM secara langsung (hallucination, kontrol jawaban)
- Kebutuhan sistem chatbot yang akurat, sopan, dan terkendali
- Relevansi NLP dalam domain Penerimaan Santri Baru (PSB)

### 1.2 Rumusan Masalah
- Permasalahan pemahaman maksud pengguna
- Permasalahan kontrol respons LLM
- Permasalahan perancangan sistem chatbot yang layak secara akademik

### 1.3 Tujuan Penelitian
- Merancang chatbot PSB berbasis NLP
- Menerapkan arsitektur Double Guard
- Mengevaluasi performa model dan sistem, serta membandingkan performa dua algoritma klasifikasi intent berbasis TF-IDF.

### 1.4 Batasan Masalah
- Domain terbatas pada informasi PSB
- Platform Telegram
- Tidak menggunakan Retrieval-Augmented Generation (RAG)
- Fokus pada intent classification dan kontrol respons LLM

---

## BAB II – Dataset

### 2.1 Sumber dan Karakteristik Dataset
- Dataset berbasis user stories
- Relevansi data dengan kebutuhan pengguna nyata

### 2.2 Struktur Dataset
- Format data
- Penjelasan kolom
- Contoh data

### 2.3 Distribusi dan Komposisi Data
- Jumlah data per intent
- Upaya menjaga keseimbangan dataset

### 2.4 Proses Pelabelan Data
- Metode labeling
- Definisi kelas intent
- Konsistensi dan validasi label
- **Catatan:** Dataset digunakan secara identik untuk kedua model (LR dan MNB) untuk menjamin _fairness_ evaluasi.

---

## BAB III – Tahapan Natural Language Processing (NLP)

### 3.1 Preprocessing Teks
- Case folding
- Pembersihan tanda baca
- Tokenisasi
- Penanganan stopword

### 3.2 Representasi Fitur (TF-IDF)
- Alasan pemilihan TF-IDF:
    - Cocok untuk algoritma Linear & Probabilistik
    - Efisien untuk teks pendek (intent)
    - Mendukung interpretabilitas model
- Penegasan bahwa representasi fitur yang sama digunakan untuk seluruh model klasifikasi.

### 3.3 Algoritma Klasifikasi Intent

#### 3.3.1 Logistic Regression (Baseline)
- Karakteristik algoritma
- Kelebihan untuk intent classification
- Digunakan sebagai model pembanding (_baseline_)

#### 3.3.2 Multinomial Naive Bayes
- Prinsip probabilistik
- Asumsi independensi fitur
- Kecocokan dengan TF-IDF dan data teks pendek

### 3.4 Skema Pelatihan dan Pengujian
- Skema _train-test split_
- Penggunaan dataset yang sama untuk kedua algoritma
- Parameter dasar tiap model (tanpa detail berlebihan)

---

## BAB IV – Arsitektur Model dan Sistem (Double Guard)

### 4.1 Konsep Arsitektur Double Guard
- Definisi dan tujuan
- Alasan penggunaan pendekatan berlapis

### 4.2 Guard Pertama: Intent Classification Model
- **Implementasi:** Menggunakan model klasifikasi intent berbasis TF-IDF dengan dua algoritma yang diuji (Logistic Regression dan Multinomial Naive Bayes).
- **Strategi:** Model dengan performa terbaik dipilih untuk sistem akhir.
- **Peran:** Filter awal untuk menentukan maksud pengguna.

### 4.3 Guard Kedua: Large Language Model (LLM)
- Peran LLM sebagai generator bahasa
- Pembatasan akses dan prompt control
- Hubungan LLM dengan hasil klasifikasi intent

### 4.4 Alur Keputusan Sistem
- Alur input hingga respons
- Kondisi eskalasi ke admin

### 4.5 Pertimbangan Tidak Menggunakan RAG
- Alasan teknis dan akademik
- Dampak terhadap sistem

---

## BAB V – Hasil dan Evaluasi

### 5.1 Evaluasi Model Logistic Regression
- Metrics: Accuracy, Precision, Recall, F1-score
- Analisis Confusion Matrix

### 5.2 Evaluasi Model Multinomial Naive Bayes
- Metrics: Accuracy, Precision, Recall, F1-score
- Analisis Confusion Matrix
- Format penyajian data disamakan dengan 5.1 untuk _fairness_.

### 5.3 Perbandingan Kinerja Model
- Tabel perbandingan langsung (Accuracy, F1-score, dll)
- Analisis stabilitas dan performa antar kelas

### 5.4 Model Terpilih untuk Sistem
- Alasan pemilihan model final (berdasarkan 5.3)
- Pertimbangan lain: Stabilitas, Interpretabilitas, Konsistensi prediksi

### 5.5 Evaluasi Sistem End-to-End
- Pengujian simulasi percakapan nyata
- Contoh kasus keberhasilan dan kegagalan

---

## BAB VI – Diskusi

### 6.1 Analisis Kinerja Sistem & Model
- Kekuatan pendekatan Double Guard
- Perbedaan karakteristik LR vs MNB dalam konteks PSB
- Dampak pemilihan model terhadap kinerja Double Guard

### 6.2 Perbandingan Konseptual
- Perbandingan dengan pendekatan LLM-only
- Diskusi singkat dengan sistem berbasis RAG
- Implikasi kesalahan klasifikasi terhadap respons bot

### 6.3 Keterbatasan Sistem
- Keterbatasan dataset
- Keterbatasan fleksibilitas respons

---

## BAB VII – Kesimpulan dan Saran

### 7.1 Kesimpulan
- Ringkasan hasil penelitian
- Dua algoritma intent berhasil dievaluasi; Kombinasi TF-IDF + model terpilih layak untuk domain PSB.
- Pencapaian tujuan penelitian dan efektivitas Double Guard.

### 7.2 Saran Pengembangan
- Pengembangan dataset
- Uji model neural (mis. IndoBERT) atau Ensemble intent classifier
- Pengembangan modul lanjutan (misalnya RAG) di masa depan

---

Outline ini merupakan struktur final dan tidak boleh diubah tanpa alasan
akademik yang jelas.
