import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0f1117; }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #2d3250;
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(79, 110, 245, 0.2);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4C6EF5;
        margin: 8px 0 4px;
    }
    .kpi-label { font-size: 0.85rem; color: #8892b0; }
    .kpi-icon  { font-size: 1.8rem; }
    
    /* Section header */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e0e6f0;
        border-left: 4px solid #4C6EF5;
        padding-left: 12px;
        margin: 24px 0 16px;
    }

    /* Business Question Box */
    .biz-question {
        background: linear-gradient(135deg, #1a1f35, #1e2540);
        border: 1px solid #3a4070;
        border-left: 4px solid #4C6EF5;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #c8d0e0;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .biz-question strong { color: #7b9fff; }
    
    /* Insight Box */
    .insight-box {
        background: linear-gradient(135deg, #1a2535, #1e2d40);
        border: 1px solid #2a4060;
        border-left: 4px solid #51CF66;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 16px;
        color: #b8d4c0;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .insight-box .insight-title {
        color: #51CF66;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141625 0%, #1a1d2e 100%);
        border-right: 1px solid #2d3250;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
    
    /* RFM badges */
    .badge-champions     { background: #2F9E44; color: white; padding: 3px 10px; border-radius: 999px; font-size:0.8rem; }
    .badge-loyal         { background: #1971C2; color: white; padding: 3px 10px; border-radius: 999px; font-size:0.8rem; }
    .badge-potential     { background: #F08C00; color: white; padding: 3px 10px; border-radius: 999px; font-size:0.8rem; }
    .badge-atrisk        { background: #E8590C; color: white; padding: 3px 10px; border-radius: 999px; font-size:0.8rem; }
    .badge-lost          { background: #C92A2A; color: white; padding: 3px 10px; border-radius: 999px; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/main_data.csv')
    date_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

main_df = load_data()

# ══════════════════════════════════════════════
# SIDEBAR – FILTERS
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛒 Olist Dashboard")
    st.markdown("**E-Commerce Brazil – Analisis Data**")
    st.markdown("---")

    # Date Range
    st.markdown("### 📅 Filter Tanggal")
    min_date = main_df['order_purchase_timestamp'].min().date()
    max_date = main_df['order_purchase_timestamp'].max().date()
    start_date, end_date = st.date_input(
        "Rentang Tanggal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # State filter
    st.markdown("### 🗺️ Filter State")
    all_states = sorted(main_df['customer_state'].dropna().unique().tolist())
    selected_states = st.multiselect("Negara Bagian", all_states, default=all_states)

    # Category filter
    st.markdown("### 📦 Filter Kategori")
    all_cats = sorted(main_df['product_category_name_english'].dropna().unique().tolist())
    selected_cats = st.multiselect("Kategori Produk", all_cats, default=all_cats[:20])

    st.markdown("---")
    st.markdown("*Data: Olist Brazil E-Commerce*\n\n*Dianalisis oleh: Salsabila Yufli Ramadhani*")

# Apply filters
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date) &
    (main_df['customer_state'].isin(selected_states))
]
if selected_cats:
    filtered_df = filtered_df[filtered_df['product_category_name_english'].isin(selected_cats)]

# ══════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════
st.markdown("# 🛒 E-Commerce Analytics Dashboard")
st.markdown("### Olist Brazil – Analisis Data Komprehensif")
st.markdown("---")

# ── Pertanyaan Bisnis ──
with st.expander("📋 Pertanyaan Bisnis (SMART)", expanded=False):
    questions = [
        ("Q1", "Bagaimana tren jumlah order dan total revenue bulanan selama periode <strong>Januari 2017 hingga Agustus 2018</strong>, dan pada bulan apa penjualan mencapai puncaknya?"),
        ("Q2", "Kategori produk apa yang menghasilkan <strong>revenue terbesar</strong> dan memiliki <strong>jumlah order terbanyak</strong> sepanjang tahun 2017–2018?"),
        ("Q3", "Berapa <strong>persentase pesanan yang terlambat</strong> dari estimasi pengiriman selama periode 2017–2018, dan seberapa besar <strong>perbedaan rata-rata skor ulasan</strong> antara pesanan yang terlambat dengan yang tepat waktu?"),
        ("Q4", "Berdasarkan analisis RFM terhadap data transaksi 2017–2018, berapa <strong>proporsi pelanggan di setiap segmen</strong> (Champions, Loyal Customers, Potential Loyalists, At Risk, Lost) dan berapa <strong>rata-rata nilai transaksi (monetary)</strong> dari segmen Champions dibandingkan segmen lainnya?"),
        ("Q5", "Negara bagian mana di Brazil yang menghasilkan <strong>total revenue</strong> dan <strong>jumlah pelanggan unik tertinggi</strong> selama periode 2017–2018, serta seberapa besar <strong>kontribusinya</strong> terhadap total revenue keseluruhan?"),
    ]
    for qnum, qtext in questions:
        st.markdown(f"""
        <div class="biz-question">
            <strong>{qnum}</strong> — {qtext}
        </div>""", unsafe_allow_html=True)

# ── KPI Cards ──
st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

total_orders   = filtered_df['order_id'].nunique()
total_revenue  = filtered_df['payment_value'].sum()
avg_rating     = filtered_df['review_score'].mean()
total_customers = filtered_df['customer_unique_id'].nunique()
late_pct       = filtered_df['is_late'].mean() * 100 if 'is_late' in filtered_df.columns else 0

kpis = [
    (col1, "📦", f"{total_orders:,}", "Total Orders"),
    (col2, "💰", f"R${total_revenue/1e6:.1f}M", "Total Revenue"),
    (col3, "⭐", f"{avg_rating:.2f}", "Avg Rating"),
    (col4, "👥", f"{total_customers:,}", "Total Customers"),
    (col5, "🚚", f"{late_pct:.1f}%", "Late Delivery"),
]
for col, icon, val, label in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tren Penjualan",
    "📦 Kategori Produk",
    "🚚 Performa Pengiriman",
    "🎯 RFM Analysis",
    "🗺️ Geospatial"
])

# ════════════ TAB 1: TREN PENJUALAN ════════════
with tab1:
    st.markdown('<div class="section-header">Q1 — Tren Jumlah Order & Revenue Bulanan (Jan 2017 – Agust 2018)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="biz-question">
        <strong>Pertanyaan:</strong> Bagaimana tren jumlah order dan total revenue bulanan selama periode 
        <strong>Januari 2017 hingga Agustus 2018</strong>, dan pada bulan apa penjualan mencapai puncaknya?
    </div>""", unsafe_allow_html=True)

    monthly = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('M')).agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('payment_value', 'sum')
    ).reset_index()
    monthly['order_month_str'] = monthly['order_purchase_timestamp'].astype(str)

    fig, ax1 = plt.subplots(figsize=(14, 5), facecolor='#1e2130')
    ax1.set_facecolor('#1e2130')

    x = range(len(monthly))
    bars = ax1.bar(x, monthly['total_orders'], color='#4C6EF5', alpha=0.85, width=0.6, label='Total Orders')
    ax1.set_ylabel('Jumlah Order', color='#4C6EF5', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='#4C6EF5')
    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly['order_month_str'], rotation=45, ha='right', color='#aab4c8', fontsize=8)
    ax1.tick_params(axis='x', colors='#aab4c8')
    ax1.set_xlabel('Bulan', color='#aab4c8', fontsize=11)
    for spine in ax1.spines.values():
        spine.set_edgecolor('#2d3250')

    ax2 = ax1.twinx()
    ax2.plot(x, monthly['total_revenue']/1e6, color='#FF6B6B', marker='o', linewidth=2.5, markersize=4, label='Revenue (Juta R$)')
    ax2.set_ylabel('Revenue (Juta R$)', color='#FF6B6B', fontsize=11)
    ax2.tick_params(axis='y', labelcolor='#FF6B6B')
    for spine in ax2.spines.values():
        spine.set_edgecolor('#2d3250')

    peak_idx_orders = None
    peak_idx_revenue = None
    if len(monthly) > 0:
        peak_idx_orders = monthly['total_orders'].idxmax()
        peak_idx_revenue = monthly['total_revenue'].idxmax()
        bars[peak_idx_orders].set_color('#FFD43B')
        # Annotate peak
        peak_val = monthly['total_orders'].max()
        ax1.annotate(f"Puncak\n{peak_val:,} orders",
                     xy=(peak_idx_orders, peak_val),
                     xytext=(peak_idx_orders + 1.5, peak_val * 0.9),
                     arrowprops=dict(arrowstyle='->', color='#FFD43B'),
                     color='#FFD43B', fontsize=8, fontweight='bold')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc='upper left', facecolor='#252840', labelcolor='white', fontsize=9)

    plt.title('Tren Jumlah Order & Revenue Bulanan (Jan 2017 – Agust 2018)', color='#e0e6f0', fontsize=14, fontweight='bold', pad=12)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Insight box
    if len(monthly) > 0:
        peak_month = monthly.loc[monthly['total_orders'].idxmax(), 'order_month_str']
        peak_rev_month = monthly.loc[monthly['total_revenue'].idxmax(), 'order_month_str']
        peak_orders_val = monthly['total_orders'].max()
        peak_rev_val = monthly['total_revenue'].max()
        growth_rate = ((monthly['total_orders'].iloc[-1] - monthly['total_orders'].iloc[0]) /
                       monthly['total_orders'].iloc[0] * 100) if monthly['total_orders'].iloc[0] > 0 else 0

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">📌 Insight – Tren Penjualan Bulanan</div>
            <ul style="margin:0; padding-left:18px;">
                <li>Puncak <strong>jumlah order</strong> terjadi pada bulan <strong>{peak_month}</strong> dengan <strong>{peak_orders_val:,} order</strong>, bertepatan dengan momen Black Friday/promo akhir tahun.</li>
                <li>Puncak <strong>revenue</strong> terjadi pada <strong>{peak_rev_month}</strong> dengan nilai <strong>R${peak_rev_val/1e6:.2f} juta</strong>.</li>
                <li>Secara keseluruhan, tren menunjukkan <strong>pertumbuhan positif</strong> dari awal hingga akhir periode, dengan pertumbuhan order sebesar <strong>{growth_rate:.1f}%</strong> dari bulan pertama ke bulan terakhir.</li>
                <li>Terdapat <strong>lonjakan signifikan</strong> pada Q4 2017, mengindikasikan seasonality kuat di akhir tahun yang perlu dimanfaatkan untuk strategi stok dan kampanye promosi.</li>
            </ul>
        </div>""", unsafe_allow_html=True)

# ════════════ TAB 2: KATEGORI PRODUK ════════════
with tab2:
    st.markdown('<div class="section-header">Q2 — Kategori Produk Terlaris (2017–2018)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="biz-question">
        <strong>Pertanyaan:</strong> Kategori produk apa yang menghasilkan <strong>revenue terbesar</strong> 
        dan memiliki <strong>jumlah order terbanyak</strong> sepanjang tahun 2017–2018?
    </div>""", unsafe_allow_html=True)

    category_analysis = filtered_df.groupby('product_category_name_english').agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('payment_value', 'sum'),
        avg_price=('price', 'mean')
    ).reset_index()

    top_n = st.slider("Tampilkan Top N Kategori:", min_value=5, max_value=20, value=10, step=1)
    sort_by = st.radio("Urutkan berdasarkan:", ["Total Revenue", "Jumlah Order"], horizontal=True)

    if sort_by == "Total Revenue":
        top_cats = category_analysis.sort_values('total_revenue', ascending=False).head(top_n)
        x_col, x_label = 'total_revenue', 'Total Revenue (R$)'
        x_vals = top_cats[x_col] / 1e6
        x_axis_label = 'Revenue (Juta R$)'
    else:
        top_cats = category_analysis.sort_values('total_orders', ascending=False).head(top_n)
        x_col, x_label = 'total_orders', 'Jumlah Order'
        x_vals = top_cats[x_col]
        x_axis_label = 'Jumlah Order'

    fig, ax = plt.subplots(figsize=(12, max(5, top_n*0.5)), facecolor='#1e2130')
    ax.set_facecolor('#1e2130')
    palette = sns.color_palette('Blues_r', top_n)
    y_labels = top_cats['product_category_name_english'].values[::-1]
    x_data   = x_vals.values[::-1]
    bars = ax.barh(y_labels, x_data, color=palette, edgecolor='none')
    # Add value labels
    for bar, val in zip(bars, x_data):
        ax.text(bar.get_width() + bar.get_width()*0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}' if sort_by == 'Total Revenue' else f'{int(val):,}',
                va='center', fontsize=8, color='#aab4c8')
    ax.set_xlabel(x_axis_label, color='#aab4c8', fontsize=11)
    ax.tick_params(colors='#aab4c8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2d3250')
    ax.set_title(f'Top {top_n} Kategori Produk – {x_label} (2017–2018)', color='#e0e6f0', fontsize=13, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Insight
    top1_cat = category_analysis.sort_values('total_revenue', ascending=False).iloc[0]
    top1_order = category_analysis.sort_values('total_orders', ascending=False).iloc[0]
    top3_rev = category_analysis.sort_values('total_revenue', ascending=False).head(3)
    top3_contrib = top3_rev['total_revenue'].sum() / category_analysis['total_revenue'].sum() * 100

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">📌 Insight – Kategori Produk Terlaris</div>
        <ul style="margin:0; padding-left:18px;">
            <li>Kategori <strong>{top1_cat['product_category_name_english']}</strong> menghasilkan revenue tertinggi sebesar <strong>R${top1_cat['total_revenue']/1e6:.2f} juta</strong> selama 2017–2018.</li>
            <li>Kategori <strong>{top1_order['product_category_name_english']}</strong> memiliki jumlah order terbanyak dengan <strong>{int(top1_order['total_orders']):,} order</strong>.</li>
            <li>Top 3 kategori berdasarkan revenue secara kumulatif berkontribusi <strong>{top3_contrib:.1f}%</strong> dari total revenue keseluruhan.</li>
            <li>Produk rumah tangga (<em>bed_bath_table</em>), perawatan diri (<em>health_beauty</em>), dan gaya hidup aktif (<em>sports_leisure</em>) mendominasi, mengindikasikan bahwa kebutuhan sehari-hari adalah segmen paling kuat di platform Olist.</li>
        </ul>
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 Lihat Data Lengkap"):
        st.dataframe(top_cats.rename(columns={
            'product_category_name_english': 'Kategori',
            'total_orders': 'Total Order',
            'total_revenue': 'Total Revenue (R$)',
            'avg_price': 'Avg Price (R$)'
        }).style.format({'Total Revenue (R$)': 'R${:,.0f}', 'Avg Price (R$)': 'R${:,.0f}'}),
        use_container_width=True)

# ════════════ TAB 3: PENGIRIMAN ════════════
with tab3:
    st.markdown('<div class="section-header">Q3 — Performa Pengiriman & Dampak terhadap Review Score</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="biz-question">
        <strong>Pertanyaan:</strong> Berapa <strong>persentase pesanan yang terlambat</strong> dari estimasi pengiriman 
        selama periode 2017–2018, dan seberapa besar <strong>perbedaan rata-rata skor ulasan</strong> antara pesanan 
        yang terlambat dengan yang tepat waktu?
    </div>""", unsafe_allow_html=True)

    delivery_df = filtered_df.dropna(subset=['order_delivered_customer_date', 'review_score', 'is_late'])

    # Metrics row
    late_count   = int(delivery_df['is_late'].sum())
    ontime_count = int((delivery_df['is_late'] == 0).sum())
    late_pct_val = delivery_df['is_late'].mean() * 100
    avg_score_late   = delivery_df[delivery_df['is_late'] == 1]['review_score'].mean()
    avg_score_ontime = delivery_df[delivery_df['is_late'] == 0]['review_score'].mean()
    score_diff = avg_score_ontime - avg_score_late

    m1, m2, m3, m4 = st.columns(4)
    metric_style = lambda color: f"background:linear-gradient(135deg,#1e2130,#252840);border:1px solid {color}40;border-radius:12px;padding:16px;text-align:center;"
    for col, icon, val, lbl, color in [
        (m1, "📦", f"{late_pct_val:.1f}%", "Tingkat Keterlambatan", "#FF6B6B"),
        (m2, "✅", f"{ontime_count:,}", "Tepat Waktu", "#51CF66"),
        (m3, "⚠️", f"{late_count:,}", "Terlambat", "#FF6B6B"),
        (m4, "📉", f"{score_diff:.2f} poin", "Selisih Review Score", "#FFD43B"),
    ]:
        with col:
            st.markdown(f"""
            <div style="{metric_style(color)}">
                <div style="font-size:1.6rem">{icon}</div>
                <div style="font-size:1.4rem;font-weight:700;color:{color};margin:4px 0">{val}</div>
                <div style="font-size:0.8rem;color:#8892b0">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        late_counts = delivery_df['is_late'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1e2130')
        ax.set_facecolor('#1e2130')
        labels = ['Tepat Waktu', 'Terlambat']
        colors_pie = ['#51CF66', '#FF6B6B']
        wedges, texts, autotexts = ax.pie(
            late_counts.values, labels=labels, colors=colors_pie,
            autopct='%1.1f%%', startangle=90, textprops={'color': 'white', 'fontsize': 12},
            wedgeprops={'edgecolor': '#1e2130', 'linewidth': 2}
        )
        for autotext in autotexts:
            autotext.set_fontweight('bold')
        ax.set_title('Proporsi Keterlambatan Pengiriman\n(2017–2018)', color='#e0e6f0', fontsize=12, fontweight='bold')
        st.pyplot(fig)
        plt.close()

    with colB:
        review_data = delivery_df.groupby('is_late')['review_score'].mean().reset_index()
        review_data['label'] = review_data['is_late'].map({0: 'Tepat Waktu', 1: 'Terlambat'})
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1e2130')
        ax.set_facecolor('#1e2130')
        colors_bar = ['#51CF66', '#FF6B6B']
        bars = ax.bar(review_data['label'], review_data['review_score'], color=colors_bar, width=0.4, edgecolor='none')
        ax.set_ylim(0, 5.8)
        ax.set_ylabel('Avg Review Score', color='#aab4c8', fontsize=11)
        ax.tick_params(colors='#aab4c8')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2d3250')
        ax.axhline(y=4, color='white', linestyle='--', alpha=0.3, linewidth=1, label='Skor 4.0')
        # Annotate bars
        for bar, val in zip(bars, review_data['review_score']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
                    f'{val:.2f} ⭐', ha='center', fontsize=12, fontweight='bold', color='white')
        # Annotate difference
        if len(review_data) == 2:
            y1 = review_data['review_score'].iloc[0]
            y2 = review_data['review_score'].iloc[1]
            ax.annotate('', xy=(1, y2 + 0.3), xytext=(0, y1 + 0.3),
                        arrowprops=dict(arrowstyle='<->', color='#FFD43B', lw=2))
            ax.text(0.5, max(y1, y2) + 0.5, f'Δ {abs(y1-y2):.2f}',
                    ha='center', fontsize=10, color='#FFD43B', fontweight='bold')
        ax.set_title('Perbedaan Review Score:\nTepat Waktu vs Terlambat', color='#e0e6f0', fontsize=12, fontweight='bold')
        st.pyplot(fig)
        plt.close()

    # Distribusi waktu pengiriman
    delivery_df2 = filtered_df.dropna(subset=['order_delivered_customer_date', 'order_purchase_timestamp']).copy()
    delivery_df2['delivery_days'] = (
        delivery_df2['order_delivered_customer_date'] - delivery_df2['order_purchase_timestamp']
    ).dt.days

    st.markdown('<div class="section-header">Distribusi Waktu Pengiriman (Hari)</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 4), facecolor='#1e2130')
    ax.set_facecolor('#1e2130')
    delivery_df2['delivery_days'].clip(0, 60).hist(bins=40, ax=ax, color='#4C6EF5', edgecolor='none', alpha=0.85)
    median_days = delivery_df2['delivery_days'].median()
    mean_days   = delivery_df2['delivery_days'].mean()
    ax.axvline(median_days, color='#FFD43B', linestyle='--', linewidth=2, label=f"Median: {median_days:.0f} hari")
    ax.axvline(mean_days,   color='#FF6B6B', linestyle=':', linewidth=2, label=f"Mean: {mean_days:.0f} hari")
    ax.set_xlabel('Hari Pengiriman', color='#aab4c8', fontsize=11)
    ax.set_ylabel('Frekuensi', color='#aab4c8', fontsize=11)
    ax.tick_params(colors='#aab4c8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2d3250')
    ax.legend(facecolor='#252840', labelcolor='white')
    ax.set_title('Distribusi Waktu Pengiriman (dalam hari sejak pembelian)', color='#e0e6f0', fontsize=12, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">📌 Insight – Performa Pengiriman</div>
        <ul style="margin:0; padding-left:18px;">
            <li>Sebesar <strong>{late_pct_val:.1f}%</strong> dari total pesanan mengalami keterlambatan melampaui estimasi pengiriman yang diberikan kepada pelanggan.</li>
            <li>Pesanan <strong>tepat waktu</strong> mendapatkan rata-rata skor ulasan <strong>{avg_score_ontime:.2f}/5</strong>, sedangkan pesanan <strong>terlambat</strong> hanya mendapat <strong>{avg_score_late:.2f}/5</strong> — selisih sebesar <strong>{score_diff:.2f} poin ({score_diff/avg_score_ontime*100:.1f}% lebih rendah)</strong>.</li>
            <li>Median waktu pengiriman adalah <strong>{median_days:.0f} hari</strong> dengan rata-rata <strong>{mean_days:.0f} hari</strong>, menunjukkan distribusi yang cukup bervariasi dan ada pesanan dengan waktu pengiriman sangat panjang sebagai outlier.</li>
            <li>Keterlambatan pengiriman adalah faktor kritis yang secara langsung menurunkan kepuasan pelanggan. Peningkatan 1% dalam tingkat pengiriman tepat waktu berpotensi meningkatkan rata-rata review score secara keseluruhan.</li>
        </ul>
    </div>""", unsafe_allow_html=True)

# ════════════ TAB 4: RFM ════════════
with tab4:
    st.markdown('<div class="section-header">Q4 — Segmentasi Pelanggan RFM (2017–2018)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="biz-question">
        <strong>Pertanyaan:</strong> Berdasarkan analisis RFM (Recency, Frequency, Monetary) terhadap data transaksi 2017–2018, 
        berapa <strong>proporsi pelanggan di setiap segmen</strong> dan berapa <strong>rata-rata nilai transaksi (monetary)</strong> 
        dari segmen Champions dibandingkan segmen lainnya?
    </div>""", unsafe_allow_html=True)
    st.markdown("Segmentasi pelanggan berdasarkan **R**ecency, **F**requency, dan **M**onetary value.")

    rfm_df = filtered_df.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda x: (filtered_df['order_purchase_timestamp'].max() - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('payment_value', 'sum')
    ).reset_index()

    if len(rfm_df) > 0:
        try:
            rfm_df['r_score'] = pd.qcut(rfm_df['recency'], 5, labels=[5,4,3,2,1], duplicates='drop').astype(int)
            rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
            rfm_df['m_score'] = pd.qcut(rfm_df['monetary'], 5, labels=[1,2,3,4,5], duplicates='drop').astype(int)
            rfm_df['rfm_score'] = rfm_df['r_score'] + rfm_df['f_score'] + rfm_df['m_score']

            def segment(row):
                score = row['rfm_score']
                if score >= 13:   return 'Champions'
                elif score >= 10: return 'Loyal Customers'
                elif score >= 7:  return 'Potential Loyalists'
                elif score >= 5:  return 'At Risk'
                else:             return 'Lost'

            rfm_df['segment'] = rfm_df.apply(segment, axis=1)

            seg_colors = {
                'Champions': '#2F9E44', 'Loyal Customers': '#1971C2',
                'Potential Loyalists': '#F08C00', 'At Risk': '#E8590C', 'Lost': '#C92A2A'
            }

            seg_summary = rfm_df.groupby('segment').agg(
                jumlah=('customer_unique_id', 'count'),
                avg_recency=('recency', 'mean'),
                avg_frequency=('frequency', 'mean'),
                avg_monetary=('monetary', 'mean')
            ).reset_index()

            # KPIs per segmen
            seg_order = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'At Risk', 'Lost']
            cols_rfm = st.columns(5)
            for i, seg in enumerate(seg_order):
                seg_data = seg_summary[seg_summary['segment'] == seg]
                if len(seg_data) > 0:
                    count = int(seg_data['jumlah'].values[0])
                    pct   = count / len(rfm_df) * 100
                    avg_m = seg_data['avg_monetary'].values[0]
                else:
                    count, pct, avg_m = 0, 0, 0
                color = seg_colors.get(seg, '#888')
                with cols_rfm[i]:
                    st.markdown(f"""
                    <div class="kpi-card" style="border-color:{color}40;">
                        <div style="color:{color}; font-size:1.5rem; font-weight:700;">{count:,}</div>
                        <div style="color:{color}; font-size:0.75rem; font-weight:600;">{seg}</div>
                        <div class="kpi-label">{pct:.1f}% pelanggan</div>
                        <div style="color:#aab4c8; font-size:0.72rem; margin-top:4px;">Avg R${avg_m:,.0f}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            colR1, colR2 = st.columns(2)

            with colR1:
                fig, ax = plt.subplots(figsize=(7, 5), facecolor='#1e2130')
                ax.set_facecolor('#1e2130')
                seg_plot = seg_summary.set_index('segment').reindex(seg_order).reset_index().dropna()
                bar_colors = [seg_colors.get(s, '#888') for s in seg_plot['segment']]
                bars = ax.bar(seg_plot['segment'], seg_plot['jumlah'], color=bar_colors, edgecolor='none')
                # Add percentage labels
                total_cust = seg_plot['jumlah'].sum()
                ax.set_ylabel('Jumlah Pelanggan', color='#aab4c8', fontsize=10)
                ax.tick_params(colors='#aab4c8', axis='x', rotation=25)
                ax.tick_params(colors='#aab4c8', axis='y')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#2d3250')
                for bar, val in zip(bars, seg_plot['jumlah']):
                    pct_lbl = val / total_cust * 100
                    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                            f'{int(val):,}\n({pct_lbl:.1f}%)', ha='center', fontsize=8, color='white', fontweight='bold')
                ax.set_title('Proporsi Segmen Pelanggan (RFM)', color='#e0e6f0', fontsize=12, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

            with colR2:
                # Avg monetary per segment
                seg_monetary = seg_summary.set_index('segment').reindex(seg_order).reset_index().dropna()
                bar_colors2 = [seg_colors.get(s, '#888') for s in seg_monetary['segment']]
                fig, ax = plt.subplots(figsize=(7, 5), facecolor='#1e2130')
                ax.set_facecolor('#1e2130')
                bars2 = ax.bar(seg_monetary['segment'], seg_monetary['avg_monetary'], color=bar_colors2, edgecolor='none')
                ax.set_ylabel('Avg Monetary (R$)', color='#aab4c8', fontsize=10)
                ax.tick_params(colors='#aab4c8', axis='x', rotation=25)
                ax.tick_params(colors='#aab4c8', axis='y')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#2d3250')
                for bar, val in zip(bars2, seg_monetary['avg_monetary']):
                    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
                            f'R${val:,.0f}', ha='center', fontsize=8, color='white', fontweight='bold')
                ax.set_title('Rata-rata Nilai Transaksi (Monetary)\nper Segmen Pelanggan', color='#e0e6f0', fontsize=12, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

            # Scatter Recency vs Monetary
            st.markdown('<div class="section-header">Sebaran Recency vs Monetary per Segmen</div>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(12, 5), facecolor='#1e2130')
            ax.set_facecolor('#1e2130')
            for seg, color in seg_colors.items():
                mask = rfm_df['segment'] == seg
                ax.scatter(rfm_df[mask]['recency'], rfm_df[mask]['monetary'],
                           c=color, label=seg, alpha=0.4, s=8)
            ax.set_xlabel('Recency (hari sejak terakhir order)', color='#aab4c8', fontsize=10)
            ax.set_ylabel('Monetary (R$)', color='#aab4c8', fontsize=10)
            ax.tick_params(colors='#aab4c8')
            for spine in ax.spines.values():
                spine.set_edgecolor('#2d3250')
            ax.legend(fontsize=9, facecolor='#252840', labelcolor='white', markerscale=3)
            ax.set_yscale('log')
            ax.set_title('Recency vs Monetary per Segmen Pelanggan', color='#e0e6f0', fontsize=12, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            # Insight
            champ_data = seg_summary[seg_summary['segment'] == 'Champions']
            lost_data   = seg_summary[seg_summary['segment'] == 'Lost']
            atrisk_data = seg_summary[seg_summary['segment'] == 'At Risk']
            champ_monetary = champ_data['avg_monetary'].values[0] if len(champ_data) > 0 else 0
            champ_pct      = champ_data['jumlah'].values[0] / len(rfm_df) * 100 if len(champ_data) > 0 else 0
            atrisk_pct     = atrisk_data['jumlah'].values[0] / len(rfm_df) * 100 if len(atrisk_data) > 0 else 0

            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">📌 Insight – Segmentasi RFM Pelanggan</div>
                <ul style="margin:0; padding-left:18px;">
                    <li>Segmen <strong>Champions</strong> mencakup <strong>{champ_pct:.1f}%</strong> dari total pelanggan dengan rata-rata nilai transaksi tertinggi sebesar <strong>R${champ_monetary:,.0f}</strong> per pelanggan.</li>
                    <li>Segmen <strong>At Risk</strong> (~{atrisk_pct:.1f}% pelanggan) adalah prioritas utama untuk strategi <em>re-engagement</em> — mereka pernah aktif namun kini mulai jarang bertransaksi.</li>
                    <li>Segmen <strong>Champions</strong> memiliki recency rendah (baru-baru ini bertransaksi) dan monetary tinggi, terlihat jelas di scatter plot kiri bawah dengan nilai R$ tinggi.</li>
                    <li>Mayoritas pelanggan berada di segmen <strong>Potential Loyalists</strong> dan <strong>At Risk</strong>, menandakan peluang besar untuk konversi ke segmen yang lebih tinggi melalui program loyalitas yang tepat sasaran.</li>
                </ul>
            </div>""", unsafe_allow_html=True)

            # Table
            with st.expander("📋 Detail Statistik per Segmen"):
                st.dataframe(seg_summary.rename(columns={
                    'segment': 'Segmen', 'jumlah': 'Jumlah Pelanggan',
                    'avg_recency': 'Avg Recency (hari)', 'avg_frequency': 'Avg Frequency',
                    'avg_monetary': 'Avg Monetary (R$)'
                }).style.format({
                    'Avg Recency (hari)': '{:.0f}', 'Avg Frequency': '{:.1f}', 'Avg Monetary (R$)': 'R${:,.0f}'
                }), use_container_width=True)

        except Exception as e:
            st.warning(f"RFM tidak dapat dihitung dengan filter saat ini: {e}")

# ════════════ TAB 5: GEOSPATIAL ════════════
with tab5:
    st.markdown('<div class="section-header">Q5 — Distribusi Geografis Pelanggan & Revenue (2017–2018)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="biz-question">
        <strong>Pertanyaan:</strong> Negara bagian mana di Brazil yang menghasilkan <strong>total revenue</strong> dan 
        <strong>jumlah pelanggan unik tertinggi</strong> selama periode 2017–2018, serta seberapa besar 
        <strong>kontribusinya</strong> terhadap total revenue keseluruhan?
    </div>""", unsafe_allow_html=True)

    @st.cache_data
    def load_geo():
        # Membaca file geo_customers.csv yang sudah di-pre-process
        # (merge customers + geolocation, sudah disimpan di folder dashboard/)
        return pd.read_csv('dashboard/geo_customers.csv')

    try:
        customers_geo = load_geo()
        if selected_states and len(selected_states) < len(all_states):
            customers_geo = customers_geo[customers_geo['customer_state'].isin(selected_states)]

        # State revenue & customer analysis
        state_rev  = filtered_df.groupby('customer_state')['payment_value'].sum().reset_index()
        state_cust = filtered_df.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
        state_analysis = state_rev.merge(state_cust, on='customer_state')
        state_analysis.columns = ['state', 'total_revenue', 'total_customers']
        state_analysis = state_analysis.sort_values('total_revenue', ascending=False)
        total_rev_all = state_analysis['total_revenue'].sum()
        state_analysis['revenue_pct'] = state_analysis['total_revenue'] / total_rev_all * 100

        # Metrics row
        top1_state = state_analysis.iloc[0]
        top3_states = state_analysis.head(3)
        top3_rev_pct = top3_states['total_revenue'].sum() / total_rev_all * 100

        m1, m2, m3 = st.columns(3)
        for col, icon, val, lbl, color in [
            (m1, "🏆", top1_state['state'], "State Revenue Tertinggi", "#FFD43B"),
            (m2, "💰", f"R${top1_state['total_revenue']/1e6:.1f}M ({top1_state['revenue_pct']:.1f}%)", "Revenue & Kontribusi #1", "#4C6EF5"),
            (m3, "📊", f"{top3_rev_pct:.1f}%", "Kontribusi Top 3 State", "#51CF66"),
        ]:
            with col:
                st.markdown(f"""
                <div class="kpi-card" style="border-color:{color}40;">
                    <div style="font-size:1.5rem">{icon}</div>
                    <div style="font-size:1.3rem;font-weight:700;color:{color};margin:4px 0">{val}</div>
                    <div style="font-size:0.8rem;color:#8892b0">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_geo1, col_geo2 = st.columns([2, 1])

        with col_geo1:
            st.markdown("##### 🗺️ Heatmap Distribusi Pelanggan di Brazil")
            sample = customers_geo.sample(min(3000, len(customers_geo)), random_state=42)
            m = folium.Map(location=[-14.235, -51.925], zoom_start=4, tiles='CartoDB dark_matter')
            heat_data = sample[['geolocation_lat','geolocation_lng']].dropna().values.tolist()
            HeatMap(heat_data, radius=12, blur=18, max_zoom=13,
                    gradient={0.2:'blue', 0.4:'cyan', 0.6:'lime', 0.8:'orange', 1.0:'red'}).add_to(m)
            st_folium(m, width=700, height=450)

        with col_geo2:
            st.markdown("##### 📊 Revenue & Pelanggan per State (Top 10)")
            top10 = state_analysis.head(10)
            fig, axes = plt.subplots(2, 1, figsize=(5, 8), facecolor='#1e2130')
            for ax in axes:
                ax.set_facecolor('#1e2130')

            # Revenue chart
            colors_v = sns.color_palette('viridis', len(top10))
            axes[0].barh(top10['state'][::-1], top10['total_revenue'][::-1]/1e6, color=colors_v[::-1], edgecolor='none')
            axes[0].set_xlabel('Revenue (Juta R$)', color='#aab4c8', fontsize=8)
            axes[0].tick_params(colors='#aab4c8', labelsize=8)
            for spine in axes[0].spines.values():
                spine.set_edgecolor('#2d3250')
            # Add contribution %
            for i, (rev, pct) in enumerate(zip(top10['total_revenue'][::-1]/1e6, top10['revenue_pct'][::-1])):
                axes[0].text(rev + 0.5, i, f'{pct:.1f}%', va='center', fontsize=7, color='#aab4c8')
            axes[0].set_title('Top 10 State – Revenue', color='#e0e6f0', fontsize=10, fontweight='bold')

            # Customer chart
            colors_m = sns.color_palette('magma', len(top10))
            axes[1].barh(top10['state'][::-1], top10['total_customers'][::-1], color=colors_m[::-1], edgecolor='none')
            axes[1].set_xlabel('Jumlah Pelanggan Unik', color='#aab4c8', fontsize=8)
            axes[1].tick_params(colors='#aab4c8', labelsize=8)
            for spine in axes[1].spines.values():
                spine.set_edgecolor('#2d3250')
            axes[1].set_title('Top 10 State – Pelanggan Unik', color='#e0e6f0', fontsize=10, fontweight='bold')

            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        # Insight
        top2_state = state_analysis.iloc[1] if len(state_analysis) > 1 else None
        top3_state = state_analysis.iloc[2] if len(state_analysis) > 2 else None

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">📌 Insight – Distribusi Geografis Pelanggan & Revenue</div>
            <ul style="margin:0; padding-left:18px;">
                <li>Negara bagian <strong>{top1_state['state']}</strong> mendominasi dengan revenue sebesar <strong>R${top1_state['total_revenue']/1e6:.1f} juta</strong>, berkontribusi <strong>{top1_state['revenue_pct']:.1f}%</strong> dari total revenue seluruh Brazil selama 2017–2018.</li>
                <li>Posisi kedua ditempati <strong>{top2_state['state'] if top2_state is not None else '-'}</strong> dan ketiga <strong>{top3_state['state'] if top3_state is not None else '-'}</strong>. Gabungan top 3 state berkontribusi <strong>{top3_rev_pct:.1f}%</strong> dari total revenue keseluruhan.</li>
                <li>Distribusi pelanggan sangat terkonsentrasi di wilayah <strong>tenggara Brazil</strong> (terutama sekitar kota São Paulo dan Rio de Janeiro), terlihat jelas dari heatmap dengan intensitas warna merah-oranye.</li>
                <li>Ketimpangan distribusi geografis ini menunjukkan <strong>peluang ekspansi yang signifikan</strong> ke wilayah lain seperti Nordeste dan Sul yang masih memiliki penetrasi e-commerce rendah relatif terhadap populasinya.</li>
            </ul>
        </div>""", unsafe_allow_html=True)

        with st.expander("📋 Lihat Data Revenue per State"):
            st.dataframe(
                state_analysis.rename(columns={'state':'State','total_revenue':'Total Revenue (R$)','total_customers':'Pelanggan Unik','revenue_pct':'Kontribusi (%)'})
                .style.format({'Total Revenue (R$)': 'R${:,.0f}', 'Kontribusi (%)': '{:.2f}%'}),
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Gagal load data geolokasi: {e}")

# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#555; font-size:0.85rem; padding:16px 0;">
    🛒 <strong>Olist E-Commerce Analytics Dashboard</strong> &nbsp;|&nbsp;
    Dibuat oleh <strong>Salsabila Yufli Ramadhani</strong> &nbsp;|&nbsp;
    📧 salsabilayufliramadhani@gmail.com &nbsp;|&nbsp;
    Proyek Akhir: Belajar Analisis Data dengan Python – Dicoding
</div>
""", unsafe_allow_html=True)
