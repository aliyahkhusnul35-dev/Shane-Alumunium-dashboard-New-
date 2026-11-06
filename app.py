import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Dashboard Analisis Perilaku Pembelian - Shane Alumunium",
    page_icon="📊",
    layout="wide",
)

# ==========================================
# CUSTOM CSS - SOFT BLUE PROFESSIONAL THEME
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f4f7fb;
        color: #24364b;
    }
    .main-title {
        font-weight: 800;
        color: #142d4e;
        font-size: 1.85rem;
        margin-bottom: 0;
    }
    .sub-title {
        font-weight: 400;
        color: #64758b;
        font-size: .98rem;
        margin-bottom: 12px;
    }
    .section-header {
        font-weight: 700;
        color: #173b68;
        font-size: 1.12rem;
        margin-top: 22px;
        margin-bottom: 12px;
        border-bottom: 1px solid #dce5ef;
        padding-bottom: 7px;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 15px 16px;
        border-radius: 12px;
        border: 1px solid #e2e9f2;
        box-shadow: 0 2px 8px rgba(20, 45, 78, .05);
    }
    [data-testid="stMetricLabel"] {
        color: #64758b;
        font-size: .88rem !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #142d4e;
        font-size: 1.35rem !important;
        font-weight: 800;
    }
    .info-strip {
        background: #eaf1fa;
        border-left: 4px solid #3978c5;
        padding: 10px 14px;
        border-radius: 7px;
        color: #294563;
        font-size: .88rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e9f2;
        border-radius: 9px;
    }
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

all_months_options = ["Semua Bulan"] + sorted(
    df["Bulan_Transaksi"].dropna().unique().tolist()
)
selected_month_option = st.sidebar.selectbox(
    "Pilih Periode Bulan", options=all_months_options
)

