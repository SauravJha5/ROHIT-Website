import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import load_dataset
from src.data_cleaning import clean_dataset
from src.feature_engineering import engineer_features, apply_delay_flag, FACTORY_COORDINATES, PRODUCT_FACTORY_MAP
from src.route_analysis import (compute_route_metrics, get_top_bottom_routes, identify_bottlenecks,
                                compute_ship_mode_analysis, compute_time_series)
from src.metrics import compute_kpis, generate_key_findings, compute_state_metrics
from src import visualizations as viz

st.set_page_config(page_title="Nassau Candy — Route Efficiency", page_icon="🍬",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0A0A0F;
    --card: #13131A;
    --card-hover: #1A1A25;
    --border: rgba(0,212,170,0.12);
    --border-hover: rgba(0,212,170,0.35);
    --primary: #00D4AA;
    --secondary: #0EA5E9;
    --accent: #F472B6;
    --text: #E8E8ED;
    --muted: #6B7280;
    --glass: rgba(19,19,26,0.75);
}

*, *::before, *::after { font-family: 'DM Sans', sans-serif !important; }

@keyframes heroGlow {
    0%, 100% { opacity: 0.6; filter: blur(60px); }
    50% { opacity: 1; filter: blur(80px); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes breathe {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,212,170,0); }
    50% { box-shadow: 0 0 30px -5px rgba(0,212,170,0.15); }
}
@keyframes numberPop {
    0% { transform: scale(0.8); opacity: 0; }
    60% { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
}
@keyframes dotPulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

.stApp { background: var(--bg) !important; }

.hero-container { position: relative; padding: 20px 0 10px 0; margin-bottom: 10px; }
.hero-glow {
    position: absolute; top: -40px; left: 50%; transform: translateX(-50%);
    width: 500px; height: 120px;
    background: radial-gradient(ellipse, rgba(0,212,170,0.15), rgba(14,165,233,0.08), transparent);
    animation: heroGlow 4s ease-in-out infinite; pointer-events: none; z-index: 0;
}
.hero-title {
    position: relative; z-index: 1; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #00D4AA, #0EA5E9, #F472B6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin: 0; line-height: 1.2;
}
.hero-subtitle { position: relative; z-index: 1; color: var(--muted); font-size: 0.95rem; font-weight: 400; margin: 4px 0 0 0; }
.hero-badge {
    display: inline-block; background: rgba(0,212,170,0.1); border: 1px solid rgba(0,212,170,0.2);
    color: var(--primary); font-size: 0.7rem; font-weight: 600; padding: 3px 10px;
    border-radius: 20px; margin-top: 8px; letter-spacing: 0.05em; text-transform: uppercase;
}

div[data-testid="metric-container"] {
    background: var(--glass) !important; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border) !important; border-radius: 16px !important; padding: 20px 24px !important;
    animation: slideUp 0.7s ease-out both, breathe 4s ease-in-out infinite;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); position: relative; overflow: hidden;
}
div[data-testid="metric-container"]::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
    opacity: 0; transition: opacity 0.4s;
}
div[data-testid="metric-container"]:hover {
    background: var(--card-hover) !important; border-color: var(--border-hover) !important;
    transform: translateY(-6px); box-shadow: 0 20px 60px -15px rgba(0,212,170,0.2) !important;
}
div[data-testid="metric-container"]:hover::after { opacity: 1; }
div[data-testid="metric-container"] label {
    color: var(--muted) !important; font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text) !important; font-weight: 800 !important; font-size: 1.8rem !important;
    font-family: 'JetBrains Mono', monospace !important; animation: numberPop 0.8s ease-out both;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08080D 0%, #0F0F18 40%, #08080D 100%) !important;
    border-right: 1px solid rgba(0,212,170,0.08);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {
    color: #9CA3AF !important; font-weight: 600 !important; text-transform: uppercase !important;
    font-size: 0.65rem !important; letter-spacing: 0.1em !important;
}

.sidebar-brand { text-align: center; padding: 16px 0; margin-bottom: 8px; }
.sidebar-brand-icon { font-size: 2.4rem; }
.sidebar-brand-text { font-size: 1.1rem; font-weight: 700; color: var(--text); margin: 4px 0 0; }
.sidebar-brand-sub { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.15em; font-weight: 500; }
.sidebar-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(0,212,170,0.2), transparent); margin: 16px 0; }

