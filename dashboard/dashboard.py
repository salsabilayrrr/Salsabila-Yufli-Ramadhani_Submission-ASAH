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
    st.markdown('<div class="section-header">Tren Jumlah Order & Revenue Bulanan</div>', unsafe_allow_html=True)

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

    if len(monthly) > 0:
        peak_idx = monthly['total_orders'].idxmax()
        bars[peak_idx].set_color('#FFD43B')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc='upper left', facecolor='#252840', labelcolor='white', fontsize=9)

    plt.title('Tren Jumlah Order & Revenue Bulanan', color='#e0e6f0', fontsize=14, fontweight='bold', pad=12)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Insight box
    if len(monthly) > 0:
        peak_month = monthly.loc[monthly['total_orders'].idxmax(), 'order_month_str']
        peak_rev_month = monthly.loc[monthly['total_revenue'].idxmax(), 'order_month_str']
        st.info(f"📌 **Insight:** Puncak order terjadi pada **{peak_month}** dan puncak revenue pada **{peak_rev_month}**. "
                f"Tren menunjukkan pertumbuhan yang konsisten sepanjang periode analisis.")

# ════════════ TAB 2: KATEGORI PRODUK ════════════
with tab2:
    st.markdown('<div class="section-header">Kategori Produk Terlaris</div>', unsafe_allow_html=True)

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
    bars = ax.barh(top_cats['product_category_name_english'][::-1], x_vals[::-1], color=palette, edgecolor='none')
    ax.set_xlabel(x_axis_label, color='#aab4c8', fontsize=11)
    ax.tick_params(colors='#aab4c8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2d3250')
    ax.set_title(f'Top {top_n} Kategori Produk – {x_label}', color='#e0e6f0', fontsize=13, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

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
    st.markdown('<div class="section-header">Analisis Performa Pengiriman</div>', unsafe_allow_html=True)

    delivery_df = filtered_df.dropna(subset=['order_delivered_customer_date', 'review_score', 'is_late'])

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
        ax.set_title('Proporsi Keterlambatan', color='#e0e6f0', fontsize=12, fontweight='bold')
        st.pyplot(fig)
        plt.close()

    with colB:
        review_data = delivery_df.groupby('is_late')['review_score'].mean().reset_index()
        review_data['label'] = review_data['is_late'].map({0: 'Tepat Waktu', 1: 'Terlambat'})
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1e2130')
        ax.set_facecolor('#1e2130')
        colors_bar = ['#51CF66', '#FF6B6B']
        bars = ax.bar(review_data['label'], review_data['review_score'], color=colors_bar, width=0.4, edgecolor='none')
        ax.set_ylim(0, 5.5)
        ax.set_ylabel('Avg Review Score', color='#aab4c8', fontsize=11)
        ax.tick_params(colors='#aab4c8')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2d3250')
        ax.axhline(y=4, color='white', linestyle='--', alpha=0.3, linewidth=1)
        for bar, val in zip(bars, review_data['review_score']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
                    f'{val:.2f} ⭐', ha='center', fontsize=12, fontweight='bold', color='white')
        ax.set_title('Dampak Terhadap Review Score', color='#e0e6f0', fontsize=12, fontweight='bold')
        st.pyplot(fig)
        plt.close()

    # Waktu pengiriman
    delivery_df2 = filtered_df.dropna(subset=['order_delivered_customer_date', 'order_purchase_timestamp'])
    delivery_df2 = delivery_df2.copy()
    delivery_df2['delivery_days'] = (
        delivery_df2['order_delivered_customer_date'] - delivery_df2['order_purchase_timestamp']
    ).dt.days

    st.markdown('<div class="section-header">Distribusi Waktu Pengiriman (Hari)</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 4), facecolor='#1e2130')
    ax.set_facecolor('#1e2130')
    delivery_df2['delivery_days'].clip(0, 60).hist(bins=40, ax=ax, color='#4C6EF5', edgecolor='none', alpha=0.85)
    ax.axvline(delivery_df2['delivery_days'].median(), color='#FFD43B', linestyle='--', linewidth=2,
               label=f"Median: {delivery_df2['delivery_days'].median():.0f} hari")
    ax.set_xlabel('Hari Pengiriman', color='#aab4c8', fontsize=11)
    ax.set_ylabel('Frekuensi', color='#aab4c8', fontsize=11)
    ax.tick_params(colors='#aab4c8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2d3250')
    ax.legend(facecolor='#252840', labelcolor='white')
    ax.set_title('Distribusi Waktu Pengiriman', color='#e0e6f0', fontsize=12, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ════════════ TAB 4: RFM ════════════
with tab4:
    st.markdown('<div class="section-header">RFM Analysis – Segmentasi Pelanggan</div>', unsafe_allow_html=True)
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
                    pct = count / len(rfm_df) * 100
                else:
                    count, pct = 0, 0
                color = seg_colors.get(seg, '#888')
                with cols_rfm[i]:
                    st.markdown(f"""
                    <div class="kpi-card" style="border-color:{color}40;">
                        <div style="color:{color}; font-size:1.5rem; font-weight:700;">{count:,}</div>
                        <div style="color:{color}; font-size:0.75rem; font-weight:600;">{seg}</div>
                        <div class="kpi-label">{pct:.1f}% pelanggan</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            colR1, colR2 = st.columns(2)

            with colR1:
                fig, ax = plt.subplots(figsize=(7, 5), facecolor='#1e2130')
                ax.set_facecolor('#1e2130')
                seg_plot = seg_summary.set_index('segment').reindex(seg_order).reset_index().dropna()
                bar_colors = [seg_colors.get(s, '#888') for s in seg_plot['segment']]
                bars = ax.bar(seg_plot['segment'], seg_plot['jumlah'], color=bar_colors, edgecolor='none')
                ax.set_ylabel('Jumlah Pelanggan', color='#aab4c8', fontsize=10)
                ax.tick_params(colors='#aab4c8', axis='x', rotation=25)
                ax.tick_params(colors='#aab4c8', axis='y')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#2d3250')
                for bar, val in zip(bars, seg_plot['jumlah']):
                    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                            f'{int(val):,}', ha='center', fontsize=9, color='white', fontweight='bold')
                ax.set_title('Distribusi Segmen Pelanggan', color='#e0e6f0', fontsize=12, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

            with colR2:
                fig, ax = plt.subplots(figsize=(7, 5), facecolor='#1e2130')
                ax.set_facecolor('#1e2130')
                for seg, color in seg_colors.items():
                    mask = rfm_df['segment'] == seg
                    ax.scatter(rfm_df[mask]['recency'], rfm_df[mask]['monetary'],
                               c=color, label=seg, alpha=0.4, s=8)
                ax.set_xlabel('Recency (hari)', color='#aab4c8', fontsize=10)
                ax.set_ylabel('Monetary (R$)', color='#aab4c8', fontsize=10)
                ax.tick_params(colors='#aab4c8')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#2d3250')
                ax.legend(fontsize=8, facecolor='#252840', labelcolor='white')
                ax.set_yscale('log')
                ax.set_title('Recency vs Monetary per Segmen', color='#e0e6f0', fontsize=12, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

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
    st.markdown('<div class="section-header">Geospatial Analysis – Distribusi Pelanggan di Brazil</div>', unsafe_allow_html=True)

    @st.cache_data
    def load_geo():
        geo = pd.read_csv('data/geolocation_dataset.csv')
        cust = pd.read_csv('data/customers_dataset.csv')
        geo_uniq = geo.drop_duplicates('geolocation_zip_code_prefix')
        merged = cust.merge(
            geo_uniq[['geolocation_zip_code_prefix','geolocation_lat','geolocation_lng']],
            left_on='customer_zip_code_prefix',
            right_on='geolocation_zip_code_prefix',
            how='inner'
        )
        return merged

    try:
        customers_geo = load_geo()
        if selected_states and len(selected_states) < len(all_states):
            customers_geo = customers_geo[customers_geo['customer_state'].isin(selected_states)]

        col_geo1, col_geo2 = st.columns([2, 1])

        with col_geo1:
            st.markdown("##### 🗺️ Heatmap Distribusi Pelanggan")
            sample = customers_geo.sample(min(3000, len(customers_geo)), random_state=42)
            m = folium.Map(location=[-14.235, -51.925], zoom_start=4, tiles='CartoDB dark_matter')
            heat_data = sample[['geolocation_lat','geolocation_lng']].dropna().values.tolist()
            HeatMap(heat_data, radius=12, blur=18, max_zoom=13,
                    gradient={0.2:'blue', 0.4:'cyan', 0.6:'lime', 0.8:'orange', 1.0:'red'}).add_to(m)
            st_folium(m, width=700, height=450)

        with col_geo2:
            st.markdown("##### 📊 Revenue per State")
            state_rev = filtered_df.groupby('customer_state')['payment_value'].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(5, 6), facecolor='#1e2130')
            ax.set_facecolor('#1e2130')
            colors = sns.color_palette('viridis', len(state_rev))
            ax.barh(state_rev.index[::-1], state_rev.values[::-1]/1e6, color=colors[::-1], edgecolor='none')
            ax.set_xlabel('Revenue (Juta R$)', color='#aab4c8', fontsize=9)
            ax.tick_params(colors='#aab4c8', labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor('#2d3250')
            ax.set_title('Top 10 State – Revenue', color='#e0e6f0', fontsize=11, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

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
