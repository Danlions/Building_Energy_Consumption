"""Prediksi konsumsi 24 jam dari masukan sederhana pengelola gedung."""
import json
import math
from datetime import date
from pathlib import Path

import joblib
import pandas as pd

from src.features import buat_fitur

ART = Path(__file__).resolve().parents[1] / "artifacts"
SUHU_BATAS = (5.0, 45.0)      # di luar ini dianggap mustahil
OKUPANSI_BATAS = (0.0, 1000.0)

_model = _meta = _profil = None


class InputTidakValid(ValueError):
    pass


def _muat():
    global _model, _meta, _profil
    if _model is None:
        _model = joblib.load(ART / "model.joblib")
        _meta = json.loads((ART / "metadata.json").read_text())
        p = json.loads((ART / "profil.json").read_text())

        # skalakan agar suhu_min/suhu_maks dan okupansi_puncak terpakai persis
        lo, hi = min(p["suhu"]), max(p["suhu"])
        p["suhu"] = [(v - lo) / (hi - lo) for v in p["suhu"]]
        for tipe, kurva in p["okupansi"].items():
            puncak = max(kurva)
            if puncak > 0:
                p["okupansi"][tipe] = [v / puncak for v in kurva]
        _profil = p
    return _model, _meta, _profil


def prediksi_harian(tanggal: date, libur: bool, suhu_min: float,
                    suhu_maks: float, okupansi_puncak: float) -> dict:
    model, meta, profil = _muat()

    for nama, v in [("suhu_min", suhu_min), ("suhu_maks", suhu_maks),
                    ("okupansi_puncak", okupansi_puncak)]:
        if v is None or not math.isfinite(v):
            raise InputTidakValid(f"{nama} harus berupa angka.")
    if not (SUHU_BATAS[0] <= suhu_min <= SUHU_BATAS[1]
            and SUHU_BATAS[0] <= suhu_maks <= SUHU_BATAS[1]):
        raise InputTidakValid(f"Suhu harus antara {SUHU_BATAS[0]:.0f} dan {SUHU_BATAS[1]:.0f} °C.")
    if suhu_min > suhu_maks:
        raise InputTidakValid("Suhu minimum tidak boleh lebih tinggi dari suhu maksimum.")
    if not (OKUPANSI_BATAS[0] <= okupansi_puncak <= OKUPANSI_BATAS[1]):
        raise InputTidakValid(f"Okupansi puncak harus antara {OKUPANSI_BATAS[0]:.0f} dan {OKUPANSI_BATAS[1]:.0f} orang.")

    kerja = tanggal.weekday() < 5 and not libur
    tipe = "kerja" if kerja else "libur"

    peringatan = []
    r = profil["puncak_okupansi"][tipe]
    if okupansi_puncak < r["min"] or okupansi_puncak > r["max"]:
        nama_tipe = "hari kerja" if kerja else "akhir pekan atau hari libur"
        peringatan.append(
            f"Okupansi puncak {okupansi_puncak:.0f} orang tidak lazim untuk {nama_tipe} "
            f"(di data historis: {r['min']:.0f}-{r['max']:.0f}). "
            "Periksa kembali tanggal, status libur, dan jumlah orang.")
    s = profil["suhu"]
    if suhu_maks - suhu_min < 1:
        peringatan.append("Selisih suhu min dan maks sangat kecil; kurva suhu harian menjadi hampir datar.")

    idx = pd.date_range(pd.Timestamp(tanggal), periods=24, freq="h")
    df = pd.DataFrame({
        "suhu_luar_C": [suhu_min + (suhu_maks - suhu_min) * x for x in s],
        "okupansi_orang": [okupansi_puncak * x for x in profil["okupansi"][tipe]],
        "hari_libur": int(libur),
    }, index=idx)

    X = buat_fitur(df, pakai_lag=False)[meta["fitur_masukan"]]
    pred = [max(0.0, round(float(p), 1)) for p in model.predict(X)]

    return {
        "tanggal": tanggal.isoformat(),
        "jam": list(range(24)),
        "suhu_C": [round(v, 1) for v in df["suhu_luar_C"]],
        "okupansi_orang": [round(v) for v in df["okupansi_orang"]],
        "prediksi_kWh": pred,
        "total_kWh": round(sum(pred), 1),
        "peringatan": peringatan,
        "versi_model": meta["versi"],
    }