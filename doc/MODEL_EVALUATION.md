# Model Evaluation

Dokumentasi ini berisi hasil evaluasi performa model Intent Classification untuk Chatbot Penerimaan Santri Pondok Pesantren. Model yang dievaluasi adalah **Logistic Regression** dan **Multinomial Naive Bayes**, keduanya menggunakan TF-IDF sebagai feature extraction.

---

## Evaluasi Logistic Regression

### Metrik Keseluruhan
| Metrik | Nilai |
|--------|-------|
| **Accuracy** | **91.55%** |
| **Macro Avg Precision** | 94% |
| **Macro Avg Recall** | 90% |
| **Macro Avg F1-Score** | 91% |
| **Weighted Avg F1-Score** | 92% |

### Per-Intent Performance

| Intent | Precision | Recall | F1-Score | Support |
|--------|-----------|--------|----------|---------|
| `biaya_pendidikan` | **1.00** | **1.00** | **1.00** | 20 |
| `eskalasi_admin` | 0.94 | 0.89 | 0.92 | 19 |
| `faq_umum` | 0.67 | 0.92 | 0.77 | 24 |
| `info_pendaftaran` | **1.00** | 0.95 | 0.97 | 20 |
| `kegiatan_harian` | **1.00** | 0.90 | 0.95 | 20 |
| `kirim_dokumen` | **1.00** | 0.95 | 0.97 | 19 |
| `link_formulir` | **1.00** | **1.00** | **1.00** | 20 |
| `pendidikan_formal` | 0.89 | 0.85 | 0.87 | 20 |
| `program_unggulan` | 0.91 | 0.95 | 0.93 | 21 |
| `syarat_pendaftaran` | 0.90 | 0.95 | 0.93 | 20 |

### Catatan Performa

**Kekuatan:**
- Model sangat baik dalam memprediksi intent yang berkaitan dengan biaya dan link formulir
- 2 intent mencapai **perfect F1-score 100%** (`biaya_pendidikan`, `link_formulir`)

**Kelemahan:**
- `faq_umum` memiliki precision terendah (67%), menandakan banyak false positive

---

## Evaluasi Multinomial Naive Bayes

### Metrik Keseluruhan
| Metrik | Nilai |
|--------|-------|
| **Accuracy** | **89.67%** |
| **Macro Avg Precision** | 92% |
| **Macro Avg Recall** | 87% |
| **Macro Avg F1-Score** | 87% |
| **Weighted Avg F1-Score** | 89% |

### Per-Intent Performance

| Intent | Precision | Recall | F1-Score | Support |
|--------|-----------|--------|----------|---------|
| `biaya_pendidikan` | 0.91 | **1.00** | 0.95 | 20 |
| `eskalasi_admin` | 0.82 | 0.95 | 0.88 | 19 |
| `faq_umum` | 0.79 | 0.92 | 0.85 | 24 |
| `info_pendaftaran` | **1.00** | 0.75 | 0.86 | 20 |
| `kegiatan_harian` | **1.00** | 0.85 | 0.92 | 20 |
| `kirim_dokumen` | 0.95 | **1.00** | 0.97 | 19 |
| `link_formulir` | 0.95 | **1.00** | 0.98 | 20 |
| `pendidikan_formal` | 0.89 | 0.85 | 0.87 | 20 |
| `program_unggulan` | 0.81 | **1.00** | 0.89 | 21 |
| `syarat_pendaftaran` | 0.95 | 0.95 | 0.95 | 20 |

### Catatan Performa

**Kekuatan:**
- 4 intent mencapai **recall 100%** (`biaya_pendidikan`, `kirim_dokumen`, `link_formulir`, `program_unggulan`)
- Performa yang bagus untuk intent `faq_umum` (F1: 85%) dibandingkan Logistic Regression
- Model cenderung lebih baik dalam menangkap variasi pertanyaan

**Kelemahan:**
- `info_pendaftaran` memiliki recall yang lebih rendah (75%) dibandingkan Logistic Regression
- Accuracy keseluruhan lebih rendah dibandingkan Logistic Regression

---

## Perbandingan Model

### Ringkasan Perbedaan Performa

| Metrik | Logistic Regression | Multinomial Naive Bayes | Selisih |
|--------|---------------------|------------------------|---------|
| **Accuracy** | **91.55%** | 89.67% | +1.88% |
| **Macro Precision** | **94%** | 92% | +2% |
| **Macro Recall** | **90%** | 87% | +3% |
| **Macro F1-Score** | **91%** | 87% | +4% |
| **Weighted F1-Score** | **92%** | 89% | +3% |

### Model yang Lebih Stabil

**Logistic Regression** menunjukkan performa yang **lebih stabil dan unggul** dalam semua metrik evaluasi:

1. **Accuracy lebih tinggi**: 91.55% vs 89.67%
2. **Precision lebih baik**: Lebih sedikit false positive secara keseluruhan
3. **Recall lebih konsisten**: Lebih seimbang antar intent
4. **F1-Score lebih tinggi**: Menunjukkan keseimbangan yang lebih baik antara precision dan recall

### Rekomendasi

**Model terpilih: Logistic Regression**

Alasan:
- Performa keseluruhan yang lebih tinggi
- Lebih stabil dalam memprediksi berbagai intent
- 5 intent dengan perfect precision (100%)
- Weighted F1-Score 92% menunjukkan performa yang sangat baik

**Area Perbaikan untuk keduanya:**
- `faq_umum` - Perlu definisi boundary yang lebih jelas dengan intent lain

---

*Dokumen ini diperbarui: 4 Januari 2026*
