import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman Dashboard (Soft Blue Theme & Professional Layout)
st.set_page_config(
    page_title="Dashboard Analisis Perilaku Pembelian - Shane Alumunium",
    page_icon="📊",
    layout="wide",
)

# Custom CSS untuk Tipografi & Metrik
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    .main-title {
        font-weight: 700;
        color: #0f172a;
        font-size: 1.8rem;
        margin-bottom: 0px;
    }
    
    .sub-title {
        font-weight: 400;
        color: #475569;
        font-size: 1rem;
        margin-bottom: 15px;
    }

    .section-header {
        font-weight: 600;
        color: #1e3a8a;
        font-size: 1.25rem;
        margin-top: 25px;
        margin-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        font-weight: 700;
        color: #0f172a;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #64748b;
    }

    .stMetric {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Memuat & Memproses Data
@st.cache_data
def load_and_prepare_data():
    file_path = "Data Penjualan Gabungan Nov 2025-Sept 2026.xlsx"
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0])

    df["Tanggal"] = pd.to_datetime(df["Tanggal "])
    df["Invoice"] = pd.to_numeric(df["Invoice"], errors="coerce")
    df = df.dropna(subset=["Invoice"])

    product_cols = [
        "Model Rak Solid 2p",
        "Model Rak Magic 2p",
        "Model Rak Magic 3p",
    ]
    for col in product_cols:
        df[col] = df[col].fillna(0)

    df["Total Unit"] = (
        pd.to_numeric(df["Total Unit"], errors="coerce").fillna(0).astype(int)
    )
    df["Jumlah"] = (
        pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0).astype(float)
    )
    df["Cash/Transfer"] = (
        pd.to_numeric(df["Cash/Transfer"], errors="coerce")
        .fillna(0)
        .astype(float)
    )
    df["Kredit"] = (
        pd.to_numeric(df["Kredit"], errors="coerce").fillna(0).astype(float)
    )

    df["Pelanggan_Cleaned"] = (
        df["Toko/Pelanggan"].astype(str).str.strip().str.upper()
    )

    def normalize_payment(ket):
        ket_str = str(ket).strip().lower()
        if "cash" in ket_str or "tf" in ket_str:
            return "Cash / Transfer"
        elif "kredit" in ket_str or "tempo" in ket_str or "kontra bon" in ket_str:
            return "Kredit / Tempo"
        elif "giro" in ket_str:
            return "Giro"
        else:
            return "Lainnya"

    df["Kategori_Pembayaran"] = df["Keterangan"].apply(normalize_payment)
    df["Bulan_Transaksi"] = df["Tanggal"].dt.to_period("M").astype(str)
    return df


df = load_and_prepare_data()

# ==========================================
# SIDEBAR: FILTER DASHBOARD
# ==========================================
st.sidebar.markdown("### 🔍 Filter Dashboard")
st.sidebar.markdown("---")

all_months_options = ["Semua Bulan"] + sorted(
    df["Bulan_Transaksi"].unique().tolist()
)
selected_month_option = st.sidebar.selectbox(
    "Pilih Periode Bulan", options=all_months_options
)

