from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)

VALID = {
    "tanggal": "2026-07-01",        # hari Rabu
    "libur_nasional": False,
    "suhu_min": 22,
    "suhu_maks": 31,
    "okupansi_puncak": 450,
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "versi_model" in body


def test_predict_normal():
    r = client.post("/predict", json=VALID)
    assert r.status_code == 200
    body = r.json()
    assert len(body["prediksi_kWh"]) == 24
    assert body["total_kWh"] > 0
    assert body["peringatan"] == []


def test_predict_minggu_okupansi_tinggi_memberi_peringatan():
    r = client.post("/predict", json={**VALID, "tanggal": "2026-07-05"})
    assert r.status_code == 200
    assert len(r.json()["peringatan"]) == 1


def test_predict_suhu_mustahil():
    r = client.post("/predict", json={**VALID, "suhu_maks": 80})
    assert r.status_code == 422


def test_predict_suhu_min_lebih_besar_dari_maks():
    r = client.post("/predict", json={**VALID, "suhu_min": 35, "suhu_maks": 25})
    assert r.status_code == 422


def test_predict_okupansi_negatif():
    r = client.post("/predict", json={**VALID, "okupansi_puncak": -5})
    assert r.status_code == 422


def test_predict_okupansi_terlalu_besar():
    r = client.post("/predict", json={**VALID, "okupansi_puncak": 5000})
    assert r.status_code == 422


def test_predict_field_hilang():
    r = client.post("/predict", json={"tanggal": "2026-07-01"})
    assert r.status_code == 422


def test_predict_tanggal_salah_format():
    r = client.post("/predict", json={**VALID, "tanggal": "bukan-tanggal"})
    assert r.status_code == 422