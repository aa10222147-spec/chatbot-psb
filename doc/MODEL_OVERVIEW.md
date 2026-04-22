# Model Overview – Intent Classification

Sistem Chatbot PSB menggunakan pendekatan klasifikasi intent
berbasis TF-IDF dengan dua algoritma yang diuji:

1. Logistic Regression (LR)
2. Multinomial Naive Bayes (MNB)

Kedua model:
- Menggunakan dataset yang sama
- Menggunakan preprocessing yang sama
- Menggunakan representasi fitur TF-IDF yang sama

Tujuan penggunaan dua model:
- Membandingkan performa klasifikasi intent
- Menentukan model paling sesuai untuk sistem akhir

Model yang digunakan dalam sistem produksi (Guard 1):
- Logistice Regression

Model yang tidak digunakan dalam sistem akhir:
- Digunakan sebagai pembanding evaluasi
