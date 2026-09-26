"""
generate_gd_report.py
======================
Skrip ekspor data untuk Skripsi Bab IV, Subbab 4.3 (Hasil Penerapan Graceful Degradation).

Skrip ini memanggil fungsi yang SUDAH ADA di database.py:
  - get_graceful_degradation_stats()   -> statistik agregat (Tabel 4.X Ringkasan)
  - get_graceful_degradation_samples() -> daftar kueri lengkap (Tabel 4.X Sampel)

Cara pakai:
1. Salin file ini ke root folder repo chatbot-psb (sejajar dengan database.py),
   ATAU jalankan dari lokasi lain dengan menambahkan repo ke PYTHONPATH.
2. Pastikan environment variable DATABASE_URL mengarah ke database produksi
   (di Railway: Settings > Variables pada service Postgres, atau jalankan
   lewat `railway run python generate_gd_report.py` supaya env terisi otomatis).
3. (Opsional) atur START_DATE / END_DATE di bawah bila ingin membatasi periode
   pengujian (mis. hanya log selama sesi pengujian FCR pada Subbab 3.14).
4. Jalankan: python generate_gd_report.py
5. Keluaran:
   - gd_summary.md         -> tabel ringkasan statistik siap tempel ke skripsi
   - gd_samples_full.csv   -> seluruh log kueri (arsip mentah / lampiran)
   - gd_samples_table.md   -> tabel sampel representatif (Markdown, sudah dibagi
                              proporsional ke 3 kategori: tinggi/sedang/rendah)
   - gd_transcripts.md     -> 2 transkrip contoh (normal & fallback) siap tempel
                              ke Subbab 4.3.5

Catatan penting:
- Skrip ini TIDAK mengubah data apa pun di database (read-only).
- Bila hasil kosong (total_queries = 0), berarti belum ada kueri riil yang
  tercatat -- jalankan dulu sejumlah kueri uji melalui bot Telegram produksi
  sebelum menjalankan skrip ini.
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from database import get_graceful_degradation_stats, get_graceful_degradation_samples
except ImportError:
    print(
        "[ERROR] Tidak bisa import dari database.py.\n"
        "        Pastikan skrip ini dijalankan dari root folder repo chatbot-psb\n"
        "        (sejajar dengan database.py, response_router.py, dst.)."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# KONFIGURASI - sesuaikan bila perlu
# ---------------------------------------------------------------------------
START_DATE = None   # None = tidak ada filter tanggal awal (ambil semua)
END_DATE   = None   # None = tidak ada filter tanggal akhir (ambil semua)
PLATFORM   = None   # None = semua platform (telegram, web, dll.)
SAMPLES_PER_CATEGORY = 5   # jumlah baris contoh per kategori pada gd_samples_table.md
OUTPUT_DIR = Path("data-postgres")  # folder tujuan semua berkas keluaran

CATEGORY_LABEL = {
    "high": "Tinggi (\u2265 0,70) - Alur normal",
    "medium": "Sedang (0,30-0,70) - Alur hati-hati",
    "low": "Rendah (< 0,30) - Fallback total",
}


def categorize(confidence):
    if confidence is None:
        return "unknown"
    if confidence >= 0.70:
        return "high"
    elif confidence >= 0.30:
        return "medium"
    else:
        return "low"


def main():
    # Buat folder keluaran jika belum ada
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Mengambil statistik agregat dari database (SEMUA data, tanpa filter)...")
    stats = get_graceful_degradation_stats(
        start_date=START_DATE, end_date=END_DATE, platform=PLATFORM
    )

    print("Mengambil seluruh sampel kueri dari database (SEMUA data, tanpa filter)...")
    samples = get_graceful_degradation_samples(
        start_date=START_DATE, end_date=END_DATE, platform=PLATFORM
    )

    if stats["total_queries"] == 0:
        print(
            "\n[PERINGATAN] total_queries = 0. Belum ada log kueri pada rentang "
            "yang diminta. Jalankan dulu kueri uji melalui bot, lalu ulangi."
        )

    # -----------------------------------------------------------------
    # 1) gd_summary.md - Tabel Ringkasan Statistik (untuk Subbab 4.3.4)
    # -----------------------------------------------------------------
    with open(OUTPUT_DIR / "gd_summary.md", "w", encoding="utf-8") as f:
        f.write("**Tabel 4.X** Ringkasan Statistik Graceful Degradation\n\n")
        f.write("| Kategori | Jumlah Kueri | Persentase |\n")
        f.write("|---|---|---|\n")
        f.write(
            f"| Alur normal (confidence >= 0,70) | {stats['high_confidence_queries']} | "
            f"{stats['high_confidence_queries'] / stats['total_queries'] * 100:.2f}% |\n"
            if stats["total_queries"] else
            "| Alur normal (confidence >= 0,70) | 0 | 0,00% |\n"
        )
        if stats["total_queries"]:
            f.write(
                f"| Alur cautious (0,30 <= confidence < 0,70) | {stats['medium_confidence_queries']} | "
                f"{stats['medium_confidence_queries'] / stats['total_queries'] * 100:.2f}% |\n"
            )
            f.write(
                f"| Fallback total (confidence < 0,30) | {stats['very_low_confidence_queries']} | "
                f"{stats['very_low_confidence_queries'] / stats['total_queries'] * 100:.2f}% |\n"
            )
        f.write(f"| **Total** | **{stats['total_queries']}** | **100%** |\n\n")
        f.write(
            f"Dari total {stats['total_queries']} kueri uji, tercatat "
            f"{stats['fallback_queries']} kueri ({stats['fallback_percentage']}%) yang memicu "
            f"mekanisme fallback total (confidence score < 0,30).\n"
        )
    print(f"-> {OUTPUT_DIR}/gd_summary.md ditulis.")

    # -----------------------------------------------------------------
    # 2) gd_samples_full.csv - arsip mentah seluruh log (lampiran)
    # -----------------------------------------------------------------
    with open(OUTPUT_DIR / "gd_samples_full.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["id", "question", "intent", "confidence", "confidence_status",
             "fallback", "routed_to", "response"]
        )
        for s in samples:
            writer.writerow([
                s["id"], s["question"], s["intent"], s["confidence"],
                s["confidence_status"], s["fallback"], s["routed_to"], s["response"],
            ])
    print(f"-> {OUTPUT_DIR}/gd_samples_full.csv ditulis ({len(samples)} baris).")

    # -----------------------------------------------------------------
    # 3) gd_samples_table.md - tabel sampel representatif (Subbab 4.3.3)
    # -----------------------------------------------------------------
    buckets = {"high": [], "medium": [], "low": []}
    for s in samples:
        cat = categorize(s["confidence"])
        if cat in buckets:
            buckets[cat].append(s)

    with open(OUTPUT_DIR / "gd_samples_table.md", "w", encoding="utf-8") as f:
        f.write("**Tabel 4.X** Sampel Kueri Uji Berdasarkan Status Perutean\n\n")
        f.write("| No | Kueri Pengguna | Intent Terprediksi | Confidence Score | Status | Rute |\n")
        f.write("|---|---|---|---|---|---|\n")
        no = 1
        for cat in ["high", "medium", "low"]:
            for s in buckets[cat][:SAMPLES_PER_CATEGORY]:
                q = (s["question"] or "").replace("|", "/").replace("\n", " ")
                f.write(
                    f"| {no} | {q} | {s['intent']} | {s['confidence']:.4f} | "
                    f"{CATEGORY_LABEL[cat]} | {s['routed_to']} |\n"
                )
                no += 1
    print(f"-> {OUTPUT_DIR}/gd_samples_table.md ditulis "
          f"({sum(len(b[:SAMPLES_PER_CATEGORY]) for b in buckets.values())} baris sampel).")

    # -----------------------------------------------------------------
    # 4) gd_transcripts.md - 2 contoh transkrip siap tempel (Subbab 4.3.5)
    # -----------------------------------------------------------------
    with open(OUTPUT_DIR / "gd_transcripts.md", "w", encoding="utf-8") as f:
        f.write("## Transkrip Percakapan Nyata (draf otomatis, cek ulang sebelum dipakai)\n\n")

        normal_example = buckets["high"][0] if buckets["high"] else None
        fallback_example = buckets["low"][0] if buckets["low"] else None

        f.write("### Skenario 1 - Intent Jelas (Alur Normal)\n\n")
        if normal_example:
            f.write("```\n")
            f.write(f"Pengguna : {normal_example['question']}\n")
            f.write(
                f"Sistem   : Intent = {normal_example['intent']} | "
                f"Confidence = {normal_example['confidence']:.4f}\n"
            )
            f.write(f"           {normal_example['response']}\n")
            f.write("```\n\n")
        else:
            f.write("[Belum ada sampel dengan confidence >= 0,70 pada rentang data ini]\n\n")

        f.write("### Skenario 2 - Confidence Rendah (Fallback)\n\n")
        if fallback_example:
            f.write("```\n")
            f.write(f"Pengguna : {fallback_example['question']}\n")
            f.write(
                f"Sistem   : Intent = {fallback_example['intent']} | "
                f"Confidence = {fallback_example['confidence']:.4f} (< 0,30)\n"
            )
            f.write(f"           {fallback_example['response']}\n")
            f.write("```\n\n")
        else:
            f.write("[Belum ada sampel dengan confidence < 0,30 pada rentang data ini]\n\n")

    print(f"-> {OUTPUT_DIR}/gd_transcripts.md ditulis.")

    print(f"\nSelesai. Periksa isi keempat berkas di folder '{OUTPUT_DIR}/', lalu salin ke draf skripsi.")
    print("Ingat: nomor tabel 'Tabel 4.X' masih placeholder - sesuaikan dengan")
    print("penomoran final Bab IV setelah §4.1 disisipkan.")


if __name__ == "__main__":
    main()