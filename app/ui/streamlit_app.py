import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))  # agar "src" terbaca

import pandas as pd
import streamlit as st

from src.predict import InputTidakValid, prediksi_harian, _muat

st.set_page_config(page_title="Prediksi Konsumsi Energi Gedung", page_icon="⚡")
st.title("⚡ Prediksi Konsumsi Listrik Besok")
st.caption("Gedung perkantoran 8 lantai, Bandung. Prediksi kWh per jam untuk 24 jam.")

_, meta, _ = _muat()
besok = date.today() + timedelta(days=1)

with st.form("masukan"):
    tanggal = st.date_input("Tanggal", value=besok)
    libur = st.checkbox("Hari libur nasional / cuti bersama")
    c1, c2 = st.columns(2)
    suhu_min = c1.number_input("Suhu minimum (°C)", value=22.0, step=0.5)
    suhu_maks = c2.number_input("Suhu maksimum (°C)", value=31.0, step=0.5)
    okupansi = st.number_input("Perkiraan jumlah orang pada jam tersibuk",
                               value=450.0 if besok.weekday() < 5 else 20.0, step=10.0)
    kirim = st.form_submit_button("Prediksi")

if kirim:
    try:
        h = prediksi_harian(tanggal, libur, suhu_min, suhu_maks, okupansi)
    except InputTidakValid as e:
        st.error(str(e))
    else:
        for p in h["peringatan"]:
            st.warning(p)

        df = pd.DataFrame({"jam": h["jam"], "kWh": h["prediksi_kWh"]}).set_index("jam")
        k1, k2 = st.columns(2)
        k1.metric("Total 24 jam", f"{h['total_kWh']:,.0f} kWh")
        k2.metric("Jam puncak", f"{df['kWh'].idxmax():02d}:00", f"{df['kWh'].max():.0f} kWh")

        st.bar_chart(df, y_label="kWh", x_label="Jam")
        with st.expander("Lihat tabel per jam"):
            st.dataframe(pd.DataFrame({"jam": h["jam"], "suhu_C": h["suhu_C"],
                                       "orang": h["okupansi_orang"],
                                       "prediksi_kWh": h["prediksi_kWh"]}),
                         hide_index=True)

        mae = meta["metrik"]["validation_MAE_model"]
        st.caption(f"Galat rata-rata model pada data validasi ±{mae:.1f} kWh per jam "
                   f"jika suhu dan okupansi akurat; bisa lebih besar jika prakiraan meleset. "
                   f"Model v{h['versi_model']}.")