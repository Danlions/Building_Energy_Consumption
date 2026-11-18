<<<<<<< HEAD
# Prediksi Konsumsi Energi Gedung · Tim [nama tim]

**Kasus:** 02 · Konsumsi energi gedung · **Aplikasi:** https://buildingenergyconsumption.streamlit.app/ · **Video:** [tautan video]

| Anggota | NIM | Bagian yang dikerjakan |
|---|---|---|
| [nama] | [NIM] | [misalnya EDA dan pembersihan data] |
| [nama] | [NIM] | [misalnya model dan evaluasi] |
| [nama] | [NIM] | [misalnya API dan aplikasi] |

## Masalah dan pengguna

[Dua atau tiga kalimat: siapa penggunanya dan keputusan apa yang dibantu oleh model ini.]

## Data dan pembersihan

| Masalah yang ditemukan | Jumlah baris | Cara menangani |
|---|---|---|
| [misalnya baris duplikat] | [angka] | [misalnya dihapus dengan drop_duplicates] |

## Hasil

| Model | [metrik utama] *validation* | [metrik utama] *test* |
|---|---|---|
| *Baseline*: [nama *baseline*] | | |
| [model final] | | |

*Threshold* yang dipakai: [angka], karena [alasan bisnis].

## Cara menjalankan

```bash
pip install -r requirements.txt
uvicorn app.api.main:app --reload       # API
streamlit run app/ui/streamlit_app.py   # aplikasi
```

## Struktur repositori

```
notebooks/      notebook dari EDA sampai penyimpanan model
data/           data mentah (dan data bersih jika perlu)
src/features.py fungsi pembuat fitur, dipakai saat pelatihan dan saat prediksi
artifacts/      model.joblib + metadata.json
app/            API (FastAPI) dan antarmuka (Streamlit)
```

## Keterbatasan

[Dalam kondisi apa model ini tidak dapat dipercaya? Data apa yang belum tersedia?]

## Daftar periksa sebelum dikumpulkan

- [ ] Repositori bersifat publik dan setiap anggota memiliki *commit*
- [ ] *Notebook* dapat dijalankan ulang dari awal sampai akhir tanpa galat
- [ ] *Baseline* wajib dilaporkan dan dibandingkan
- [ ] Data *test* hanya dibuka satu kali, di akhir
- [ ] `artifacts/metadata.json` berisi versi model, fitur masukan, *threshold*, dan metrik
- [ ] Aplikasi dapat dibuka orang lain melalui tautan, termasuk dari ponsel
- [ ] Aplikasi tidak berhenti mendadak ketika menerima masukan yang tidak wajar
- [ ] Laporan paling banyak 6 halaman dan video paling lama 5 menit
=======
# Prediksi Konsumsi Energi Gedung · Tim [kaciww]

**Kasus:** 02, Konsumsi Energi Gedung (regresi deret waktu, metrik utama MAE) · **Aplikasi:** https://buildingenergyconsumption.streamlit.app/ · **Video:** [tautan video]

| Anggota | NIM | Bagian yang dikerjakan |
- Dwiky Jerryan Koryanto Muhammad | 2401401 | EDA dan pembersihan data, model dan evaluasi, API dan aplikasi |
- Rifa Ardhan | 2400920 | Pengujian otomatis (pytest untuk `src/predict.py` dan API), pengujian manual aplikasi, notebook analisis galat, tombol unduh CSV |

## Masalah dan pengguna

Pengelola gedung perkantoran 8 lantai di Bandung perlu mengetahui konsumsi listrik (kWh) per jam untuk **besok**, agar jadwal chiller dan kontrak daya bisa diatur. Aplikasi memprediksi 24 jam konsumsi dari lima masukan: tanggal, status libur, suhu minimum, suhu maksimum, dan okupansi puncak.

## Aturan brief yang dipatuhi

- Tidak memakai data masa depan; konsumsi masa lalu hanya boleh dipakai jika lag >= 24 jam.
- Pembagian berdasarkan waktu: train sampai Feb 2026, validation Mar-Apr 2026, test Mei-Jun 2026.
- Baseline wajib: "sama dengan minggu lalu" (lag 168 jam).
- Test set dibuka satu kali; model tidak diubah setelahnya.

## Data dan pembersihan

Data mentah `raw.csv` berisi 21.837 baris (Jan 2024 - Jun 2026).

| Masalah yang ditemukan | Jumlah baris | Cara menangani |
|---|---|---|
| Format waktu tidak konsisten (DD/MM/YYYY HH.MM) | 747 (Mar 2026) | Diparse dengan format kedua |
| Baris duplikat penuh | 80 | Dihapus |
| Jam hilang | 131 | Dibuat kisi jam lengkap (21.888 jam) |
| Konsumsi negatif | 21 | Dijadikan NaN |
| Kode galat 99999 | 19 | Dijadikan NaN |
| Nol tersebar acak | 41 | Dijadikan NaN |
| Suhu dan kelembapan kosong | celah 1 jam; satu celah 97 jam (7-11 Okt 2025) | Celah pendek diinterpolasi; celah 97 jam diisi rata-rata bulan-jam |
| Okupansi kosong | 216 | Interpolasi |
| hari_libur kosong | - | Dipulihkan dari tanggal yang sama |

