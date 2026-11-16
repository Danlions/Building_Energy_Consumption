from datetime import date

import pytest

from src.predict import InputTidakValid, prediksi_harian

RABU = date(2026, 7, 1)    # hari kerja
MINGGU = date(2026, 7, 5)  # akhir pekan


def test_hari_kerja_normal():
    h = prediksi_harian(RABU, False, 22, 31, 450)
    assert len(h["prediksi_kWh"]) == 24
    assert h["total_kWh"] > 0
    assert h["peringatan"] == []


def test_hari_kerja_lebih_boros_dari_libur():
    kerja = prediksi_harian(RABU, False, 22, 31, 450)
    libur = prediksi_harian(MINGGU, False, 22, 31, 20)
    assert kerja["total_kWh"] > libur["total_kWh"]


def test_minggu_okupansi_tinggi_memberi_peringatan():
    h = prediksi_harian(MINGGU, False, 22, 31, 450)
    assert len(h["peringatan"]) == 1


def test_suhu_mustahil():
    with pytest.raises(InputTidakValid):
        prediksi_harian(RABU, False, 22, 80, 450)


def test_suhu_min_lebih_besar_dari_maks():
    with pytest.raises(InputTidakValid):
        prediksi_harian(RABU, False, 35, 25, 450)


def test_okupansi_negatif():
    with pytest.raises(InputTidakValid):
        prediksi_harian(RABU, False, 22, 31, -5)


def test_okupansi_terlalu_besar():
    with pytest.raises(InputTidakValid):
        prediksi_harian(RABU, False, 22, 31, 5000)


def test_masukan_bukan_angka():
    with pytest.raises(InputTidakValid):
        prediksi_harian(RABU, False, float("nan"), 31, 450)