.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: rgba(19,19,26,0.5); border-radius: 12px; padding: 4px;
    border: 1px solid rgba(0,212,170,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 10px 18px; font-weight: 600; font-size: 0.85rem;
    color: var(--muted) !important; transition: all 0.3s ease; border: none !important;
}
.stTabs [data-baseweb="tab"]:hover { background: rgba(0,212,170,0.06) !important; color: var(--text) !important; }
.stTabs [aria-selected="true"] {
    background: rgba(0,212,170,0.12) !important; color: var(--primary) !important;
    border-bottom: none !important; box-shadow: 0 0 20px rgba(0,212,170,0.08);
}

.section-header { font-size: 1.3rem; font-weight: 700; color: var(--text); margin: 24px 0 16px; display: flex; align-items: center; gap: 10px; }
.section-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); animation: dotPulse 2s ease-in-out infinite; }
.glass-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,212,170,0.15), rgba(14,165,233,0.1), transparent); margin: 28px 0; }

div[data-testid="stPlotlyChart"] {
    animation: slideUp 0.6s ease-out both; background: rgba(19,19,26,0.3);
    border: 1px solid rgba(255,255,255,0.03); border-radius: 16px; padding: 8px; transition: all 0.3s ease;
}
div[data-testid="stPlotlyChart"]:hover { border-color: rgba(0,212,170,0.12); background: rgba(19,19,26,0.5); }