Total 212 baris target (negatif, 99999, nol acak) tidak dipakai untuk melatih maupun menilai. Kolom `konsumsi_filled` hanya dipakai untuk fitur lag, bukan untuk penilaian.

## Model

`HistGradientBoostingRegressor` (loss `absolute_error`) dengan 6 fitur: jam, hari_minggu, bulan, suhu_luar_C, okupansi_orang, hari_libur. Model dengan fitur lag (24, 168) tidak lebih baik (MAE 5,07 vs 5,03 pada validation), sehingga dipilih model tanpa lag yang lebih sederhana. Model final (v1.1.0) dilatih pada train + validation.

Fitur paling berpengaruh (permutation importance): okupansi (73), suhu (10), jam (2).

## Hasil

Metrik: MAE (kWh), makin kecil makin baik.

| Model | MAE *validation* | MAE *test* |
|---|---|---|
| *Baseline*: sama dengan minggu lalu (lag 168 jam) | 22,12 | 24,24 |
| HistGradientBoostingRegressor (6 fitur, tanpa lag) | 4,97 | 4,97 |
| Model yang sama, masukan berderau | 9,69 | 9,86 |

- Pada test: bias -0,34 kWh; MAE minggu biasa 4,99 dan minggu libur 4,85.
- Derau (suhu ±1,5 °C, okupansi ±15%) adalah asumsi tim, bukan data prakiraan sungguhan.
- Angka validation berasal dari model yang dilatih hanya pada train, sedangkan model di test dilatih pada train + validation.
- Ini kasus regresi, jadi tidak ada *threshold*.

### Analisis galat (`notebooks/03_error_analysis.ipynb`)

Notebook hanya membaca galat; model tidak diubah setelah test set dibuka. Angkanya cocok dengan hasil tim (1.449 baris dinilai, MAE 4,97, bias -0,34, baseline 24,24).

- MAE per jam 4,07-5,77 kWh dan per hari 4,56-5,40 kWh; tidak ada jam atau hari yang jelas bermasalah.
- MAE tidak membesar saat panas (4,75-5,14 kWh); bias paling negatif pada 28-34 °C (-0,85).
- 8 dari 10 galat terbesar berupa tebakan terlalu rendah (20-35 kWh), empat di antaranya Sabtu siang dengan okupansi sekitar 20 orang. Penyebabnya baru dugaan.
- Dua bulan test tidak cukup untuk menguji dugaan bahwa tren naik membuat model menebak terlalu rendah.

### Pengujian

- **Otomatis:** 17 uji pytest lulus: 8 untuk `src/predict.py` dan 9 untuk API (`/health`, `/predict`). Masukan tidak valid menghasilkan kode 422, bukan 500.
- **Manual:** 16 skenario di ponsel (tampilan, masukan normal, masukan tidak wajar, peringatan, nilai batas), semua lulus.
- Uji ini memeriksa logika masukan dan bentuk keluaran, bukan akurasi prediksi. Akurasi dinilai lewat MAE di test set.

## Cara menjalankan

```bash
git clone https://github.com/Danlions/Building_Energy_Consumption.git
cd Building_Energy_Consumption
python -m venv .venv
.venv\Scripts\activate                   # Windows
pip install -r requirements.txt
uvicorn app.api.main:app --reload       # API
streamlit run app/ui/streamlit_app.py   # aplikasi
```

Uji otomatis:

```bash
pip install pytest httpx
python -m pytest -v
```

Versi Python yang dipakai: 3.13.7 dan 3.15.2.

## Struktur repositori

```
notebooks/      01_eda.ipynb, 02_model.ipynb, 03_error_analysis.ipynb
data/           raw.csv, clean.csv
src/            features.py (pembuat fitur), predict.py (prediksi 24 jam)
artifacts/      model.joblib, metadata.json, profil.json
app/            api/main.py (FastAPI), ui/streamlit_app.py (Streamlit)
tests/          test_predict.py, test_api.py
```

## Keterbatasan

- Model sangat bergantung pada okupansi; okupansi yang salah menghasilkan prediksi yang salah tanpa disadari.
- Data sintetis dan hanya dari satu gedung.
- Data latih berhenti Apr 2026; tren naik sekitar 4-5% per tahun bisa membuat model menebak terlalu rendah di masa depan.
- Profil suhu dan okupansi per jam adalah rata-rata historis, bukan prakiraan nyata.
- Okupansi di luar kisaran historis hari kerja (428-581 orang) memicu peringatan, dan prediksinya kurang bisa dipercaya.

## Daftar periksa sebelum dikumpulkan

- [✅] Repositori bersifat publik dan setiap anggota memiliki *commit*
- [✅] *Notebook* dapat dijalankan ulang dari awal sampai akhir tanpa galat
- [✅] *Baseline* wajib dilaporkan dan dibandingkan
- [✅] Data *test* hanya dibuka satu kali, di akhir
- [✅] `artifacts/metadata.json` berisi versi model, fitur masukan, *threshold*, dan metrik
- [✅] Aplikasi dapat dibuka orang lain melalui tautan, termasuk dari ponsel
- [✅] Aplikasi tidak berhenti mendadak ketika menerima masukan yang tidak wajar
- [✅] Laporan paling banyak 6 halaman dan video paling lama 5 menit
>>>>>>> e50a5c024ce47777bc011740cd454cc4849fd408
