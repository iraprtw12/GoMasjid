import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import json

# ===============================
# KONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="Peta Masjid STT NF",
    layout="wide"
)

st.title("Peta Masjid Sekitar STT Terpadu Nurul Fikri")
st.markdown("---")

# ===============================
# KOORDINAT KAMPUS
# ===============================
STT_NF_KAMPUS_A = (-6.3627193, 106.8443742)
STT_NF_KAMPUS_B = (-6.3528215, 106.8326181)

# ===============================
# FILE DATA (READ ONLY)
# ===============================
DATA_FILE = "data/data_masjid.json"

# ===============================
# LOAD DATA JSON
# ===============================
@st.cache_data
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

st.session_state.masjids = load_data()

# ===============================
# FUNGSI
# ===============================
def hitung_jarak(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def masjid_terdekat(lat, lon, data, limit=10):
    hasil = []
    for m in data:
        jarak = hitung_jarak(lat, lon, m["latitude"], m["longitude"])
        hasil.append({**m, "jarak": round(jarak, 3)})
    hasil.sort(key=lambda x: x["jarak"])
    return hasil[:limit]

def buat_peta(data, user_loc=None, lat=-6.3577, lon=106.8385):
    m = folium.Map(location=[lat, lon], zoom_start=14)

    folium.Marker(
        STT_NF_KAMPUS_A,
        popup="Kampus A STT NF",
        icon=folium.Icon(color="green", icon="university", prefix="fa")
    ).add_to(m)

    folium.Marker(
        STT_NF_KAMPUS_B,
        popup="Kampus B STT NF",
        icon=folium.Icon(color="darkgreen", icon="university", prefix="fa")
    ).add_to(m)

    for d in data:
        info = f"""
        <b>{d['nama']}</b><br>
        {d['alamat']}<br>
        {d.get('jarak', '')} km
        """
        folium.Marker(
            [d["latitude"], d["longitude"]],
            popup=info,
            icon=folium.Icon(color="blue", icon="star", prefix="fa")
        ).add_to(m)

    if user_loc:
        folium.Marker(
            [user_loc[0], user_loc[1]],
            popup="Lokasi Anda",
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(m)

    return m

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.header("Menu")
    menu = st.radio(
        "Pilih Halaman",
        ["Beranda", "Peta Masjid", "Cari Masjid Terdekat", "Data Masjid"]
    )
    st.markdown("---")
    st.metric("Jumlah Masjid", len(st.session_state.masjids))

# ===============================
# HALAMAN
# ===============================
if menu == "Beranda":
    st.write(
        "Aplikasi ini membantu mahasiswa dan masyarakat sekitar "
        "menemukan lokasi masjid di sekitar Kampus STT Terpadu Nurul Fikri."
    )
    peta = buat_peta(st.session_state.masjids)
    st_folium(peta, width=1200, height=500)

elif menu == "Peta Masjid":
    peta = buat_peta(st.session_state.masjids)
    st_folium(peta, width=1200, height=600)

elif menu == "Cari Masjid Terdekat":
    pilihan = st.radio(
        "Pilih Lokasi Awal",
        ["Kampus A", "Kampus B", "Manual"]
    )

    if pilihan == "Kampus A":
        lat, lon = STT_NF_KAMPUS_A
    elif pilihan == "Kampus B":
        lat, lon = STT_NF_KAMPUS_B
    else:
        lat = st.number_input("Latitude", value=-6.3577, format="%.7f")
        lon = st.number_input("Longitude", value=106.8385, format="%.7f")

    if st.button("Cari Masjid Terdekat"):
        hasil = masjid_terdekat(lat, lon, st.session_state.masjids)

        df = pd.DataFrame(hasil)[["nama", "alamat", "jarak"]]
        df.columns = ["Nama Masjid", "Alamat", "Jarak (km)"]
        st.dataframe(df, use_container_width=True)

        peta = buat_peta(hasil, (lat, lon), lat, lon)
        st_folium(peta, width=1200, height=500)

elif menu == "Data Masjid":
    df = pd.DataFrame(st.session_state.masjids)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download Data JSON",
        data=df.to_json(orient="records", force_ascii=False),
        file_name="data_masjid.json",
        mime="application/json"
    )

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("Peta Masjid STT Terpadu Nurul Fikri • Streamlit Cloud Ready")