.stDataFrame { border-radius: 12px !important; overflow: hidden; animation: slideUp 0.5s ease-out both; border: 1px solid rgba(0,212,170,0.08) !important; }
.streamlit-expanderHeader { font-weight: 600 !important; color: var(--primary) !important; font-size: 0.9rem; }
details { border: 1px solid rgba(0,212,170,0.1) !important; border-radius: 12px !important; background: rgba(19,19,26,0.4) !important; }
.stAlert { border-radius: 12px !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #2A2A35; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

#MainMenu {visibility: hidden;} header {visibility: hidden;} .stDeployButton {display: none;}

.status-live { display: inline-flex; align-items: center; gap: 6px; font-size: 0.7rem; color: var(--primary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--primary); animation: dotPulse 1.5s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def run_pipeline():
    df_raw = load_dataset()
    df_clean, clean_report = clean_dataset(df_raw)
    df_features, feat_report = engineer_features(df_clean)
    return df_features, clean_report, feat_report

try:
    df_full, clean_report, feat_report = run_pipeline()
except (FileNotFoundError, ValueError) as e:
    st.error(f"Data loading error: {e}")
    st.stop()

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🍬</div>
        <div class="sidebar-brand-text">Nassau Candy</div>
        <div class="sidebar-brand-sub">Route Analytics</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    delay_threshold = st.slider("DELAY THRESHOLD", 1, 12, 5, help="Shipments exceeding this are flagged delayed.")
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    min_date = df_full["Order Date"].min().date()
    max_date = df_full["Order Date"].max().date()
    date_range = st.date_input("DATE RANGE", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    selected_regions = st.multiselect("REGION", sorted(df_full["Region"].unique()), default=sorted(df_full["Region"].unique()))
    selected_factories = st.multiselect("FACTORY", sorted(df_full["Factory"].unique()), default=sorted(df_full["Factory"].unique()))
    selected_states = st.multiselect("STATE", sorted(df_full["State/Province"].unique()), default=sorted(df_full["State/Province"].unique()))
    selected_modes = st.multiselect("SHIP MODE", sorted(df_full["Ship Mode"].unique()), default=sorted(df_full["Ship Mode"].unique()))

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-live"><span class="status-dot"></span> LIVE DATA</div><br><span style="color:#4B5563;font-size:0.72rem;">{min_date.strftime("%b %Y")} - {max_date.strftime("%b %Y")}<br>{len(df_full):,} records</span>', unsafe_allow_html=True)

def apply_filters(df):
    mask = pd.Series(True, index=df.index)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        mask &= df["Order Date"].dt.date >= date_range[0]
        mask &= df["Order Date"].dt.date <= date_range[1]
    if selected_regions: mask &= df["Region"].isin(selected_regions)
    if selected_factories: mask &= df["Factory"].isin(selected_factories)
    if selected_states: mask &= df["State/Province"].isin(selected_states)
    if selected_modes: mask &= df["Ship Mode"].isin(selected_modes)
    return df[mask].copy()

df = apply_delay_flag(apply_filters(df_full), threshold=delay_threshold)
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

kpis = compute_kpis(df)
route_metrics = compute_route_metrics(df, "Route", delay_threshold)
mode_metrics = compute_ship_mode_analysis(df)
monthly = compute_time_series(df)
state_metrics = compute_state_metrics(df)
top_routes, bottom_routes, excluded_count = get_top_bottom_routes(route_metrics, 10, 5)
bottlenecks = identify_bottlenecks(route_metrics)
findings = generate_key_findings(df, route_metrics, kpis, delay_threshold)

st.markdown("""
<div class="hero-container">
    <div class="hero-glow"></div>
    <div class="hero-title">Nassau Candy Distributor</div>
    <div class="hero-subtitle">Factory-to-Customer Shipping Route Efficiency Analysis</div>
    <div class="hero-badge">● Live Dashboard</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🛣️ Routes", "🗺️ Geography", "📦 Ship Modes", "🔎 Drill-Down"])

with tab1:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Shipments", f"{kpis['total_shipments']:,}")
    c2.metric("Avg Lead Time", f"{kpis['avg_lead_time']}d")
    c3.metric("Delay Rate", f"{kpis['delay_rate']}%")
    c4.metric("Active Routes", f"{kpis['total_routes']}")
    c5.metric("Revenue", f"${kpis['total_sales']:,.0f}")
    c6.metric("Gross Profit", f"${kpis['total_gross_profit']:,.0f}")

    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(viz.chart_monthly_shipments(monthly), use_container_width=True)
    col2.plotly_chart(viz.chart_lead_time_by_factory(df), use_container_width=True)
    col3, col4 = st.columns(2)
    col3.plotly_chart(viz.chart_delay_rate_by_region(df), use_container_width=True)
    col4.plotly_chart(viz.chart_shipments_by_region(df), use_container_width=True)

    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-dot"></span> Key Findings</div>', unsafe_allow_html=True)
    st.caption(f"From {kpis['total_shipments']:,} shipments · delay threshold >{delay_threshold} days")
    for f in findings:
        st.markdown(f"- {f}")

    with st.expander("Data Cleaning & Methodology"):
        for d in clean_report.get("decisions", []):
            st.markdown(f"- {d}")
        issues = clean_report.get("issues", [])
        for iss in issues:
            st.markdown(f"- {iss}")
        if not issues:
            st.markdown("- No data quality issues detected.")
        st.markdown(f"**Records:** {clean_report['original_rows']:,} loaded, {clean_report['final_rows']:,} retained")

with tab2:
    st.markdown('<div class="section-header"><span class="section-dot"></span> Route Efficiency</div>', unsafe_allow_html=True)
    col_a, _ = st.columns([1, 3])
    with col_a:
        min_ship = st.number_input("Min. Shipments", 1, 100, 5, help="Exclude low-volume routes")
    top_r, bot_r, exc = get_top_bottom_routes(route_metrics, 10, min_ship)
    if exc > 0:
        st.info(f"{exc} routes with <{min_ship} shipments excluded.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Top 10 Efficient Routes")
        if not top_r.empty:
            dcols = [c for c in [top_r.columns[0], "Total_Shipments", "Avg_Lead_Time", "Delay_Rate", "Efficiency_Score"] if c in top_r.columns]
            st.dataframe(top_r[dcols].style.format({"Avg_Lead_Time": "{:.2f}", "Delay_Rate": "{:.1f}%", "Efficiency_Score": "{:.1f}"}), use_container_width=True, height=400)
        else:
            st.info("No routes meet threshold.")
    with col2:
        st.markdown("##### Bottom 10 Routes")
        if not bot_r.empty:
            dcols = [c for c in [bot_r.columns[0], "Total_Shipments", "Avg_Lead_Time", "Delay_Rate", "Efficiency_Score"] if c in bot_r.columns]
            st.dataframe(bot_r[dcols].style.format({"Avg_Lead_Time": "{:.2f}", "Delay_Rate": "{:.1f}%", "Efficiency_Score": "{:.1f}"}), use_container_width=True, height=400)
        else:
            st.info("No routes meet threshold.")

    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    col3.plotly_chart(viz.chart_route_scatter(route_metrics), use_container_width=True)
    col4.plotly_chart(viz.chart_efficiency_distribution(route_metrics), use_container_width=True)

    with st.expander("Full Route Leaderboard"):
        st.plotly_chart(viz.chart_route_leaderboard(route_metrics, 20), use_container_width=True)
    with st.expander("Scoring Methodology"):
        st.markdown("- **Lead Time Score (70%):** `100 * (Max - Route) / (Max - Min)`\n- **Delay Score (30%):** `100 - Delay_Rate`\n- **Final:** `0.7 * LT + 0.3 * Delay`")

    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-dot"></span> Bottleneck Analysis</div>', unsafe_allow_html=True)
    bn1, bn2 = st.columns(2)
    with bn1:
        st.markdown("##### High-Volume & Poor-Performance")
        hvpp = bottlenecks.get("high_volume_poor_perf", pd.DataFrame())
        if not hvpp.empty:
            hcols = [c for c in [hvpp.columns[0], "Total_Shipments", "Avg_Lead_Time", "Delay_Rate", "Efficiency_Score"] if c in hvpp.columns]
            st.dataframe(hvpp[hcols], use_container_width=True)
        else:
            st.success("No bottlenecks detected.")
    with bn2:
        st.markdown("##### Factory Performance")
        fp = bottlenecks.get("factory_performance", pd.DataFrame())
        if not fp.empty:
            st.dataframe(fp.style.format({"Avg_Lead_Time": "{:.2f}", "Avg_Delay_Rate": "{:.1f}%", "Avg_Efficiency": "{:.1f}"}), use_container_width=True)

with tab3:
    st.markdown('<div class="section-header"><span class="section-dot"></span> Geographic Analysis</div>', unsafe_allow_html=True)
    gc1, _ = st.columns([1, 3])
    with gc1:
        metric_opt = st.selectbox("Map Metric", ["Avg_Lead_Time", "Delay_Rate", "Shipments", "Efficiency_Score"],
            format_func=lambda x: {"Avg_Lead_Time": "Avg Lead Time", "Delay_Rate": "Delay Rate", "Shipments": "Volume", "Efficiency_Score": "Efficiency"}.get(x, x))
    titles = {"Avg_Lead_Time": "Average Lead Time by State", "Delay_Rate": "Delay Rate by State", "Shipments": "Shipment Volume by State", "Efficiency_Score": "Efficiency Score by State"}
    st.plotly_chart(viz.chart_us_choropleth(state_metrics, metric_opt, titles.get(metric_opt, "")), use_container_width=True)
    st.plotly_chart(viz.chart_factory_map(df), use_container_width=True)

    with st.expander("State Metrics Table"):
        if not state_metrics.empty:
            st.dataframe(state_metrics.sort_values("Avg_Lead_Time", ascending=False).reset_index(drop=True)[
                ["State/Province", "Region", "Country", "Shipments", "Avg_Lead_Time", "Delay_Rate", "Efficiency_Score", "Total_Sales"]
            ].style.format({"Avg_Lead_Time": "{:.2f}", "Delay_Rate": "{:.1f}%", "Efficiency_Score": "{:.1f}", "Total_Sales": "${:,.0f}"}), use_container_width=True, height=500)

    st.markdown("##### Regional Comparison")
    ragg = df.groupby("Region").agg(Shipments=("Row ID", "count"), Avg_LT=("Shipping Lead Time", "mean"), DR=("Delay Flag", "mean")).reset_index()
    ragg["DR"] = (ragg["DR"] * 100).round(1)
    rcols = st.columns(4)
    for i, (_, r) in enumerate(ragg.sort_values("Shipments", ascending=False).iterrows()):
        rcols[i % 4].metric(r["Region"], f"{r['Shipments']:,}", f"LT: {r['Avg_LT']:.1f}d · Delay: {r['DR']:.1f}%")

with tab4:
    st.markdown('<div class="section-header"><span class="section-dot"></span> Ship Mode Analysis</div>', unsafe_allow_html=True)
    sm_cols = st.columns(len(mode_metrics))
    for i, (_, r) in enumerate(mode_metrics.iterrows()):
        sm_cols[i].metric(r["Ship Mode"], f"{int(r['Shipments']):,}", f"LT: {r['Avg_Lead_Time']:.1f}d")

    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.chart_ship_mode_volume(mode_metrics), use_container_width=True)
    c2.plotly_chart(viz.chart_ship_mode_lead_time(mode_metrics), use_container_width=True)
    c3, c4 = st.columns(2)
    c3.plotly_chart(viz.chart_ship_mode_delay(mode_metrics), use_container_width=True)
    c4.plotly_chart(viz.chart_lead_time_distribution(df, by_mode=True), use_container_width=True)
    st.plotly_chart(viz.chart_monthly_ship_mode(df), use_container_width=True)

    with st.expander("Detailed Metrics"):
        st.dataframe(mode_metrics.style.format({"Avg_Lead_Time": "{:.2f}", "Median_Lead_Time": "{:.0f}", "Std_Lead_Time": "{:.2f}",
            "Delay_Rate": "{:.1f}%", "Total_Sales": "${:,.0f}", "Avg_Sales": "${:.2f}", "Total_Gross_Profit": "${:,.0f}"}), use_container_width=True)

with tab5:
    st.markdown('<div class="section-header"><span class="section-dot"></span> Route Drill-Down</div>', unsafe_allow_html=True)
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        dd_factory = st.selectbox("Factory", ["All"] + sorted(df["Factory"].unique()), key="dd_f")
    with dc2:
        opts = sorted(df[df["Factory"] == dd_factory]["State/Province"].unique()) if dd_factory != "All" else sorted(df["State/Province"].unique())
        dd_state = st.selectbox("State", ["All"] + opts, key="dd_s")
    with dc3:
        dd_mode = st.selectbox("Ship Mode", ["All"] + sorted(df["Ship Mode"].unique()), key="dd_m")

    dd = df.copy()
    if dd_factory != "All": dd = dd[dd["Factory"] == dd_factory]
    if dd_state != "All": dd = dd[dd["State/Province"] == dd_state]
    if dd_mode != "All": dd = dd[dd["Ship Mode"] == dd_mode]

    if dd.empty:
        st.warning("No shipments match drill-down filters.")
    else:
        dk = compute_kpis(dd)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Shipments", f"{dk['total_shipments']:,}")
        k2.metric("Avg Lead Time", f"{dk['avg_lead_time']}d")
        k3.metric("Delay Rate", f"{dk['delay_rate']}%")
        k4.metric("Revenue", f"${dk['total_sales']:,.0f}")

        st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)
        dc1, dc2 = st.columns(2)
        dc1.plotly_chart(viz.chart_lead_time_distribution(dd, by_mode=False), use_container_width=True)
        dc2.plotly_chart(viz.chart_product_mix(dd), use_container_width=True)
        st.plotly_chart(viz.chart_route_monthly_trend(dd), use_container_width=True)

        with st.expander("Order-Level Details"):
            disp = dd[["Order ID", "Order Date", "Decoded Ship Date", "Ship Mode", "Customer ID",
                        "State/Province", "Product Name", "Factory", "Sales", "Units",
                        "Shipping Lead Time", "Delay Flag"]].copy()
            disp.columns = ["Order ID", "Order Date", "Ship Date", "Mode", "Customer", "State",
                            "Product", "Factory", "Sales", "Units", "Lead Time", "Delayed"]
            disp["Order Date"] = disp["Order Date"].dt.strftime("%Y-%m-%d")
            disp["Ship Date"] = disp["Ship Date"].dt.strftime("%Y-%m-%d")
            disp["Delayed"] = disp["Delayed"].map({1: "Yes", 0: "No"})
            st.dataframe(disp.sort_values("Order Date", ascending=False), use_container_width=True, height=500)
