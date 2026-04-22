Decision: Tidak menggunakan RAG
Reason:
- Scope domain PSB terbatas
- Data bersifat statis
- Fokus penelitian pada NLP intent classification
Impact:
- Sistem lebih terkendali
- LLM berperan sebagai generator bahasa, bukan sumber fakta


# Model Decision Log

## Keputusan: Penambahan Multinomial Naive Bayes

Alasan:
- Multinomial Naive Bayes secara teoritis cocok untuk data teks
- Efektif pada representasi TF-IDF
- Digunakan luas pada tugas klasifikasi teks

Tujuan:
- Sebagai model pembanding terhadap Logistic Regression
- Bukan sebagai pengganti langsung tanpa evaluasi

## Keputusan: Pemilihan Model Final

Model terpilih:
- <Logistic Regression>

Dasar pemilihan:
- Hasil evaluasi kuantitatif
- Stabilitas prediksi
- Konsistensi performa pada kelas intent