all_payment_options = ["Semua Metode Pembayaran"] + sorted(
    df["Kategori_Pembayaran"].dropna().unique().tolist()
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

# Pencarian tetap diterapkan pada data dashboard seperti pada kode awal.
if search_query.strip():
    df_filtered = df_filtered[
        df_filtered["Pelanggan_Cleaned"].str.contains(
            search_query.strip().upper(), na=False
        )
    ]

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **Total Data Terpilih:** {len(df_filtered):,} baris")

# ==========================================
# BARIS 1: TREN PENJUALAN DAN JUMLAH TRANSAKSI
# ==========================================
st.markdown(
    '<p class="section-header">📈 1. Tren Penjualan</p>',
    unsafe_allow_html=True,
)
trend_df = (
    df_filtered.groupby("Bulan_Transaksi")
    .agg(
        Total_Penjualan=("Jumlah", "sum"),
        Jumlah_Transaksi=("Invoice", "count"),
    )
    .reset_index()
    .sort_values("Bulan_Transaksi")
)

col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    if not trend_df.empty:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        ax.plot(
            trend_df["Bulan_Transaksi"],
            trend_df["Total_Penjualan"] / 1e6,
            marker="o",
            color="#3978c5",
            linewidth=2.5,
            markersize=6,
        )
        ax.set_title(
            "Total Penjualan per Bulan (Juta Rupiah)",
            fontsize=11,
            fontweight="bold",
            pad=12,
        )
        ax.set_xlabel("Periode Bulan", fontsize=9)
        ax.set_ylabel("Penjualan (Juta Rp)", fontsize=9)
        plt.xticks(rotation=40, fontsize=8)
        plt.yticks(fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Tidak ada data tren penjualan.")

with col_trend2:
    if not trend_df.empty:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        bars = ax.bar(
            trend_df["Bulan_Transaksi"],
            trend_df["Jumlah_Transaksi"],
            color="#18a6a6",
            width=0.62,
        )
        ax.set_title(
            "Jumlah Transaksi per Bulan",
            fontsize=11,
            fontweight="bold",
            pad=12,
        )
        ax.set_xlabel("Periode Bulan", fontsize=9)
        ax.set_ylabel("Jumlah Transaksi", fontsize=9)
        plt.xticks(rotation=40, fontsize=8)
        plt.yticks(fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{int(bar.get_height())}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        "Kategori Produk": ["Rak Solid 2P", "Rak Magic 2P", "Rak Magic 3P"],
        "Total Unit Terjual": [
            df_filtered["Model Rak Solid 2p"].sum(),
            df_filtered["Model Rak Magic 2p"].sum(),
            df_filtered["Model Rak Magic 3p"].sum(),
        ],
    }
)
total_produk = prod_sum["Total Unit Terjual"].sum()
prod_sum["Kontribusi (%)"] = (
    prod_sum["Total Unit Terjual"] / total_produk * 100
    if total_produk > 0 else 0
)

col_prod1, col_prod2 = st.columns([1.25, 1])

with col_prod1:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = ax.barh(
        prod_sum["Kategori Produk"],
        prod_sum["Total Unit Terjual"],
        color=["#3978c5", "#18a6a6", "#8064c8"],
        height=0.55,
    )
    ax.set_title(
        "Total Unit Terjual Berdasarkan Model Rak",
        fontsize=11,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Jumlah Unit", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, pct in zip(bars, prod_sum["Kontribusi (%)"]):
        ax.text(
            bar.get_width() + max(1, total_produk * 0.01),
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f} unit ({pct:.1f}%)",
            va="center",
            fontsize=8,
        )
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_prod2:
    fig, ax = plt.subplots(figsize=(6, 3.8))
    if total_produk > 0:
        ax.pie(
            prod_sum["Total Unit Terjual"],
            labels=prod_sum["Kategori Produk"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#3978c5", "#18a6a6", "#8064c8"],
            wedgeprops={"width": 0.42, "edgecolor": "white"},
            textprops={"fontsize": 8},
        )
        ax.set_title(
            "Persentase Kontribusi Unit per Model",
            fontsize=11,
            fontweight="bold",
            pad=12,
        )
    else:
        ax.text(0.5, 0.5, "Tidak ada data produk", ha="center", va="center")
    ax.axis("equal")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.dataframe(
    prod_sum.style.format({
        "Total Unit Terjual": "{:,.0f}",
        "Kontribusi (%)": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True,
)


with st.expander("Lihat tabel lengkap RFM deskriptif"):
    rfm_display = rfm_table[
        ["Nama Pelanggan", "Recency (Hari)", "Frekuensi_Transaksi",
         "Total_Nilai_Pembelian", "Total_Unit_Dibeli"]
    ].copy()
    st.dataframe(
        rfm_display.style.format({
            "Recency (Hari)": "{:,.0f}",
            "Frekuensi_Transaksi": "{:,.0f}",
            "Total_Nilai_Pembelian": "Rp {:,.0f}",
            "Total_Unit_Dibeli": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Keterangan: Recency menunjukkan jarak hari sejak transaksi terakhir pelanggan "
    "hingga tanggal transaksi paling akhir pada data terpilih. Frequency adalah "
    "jumlah transaksi yang tercatat, sedangkan Monetary adalah total nilai pembelian."
)


# ==========================================
# 4. METODE PEMBAYARAN
# ==========================================
st.markdown(
    '<p class="section-header">💳 4. Metode Pembayaran</p>',
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
pay_sum["Rata_Rata_Penjualan"] = (
    pay_sum["Total_Penjualan"] / pay_sum["Jumlah_Transaksi"].replace(0, np.nan)
).fillna(0)
pay_sum["Proporsi_Transaksi (%)"] = (
    pay_sum["Jumlah_Transaksi"] / pay_sum["Jumlah_Transaksi"].sum() * 100
    if pay_sum["Jumlah_Transaksi"].sum() > 0 else 0
)

if not pay_sum.empty:
    col_pay1, col_pay2 = st.columns([1, 1.25])

    with col_pay1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(
            pay_sum["Jumlah_Transaksi"],
            labels=pay_sum["Kategori_Pembayaran"],
            autopct="%1.1f%%",
            startangle=140,
            colors=["#3978c5", "#e5a93d", "#64748b", "#18a6a6"],
            textprops={"fontsize": 8},
            wedgeprops={"edgecolor": "white", "linewidth": 1},
        )
        ax.set_title(
            "Proporsi Transaksi Pembayaran",
            fontsize=11,
            fontweight="bold",
            pad=12,
        )
        ax.axis("equal")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_pay2:
        st.markdown("**Tabel ringkasan metode pembayaran**")
        st.dataframe(
            pay_sum.style.format({
                "Jumlah_Transaksi": "{:,.0f}",
                "Total_Penjualan": "Rp {:,.0f}",
                "Cash_Diterima": "Rp {:,.0f}",
                "Kredit_Tempo": "Rp {:,.0f}",
                "Rata_Rata_Penjualan": "Rp {:,.0f}",
                "Proporsi_Transaksi (%)": "{:.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("Data pembayaran kosong.")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>"
    "© 2026 | Penelitian Skripsi Sistem Informasi - STMIK IKMI Cirebon"
    "</p>",
    unsafe_allow_html=True,
)
