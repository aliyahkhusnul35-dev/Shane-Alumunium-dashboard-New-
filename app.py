import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman Dashboard (Soft Blue Theme sesuai preferensi visual)
st.set_page_config(
    page_title="Dashboard Analisis Perilaku Pembelian - Shane Alumunium",
    page_icon="📊",
    layout="wide",
)

# Custom CSS untuk memperindah tampilan dashboard
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Memuat Data yang Telah Dibersihkan
@st.cache_data
def load_data():
    file_path = "Data Penjualan Gabungan Nov 2025-Sept 2026.xlsx"
    df = pd.read_excel(file_path, sheet_name="NOV 2025-SEPT 2026")

    # Preprocessing dasar untuk dashboard
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

    # Normalisasi Nama Pelanggan & Kategori Pembayaran
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


df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("🔍 Filter Dashboard")
st.sidebar.markdown(
    "Gunakan filter di bawah untuk meninjau data secara interaktif."
)

# Filter Rentang Bulan / Periode
all_months = sorted(df["Bulan_Transaksi"].unique())
selected_months = st.sidebar.multiselect(
    "Pilih Bulan Transaksi", options=all_months, default=all_months
)

# Filter Kategori Pembayaran
all_payments = sorted(df["Kategori_Pembayaran"].unique())
selected_payments = st.sidebar.multiselect(
    "Pilih Metode Pembayaran", options=all_payments, default=all_payments
)

# Terapkan Filter ke DataFrame
df_filtered = df[
    df["Bulan_Transaksi"].isin(selected_months)
    & df["Kategori_Pembayaran"].isin(selected_payments)
]

# --- HEADER UTAMA ---
st.title("📊 Dashboard Business Intelligence: Analisis Perilaku Pembelian Pelanggan")
st.subheader("Studi Kasus: Shane Alumunium (Periode November 2025 - September 2026)")
st.markdown("---")

# --- INDIKATOR UTAMA (METRICS) ---
total_penjualan = df_filtered["Jumlah"].sum()
total_transaksi = df_filtered["Invoice"].count()
total_unit_terjual = df_filtered["Total Unit"].sum()
total_pelanggan_aktif = df_filtered["Pelanggan_Cleaned"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Nilai Penjualan", f"Rp {total_penjualan:,.0f}")
col2.metric("Jumlah Transaksi", f"{total_transaksi:,} Invoice")
col3.metric("Total Unit Terjual", f"{total_unit_terjual:,} Unit")
col4.metric("Pelanggan Aktif", f"{total_pelanggan_aktif:,} Toko")

st.markdown("---")

# --- TABS UNTUK STRUKTUR ANALISIS ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Tren Penjualan", "📦 Analisis Produk", "👥 Perilaku Pelanggan", "💳 Analisis Pembayaran"]
)

with tab1:
    st.markdown("### Analisis Tren Penjualan Bulanan")
    st.markdown(
        "Grafik berikut menunjukkan fluktuasi nilai penjualan total ($TS = \sum V_i$) selama periode pengamatan."
    )

    trend_df = (
        df_filtered.groupby("Bulan_Transaksi")
        .agg(Total_Penjualan=("Jumlah", "sum"), Jumlah_Transaksi=("Invoice", "count"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(
        trend_df["Bulan_Transaksi"],
        trend_df["Total_Penjualan"] / 1e6,
        marker="o",
        color="#2b5c8f",
        linewidth=2.5,
    )
    ax.set_title("Tren Nilai Penjualan Bulanan (Dalam Juta Rupiah)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Bulan", fontsize=10)
    ax.set_ylabel("Total Penjualan (Juta Rp)", fontsize=10)
    plt.xticks(rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

    with st.expander("Lihat Tabel Ringkasan Tren Penjualan"):
        st.dataframe(
            trend_df.style.format({"Total_Penjualan": "Rp {:,.2f}"}),
            use_container_width=True,
        )

with tab2:
    st.markdown("### Analisis Kontribusi Produk")
    st.markdown("Perbandingan total unit terjual ($TQ = \sum Q_i$) untuk setiap model rak.")

    prod_sum = pd.DataFrame(
        {
            "Kategori Produk": [
                "Model Rak Solid 2P",
                "Model Rak Magic 2P",
                "Model Rak Magic 3P",
            ],
            "Total Unit Terjual": [
                df_filtered["Model Rak Solid 2p"].sum(),
                df_filtered["Model Rak Magic 2p"].sum(),
                df_filtered["Model Rak Magic 3p"].sum(),
            ],
        }
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(
        prod_sum["Kategori Produk"],
        prod_sum["Total Unit Terjual"],
        color=["#4B89DC", "#34A853", "#FBBC05"],
        width=0.5,
    )
    ax.set_title("Total Unit Terjual Berdasarkan Model Produk", fontsize=12, fontweight="bold")
    ax.set_ylabel("Total Unit", fontsize=10)
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 10,
            f"{int(yval)}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    st.pyplot(fig)

    st.dataframe(prod_sum, use_container_width=True)

with tab3:
    st.markdown("### Analisis Perilaku Pembelian Pelanggan (RFM Deskriptif)")
    st.markdown(
        "Pengelompokan transaksi berdasarkan pelanggan untuk melihat frekuensi pembelian ($F_j$) dan total nilai pembelian ($M_j$)."
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
        rfm_table.head(15).style.format({"Total_Nilai_Pembelian": "Rp {:,.2f}"}),
        use_container_width=True,
    )

with tab4:
    st.markdown("### Analisis Metode Pembayaran")
    st.markdown(
        "Distribusi transaksi antara pembayaran tunai/transfer, kredit/tempo, dan giro."
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

    col_a, col_b = st.columns(2)
    with col_a:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(
            pay_sum["Jumlah_Transaksi"],
            labels=pay_sum["Kategori_Pembayaran"],
            autopct="%1.1f%%",
            startangle=140,
            colors=["#4682B4", "#CD853F", "#708090", "#DAA520"],
        )
        ax.set_title("Proporsi Transaksi Berdasarkan Pembayaran", fontsize=11, fontweight="bold")
        st.pyplot(fig)

    with col_b:
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
    "<p style='text-align: center; color: gray;'>© 2026 | Penelitian Skripsi Sistem Informasi - STMIK IKMI Cirebon</p>",
    unsafe_allow_html=True,
)