all_payment_options = ["Semua Metode Pembayaran"] + sorted(
    df["Kategori_Pembayaran"].unique().tolist()
)
selected_payment_option = st.sidebar.selectbox(
    "Metode Pembayaran", options=all_payment_options
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Pencarian Toko")
search_query = st.sidebar.text_input(
    "Cari Nama Toko / Pelanggan:", placeholder="Contoh: Barokah"
)

df_filtered = df.copy()

if selected_month_option != "Semua Bulan":
    df_filtered = df_filtered[
        df_filtered["Bulan_Transaksi"] == selected_month_option
    ]

if selected_payment_option != "Semua Metode Pembayaran":
    df_filtered = df_filtered[
        df_filtered["Kategori_Pembayaran"] == selected_payment_option
    ]

if search_query:
    df_filtered = df_filtered[
        df_filtered["Pelanggan_Cleaned"].str.contains(
            search_query.strip().upper(), na=False
        )
    ]

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **Total Data Terpilih:** {len(df_filtered)} baris")


# ==========================================
# HEADER UTAMA DASHBOARD
# ==========================================
st.markdown(
    '<p class="main-title">📊 Dashboard Business Intelligence</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Analisis Perilaku Pembelian Pelanggan | Studi Kasus: Shane Alumunium (Nov 2025 - Sept 2026)</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# --- INDIKATOR UTAMA (6 KPI - 2 Baris x 3 Kolom) ---
total_penjualan = df_filtered["Jumlah"].sum()
total_transaksi = df_filtered["Invoice"].count()
total_unit_terjual = df_filtered["Total Unit"].sum()
total_pelanggan_aktif = df_filtered["Pelanggan_Cleaned"].nunique()

rata_rata_nilai_transaksi = (
    (total_penjualan / total_transaksi) if total_transaksi > 0 else 0
)
rata_rata_unit_transaksi = (
    (total_unit_terjual / total_transaksi) if total_transaksi > 0 else 0
)

# Baris KPI 1 (3 Kartu)
kpi1_1, kpi1_2, kpi1_3 = st.columns(3)
kpi1_1.metric("Total Penjualan", f"Rp {total_penjualan:,.0f}")
kpi1_2.metric("Total Unit Terjual", f"{total_unit_terjual:,} Unit")
kpi1_3.metric("Jumlah Transaksi", f"{total_transaksi:,} Transaksi")

# Baris KPI 2 (3 Kartu)
kpi2_1, kpi2_2, kpi2_3 = st.columns(3)
kpi2_1.metric("Pelanggan Aktif", f"{total_pelanggan_aktif:,} Toko")
kpi2_2.metric("Rata-rata Nilai Transaksi", f"Rp {rata_rata_nilai_transaksi:,.0f}")
kpi2_3.metric("Rata-rata Unit per Transaksi", f"{rata_rata_unit_transaksi:.1f} Unit")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BARIS 1: TREN PENJUALAN & KONTRIBUSI MODEL PRODUK (BERDAMBINGAN)
# ==========================================
col_row1_1, col_row1_2 = st.columns(2)

with col_row1_1:
    st.markdown(
        '<p class="section-header">📈 1. Tren Penjualan Bulanan</p>',
        unsafe_allow_html=True,
    )
    trend_df = (
        df_filtered.groupby("Bulan_Transaksi")
        .agg(Total_Penjualan=("Jumlah", "sum"), Jumlah_Transaksi=("Invoice", "count"))
        .reset_index()
    )

    if len(trend_df) > 0:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        ax.plot(
            trend_df["Bulan_Transaksi"],
            trend_df["Total_Penjualan"] / 1e6,
            marker="o",
            color="#3b82f6",
            linewidth=2,
            markersize=5,
        )
        ax.set_title(
            "Total Penjualan per Bulan (Juta IDR)",
            fontsize=11,
            fontweight="bold",
            pad=10,
        )
        ax.set_xlabel("Bulan", fontsize=9)
        ax.set_ylabel("Penjualan (Juta Rp)", fontsize=9)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.4)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada data tren penjualan.")

with col_row1_2:
    st.markdown(
        '<p class="section-header">📦 2. Kontribusi Model Produk</p>',
        unsafe_allow_html=True,
    )
    prod_sum = pd.DataFrame(
        {
            "Kategori Produk": ["Rak Solid 2P", "Rak Magic 2P", "Rak Magic 3P"],
            "Total Unit Terjual": [
                df_filtered["Model Rak Solid 2p"].sum(),
                df_filtered["Model Rak Magic 2p"].sum(),
                df_filtered["Model Rak Magic 3p"].sum(),
            ],
        }
    )

    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = ax.bar(
        prod_sum["Kategori Produk"],
        prod_sum["Total Unit Terjual"],
        color=["#3b82f6", "#f
