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

# Custom CSS untuk Memperbaiki Ukuran Font Metrik (Agar Tidak Terpotong) & Tipografi Profesional
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

    /* Mengatur ukuran font nilai metrik agar tidak terpotong saat nilai nominal besar */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700;
        color: #0f172a;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #64748b;
    }

    .stMetric {
        background-color: #ffffff;
        padding: 14px;
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
    df = pd.read_excel(file_path, sheet_name="NOV 2025-SEPT 2026")

    # Preprocessing & Pembersihan Struktur
    df["Tanggal"] = pd.to_datetime(df["Tanggal "])
    df["Invoice"] = pd.to_numeric(df["Invoice"], errors="coerce")
    df = df.dropna(subset=["Invoice"])

    # Mengisi missing values pada produk dengan 0
    product_cols = [
        "Model Rak Solid 2p",
        "Model Rak Magic 2p",
        "Model Rak Magic 3p",
    ]
    for col in product_cols:
        df[col] = df[col].fillna(0)

    # Penyeragaman format angka
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

    # Normalisasi Nama Pelanggan
    df["Pelanggan_Cleaned"] = (
        df["Toko/Pelanggan"].astype(str).str.strip().str.upper()
    )

    # Normalisasi Kategori Pembayaran
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

# 1. Filter Periode Bulan
all_months_options = ["Semua Bulan"] + sorted(
    df["Bulan_Transaksi"].unique().tolist()
)
selected_month_option = st.sidebar.selectbox(
    "Pilih Periode Bulan", options=all_months_options
)

# 2. Filter Metode Pembayaran
all_payment_options = ["Semua Metode Pembayaran"] + sorted(
    df["Kategori_Pembayaran"].unique().tolist()
)
selected_payment_option = st.sidebar.selectbox(
    "Metode Pembayaran", options=all_payment_options
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Pencarian Toko")
# 3. Fitur Pencarian Toko / Pelanggan
search_query = st.sidebar.text_input(
    "Cari Nama Toko / Pelanggan:", placeholder="Contoh: Barokah"
)

# Terapkan Filter ke DataFrame
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

# --- INDIKATOR UTAMA (METRICS) ---
total_penjualan = df_filtered["Jumlah"].sum()
total_transaksi = df_filtered["Invoice"].count()
total_unit_terjual = df_filtered["Total Unit"].sum()
total_pelanggan_aktif = df_filtered["Pelanggan_Cleaned"].nunique()
rata_rata_transaksi = (
    total_penjualan / total_transaksi if total_transaksi > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penjualan", f"Rp {total_penjualan:,.0f}")
col2.metric("Total Unit Terjual", f"{total_unit_terjual:,} Unit")
col3.metric("Jumlah Transaksi", f"{total_transaksi:,} Transaksi")
col4.metric("Rata-rata / Transaksi", f"Rp {rata_rata_transaksi:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BARIS 1: TREN PENJUALAN & ANALISIS PRODUK (BERDAMBINGAN)
# ==========================================
col_row1_1, col_row1_2 = st.columns(2)

with col_row1_1:
    st.markdown(
        '<p class="section-header">📈 1. Analisis Tren Penjualan Bulanan</p>',
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
            color="#2b5c8f",
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
        '<p class="section-header">📦 2. Analisis Kontribusi Model Produk</p>',
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
        color=["#3b82f6", "#d97706", "#8b5cf6"],  # Soft elegant colors
        width=0.45,
    )
    ax.set_title(
        "Total Unit Terjual Berdasarkan Model Rak",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )
    ax.set_ylabel("Jumlah Unit", fontsize=9)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + max(1, yval * 0.02),
            f"{int(yval)}",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )
    st.pyplot(fig)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BARIS 2: PERILAKU PELANGGAN (RFM) & ANALISIS PEMBAYARAN
# ==========================================
st.markdown(
    '<p class="section-header">👥 3. Analisis Perilaku Pembelian Pelanggan (RFM Deskriptif)</p>',
    unsafe_allow_html=True,
)
rfm_table = (
    df_filtered.groupby("Pelanggan_Cleaned")
    .agg(
        Frekuensi_Transaksi=("Invoice", "count"),
        Total_Nilai_Pembelian=("Jumlah", "sum"),
        Total_Unit_Dibeli=("Total Unit", "sum"),
    )
    .reset_index()
    .sort_values(by="Total_Nilai_Pembelian", ascending=False)
)

st.dataframe(
    rfm_table.head(10).style.format({"Total_Nilai_Pembelian": "Rp {:,.2f}"}),
    use_container_width=True,
)

st.markdown(
    '<p class="section-header">💳 4. Analisis Metode Pembayaran</p>',
    unsafe_allow_html=True,
)
pay_sum = (
    df_filtered.groupby("Kategori_Pembayaran")
    .agg(
        Jumlah_Transaksi=("Invoice", "count"),
        Total_Penjualan=("Jumlah", "sum"),
        Cash_Diterima=("Cash/Transfer", "sum"),
        Kredit_Tempo=("Kredit", "sum"),
    )
    .reset_index()
)

col_a, col_b = st.columns([1, 1.2])
with col_a:
    if len(pay_sum) > 0:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.pie(
            pay_sum["Jumlah_Transaksi"],
            labels=pay_sum["Kategori_Pembayaran"],
            autopct="%1.1f%%",
            startangle=140,
            colors=["#3b82f6", "#f59e0b", "#64748b", "#10b981"],
        )
        ax.set_title("Proporsi Transaksi Pembayaran", fontsize=10, fontweight="bold")
        st.pyplot(fig)
    else:
        st.info("Data pembayaran kosong.")

with col_b:
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(
        pay_sum.style.format(
            {
                "Total_Penjualan": "Rp {:,.2f}",
                "Cash_Diterima": "Rp {:,.2f}",
                "Kredit_Tempo": "Rp {:,.2f}",
            }
        ),
        use_container_width=True,
    )

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>© 2026 | Penelitian Skripsi Sistem Informasi - STMIK IKMI Cirebon</p>",
    unsafe_allow_html=True,
)
