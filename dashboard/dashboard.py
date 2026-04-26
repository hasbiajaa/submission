import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- PERBAIKAN 1: Pindah ke Paling Atas ---
# set_page_config WAJIB dipanggil pertama kali di Streamlit
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# Mengatur tema seaborn
sns.set_theme(style="whitegrid")

# ==============================
# 1. LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    
    # List kolom yang biasanya beda antara dataset asli vs codingan
    rename_dict = {
        'dteday': 'date',
        'cnt': 'total_count',
        'hum': 'humidity',
        'weathersit': 'weather',
        'yr': 'year' # <-- Tambahan jaga-jaga kalau namanya masih 'yr'
    }
    
    # Rename kolom yang ada aja
    df.rename(columns=rename_dict, inplace=True)
    
    # --- PERBAIKAN 2: Typo nama kolom disamakan jadi 'date' ---
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        
    return df

df = load_data()

# ==============================
# 2. KOMPONEN UI & SIDEBAR INTERAKTIF
# ==============================
st.title("🚲 Dashboard Analisis Persewaan Sepeda")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=150)
    st.header("SeSepedaaa")
    st.title ("Persewaan Sepeda Terbaik Sepanjang Sejarah!")
    st.markdown("---")
    st.header("Filter Data 🎛️")
    
    # Filter Interaktif 1: Tahun
    tahun_pilihan = st.selectbox("Pilih Tahun:", ('Semua Tahun', '2011', '2012'))
    
    # Filter Interaktif 2: Musim
    musim_pilihan = st.multiselect(
        "Pilih Musim:",
        options=df['season'].unique(),
        default=df['season'].unique()
    )

# --- PERBAIKAN 3: Antisipasi tipe data pas filter ---
if tahun_pilihan != 'Semua Tahun':
    # Diubah ke string dulu biar filter teks vs angkanya gak nge-bug
    main_df = df[df['year'].astype(str) == tahun_pilihan]
else:
    main_df = df.copy()

main_df = main_df[main_df['season'].isin(musim_pilihan)]

# ==============================
# 3. METRIK UTAMA
# ==============================
col_met1, col_met2, col_met3 = st.columns(3)
with col_met1:
    st.metric("Total Penyewaan", value=f"{main_df['total_count'].sum():,}")
with col_met2:
    st.metric("Pengguna Kasual", value=f"{main_df['casual'].sum():,}")
with col_met3:
    st.metric("Pengguna Terdaftar", value=f"{main_df['registered'].sum():,}")

st.markdown("---")

# ==============================
# 4. VISUALISASI 1 (CUACA) - ATAS BAWAH
# ==============================
st.subheader("1. Pengaruh Cuaca Terhadap Penyewaan Sepeda")
rata_rata_cuaca = main_df.groupby('weather', observed=True)['total_count'].mean().reset_index()

# --- GRAFIK A (ATAS): BAR CHART ---
st.markdown("**A. Rata-rata Sewa per Kondisi Cuaca**")
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(x="weather", y="total_count", data=rata_rata_cuaca, palette=["#2ecc71", "#f1c40f", "#e74c3c"], ax=ax1)
ax1.set_ylabel("Rata-rata Sewa")
ax1.set_xlabel("Kondisi Cuaca")
st.pyplot(fig1)

st.write("") # Kasih jarak dikit biar rapi

# --- GRAFIK B (BAWAH): BOXPLOT ---
st.markdown("**B. Distribusi Total Sewa per Kondisi Cuaca**")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.boxplot(x="weather", y="total_count", data=main_df, palette=["#2ecc71", "#f1c40f", "#e74c3c"], ax=ax2)
ax2.set_ylabel("Total Sewa")
ax2.set_xlabel("Kondisi Cuaca")
st.pyplot(fig2)

st.markdown("---")

# ==============================
# 5. VISUALISASI 2 (HARI KERJA VS LIBUR)
# ==============================
st.subheader("2. Rata-rata Sewa & Komposisi Pengguna: Hari Kerja vs Libur")

# --- GRAFIK 1 (ATAS): RATA-RATA SEWA TOTAL ---
st.markdown("**A. Rata-rata Total Sewa**")

# Hitung rata-rata dulu
rata_rata_hari = main_df.groupby('workingday')['total_count'].mean().reset_index()
rata_rata_hari['workingday'] = rata_rata_hari['workingday'].replace({0: 'Akhir Pekan/Libur', 1: 'Hari Kerja', '0': 'Akhir Pekan/Libur', '1': 'Hari Kerja'})

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(x="workingday", y="total_count", data=rata_rata_hari, palette=["#3498db", "#e74c3c"], ax=ax3)
ax3.set_ylabel("Rata-rata Sewa Total")
ax3.set_xlabel("Kategori Hari")
st.pyplot(fig3)

st.write("") # Kasih jarak dikit biar gak terlalu nempel

# --- GRAFIK 2 (BAWAH): KOMPOSISI PENGGUNA ---
st.markdown("**B. Komposisi: Kasual vs Terdaftar**")

# Melt data untuk misahin casual dan registered
data_melted = main_df.melt(
    id_vars=['workingday'], 
    value_vars=['casual', 'registered'], 
    var_name='user_type', 
    value_name='count'
)

# Mapping nama kategori hari biar rapi
data_melted['workingday'] = data_melted['workingday'].replace({'0': 'Akhir Pekan/Libur', '1': 'Hari Kerja', 0: 'Akhir Pekan/Libur', 1: 'Hari Kerja'})

fig4, ax4 = plt.subplots(figsize=(10, 5))
sns.barplot(x="workingday", y="count", hue="user_type", data=data_melted, palette=["#e67e22", "#2c3e50"], errorbar=None, ax=ax4)
ax4.set_ylabel("Rata-rata Sewa per Tipe")
ax4.set_xlabel("Kategori Hari")
st.pyplot(fig4)

st.markdown("---")
st.caption("Copyright © Dicoding Cohort 2026")