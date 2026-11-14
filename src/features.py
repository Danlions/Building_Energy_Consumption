"""Pembuat fitur. Dipakai oleh notebook (pelatihan) dan aplikasi (prediksi)."""
import pandas as pd

KOLOM_DASAR = ["suhu_luar_C", "kelembaban_luar_pct", "okupansi_orang", "hari_libur"]
LAGS = (24, 168)  # semua >= 24 jam: tidak memakai data masa depan


def buat_fitur(df: pd.DataFrame, pakai_lag: bool) -> pd.DataFrame:
    """df: indeks waktu per jam tanpa celah, berisi KOLOM_DASAR
    (dan 'konsumsi_filled' jika pakai_lag=True)."""
    sel = df.index.to_series().diff().dropna()
    assert df.index.is_monotonic_increasing and (sel == pd.Timedelta("1h")).all(), \
        "indeks waktu harus berurutan dan tanpa celah per jam"

    X = pd.DataFrame(index=df.index)
    X["jam"] = df.index.hour
    X["hari_minggu"] = df.index.dayofweek
    X["bulan"] = df.index.month
    for c in KOLOM_DASAR:
        X[c] = df[c]

    if pakai_lag:
        for L in LAGS:
            X[f"lag_{L}"] = df["konsumsi_filled"].shift(L)
            X[f"libur_lag_{L}"] = df["hari_libur"].shift(L)
    return X