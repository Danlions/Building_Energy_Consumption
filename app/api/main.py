from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.predict import InputTidakValid, prediksi_harian, _muat

app = FastAPI(title="Prediksi Konsumsi Energi Gedung")


class Masukan(BaseModel):
    tanggal: date
    libur_nasional: bool = False
    suhu_min: float
    suhu_maks: float
    okupansi_puncak: float


@app.get("/health")
def health():
    _, meta, _ = _muat()
    return {"status": "ok", "versi_model": meta["versi"]}


@app.post("/predict")
def predict(m: Masukan):
    try:
        return prediksi_harian(m.tanggal, m.libur_nasional,
                               m.suhu_min, m.suhu_maks, m.okupansi_puncak)
    except InputTidakValid as e:
        raise HTTPException(status_code=422, detail=str(e))