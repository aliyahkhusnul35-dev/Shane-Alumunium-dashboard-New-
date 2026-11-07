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
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

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
# BAGIAN 1: ANALISIS TREN PENJUALAN BULANAN
# ==========================================
st.markdown(
    '<p class="section-header">📈 1. Analisis Tren Penjualan Bulanan</p>',
    unsafe_allow_html=True,
)

trend_df = (
    df_filtered.groupby("Bulan_Transaksi")
    .agg(
        Total_Penjualan=("Jumlah", "sum"),
        Jumlah_Transaksi=("Invoice", "count"),
    )
    .reset_index()
)

if len(trend_df) > 0:
    max_sales_row = trend_df.loc[trend_df["Total_Penjualan"].idxmax()]
    min_sales_row = trend_df.loc[trend_df["Total_Penjualan"].idxmin()]

    col_info1, col_info2 = st.columns(2)
    col_info1.info(
        f"🔥 **Bulan Penjualan Tertinggi:** {max_sales_row['Bulan_Transaksi']} (Rp {max_sales_row['Total_Penjualan']:,.0f})"
    )
    col_info2.warning(
        f"📉 **Bulan Penjualan Terendah:** {min_sales_row['Bulan_Transaksi']} (Rp {min_sales_row['Total_Penjualan']:,.0f})"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_trend1, col_trend2 = st.columns(2)

    with col_trend1:
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
            "Tren Total Penjualan per Bulan (Juta IDR)",
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

    with col_trend2:
        fig2, ax2 = plt.subplots(figsize=(7, 3.8))
        ax2.plot(
            trend_df["Bulan_Transaksi"],
            trend_df["Jumlah_Transaksi"],
            marker="s",
            color="#f59e0b",
            linewidth=2,
            markersize=5,
        )
        ax2.set_title(
            "Tren Jumlah Transaksi per Bulan",
            fontsize=11,
            fontweight="bold",
            pad=10,
        )
        ax2.set_xlabel("Bulan", fontsize=9)
        ax2.set_ylabel("Jumlah Transaksi", fontsize=9)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=8)
        ax2.grid(True, linestyle="--", alpha=0.4)
        st.pyplot(fig2)
else:
    st.warning("Tidak ada data tren penjualan.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BAGIAN 2: KONTRIBUSI MODEL PRODUK
# ==========================================
st.markdown(
    '<p class="section-header">📦 2. Kontribusi Model Produk</p>',
    unsafe_allow_html=True,
)

total_solid = df_filtered["Model Rak Solid 2p"].sum()
total_magic2 = df_filtered["Model Rak Magic 2p"].sum()
total_magic3 = df_filtered["Model Rak Magic 3p"].sum()
grand_total_unit = total_solid + total_magic2 + total_magic3

prod_sum = pd.DataFrame(
    {
        "Model Rak": ["Rak Solid 2P", "Rak Magic 2P", "Rak Magic 3P"],
        "Total Unit Terjual": [total_solid, total_magic2, total_magic3],
    }
)

if grand_total_unit > 0:
    prod_sum["Kontribusi (%)"] = (
        prod_sum["Total Unit Terjual"] / grand_total_unit
    ) * 100
else:
    prod_sum["Kontribusi (%)"] = 0.0

prod_sum = prod_sum.sort_values(
    by="Total Unit Terjual", ascending=False
).reset_index(drop=True)
prod_sum["Peringkat"] = range(1, len(prod_sum) + 1)

prod_sum_table = prod_sum[
    ["Peringkat", "Model Rak", "Total Unit Terjual", "Kontribusi (%)"]
]

col_prod1, col_prod2 = st.columns(2)

with col_prod1:
    fig_prod, ax_prod = plt.subplots(figsize=(7, 3.8))
    bars = ax_prod.bar(
        prod_sum["Model Rak"],
        prod_sum["Total Unit Terjual"],
        color=["#3b82f6", "#f59e0b", "#8b5cf6"],
        width=0.45,
    )
    ax_prod.set_title(
        "Total Unit Terjual Berdasarkan Model Rak",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )
    ax_prod.set_ylabel("Jumlah Unit", fontsize=9)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    for bar in bars:
        yval = bar.get_height()
        ax_prod.text(
            bar.get_x() + bar.get_width() / 2,
            yval + max(1, yval * 0.02),
            f"{int(yval)}",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )
    st.pyplot(fig_prod)

with col_prod2:
    st.markdown(
        "<p style='font-weight: 600; font-size: 1.05rem; color: #1e293b; margin-top: 5px;'>Tabel Ringkasan & Peringkat Produk</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        prod_sum_table.style.format(
            {"Total Unit Terjual": "{:,}", "Kontribusi (%)": "{:.2f}%"}
        ),
        use_container_width=True,
