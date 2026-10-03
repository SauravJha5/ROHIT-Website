"""
Visualizations Module
=====================
Creates all Plotly charts for the Streamlit dashboard.
All charts use a consistent dark professional theme.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from src.metrics import US_STATE_ABBREV, CA_PROVINCE_ABBREV

# ──────────────────────────────────────────────────────────
# Theme Constants
# ──────────────────────────────────────────────────────────
COLORS = {
    "primary": "#6366F1",       # Indigo
    "secondary": "#8B5CF6",     # Violet
    "accent": "#EC4899",        # Pink
    "success": "#10B981",       # Emerald
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "info": "#3B82F6",          # Blue
    "bg": "#0F172A",            # Slate-900
    "card": "#1E293B",          # Slate-800
    "text": "#F1F5F9",          # Slate-100
    "muted": "#94A3B8",         # Slate-400
}

PALETTE = [
    "#6366F1", "#8B5CF6", "#EC4899", "#10B981", "#F59E0B",
    "#3B82F6", "#EF4444", "#14B8A6", "#F97316", "#A855F7",
]

FACTORY_COLORS = {
    "Lot's O' Nuts": "#6366F1",
    "Wicked Choccy's": "#EC4899",
    "Sugar Shack": "#10B981",
    "Secret Factory": "#F59E0B",
    "The Other Factory": "#3B82F6",
}

SHIP_MODE_COLORS = {
    "Same Day": "#10B981",
    "First Class": "#6366F1",
    "Second Class": "#F59E0B",
    "Standard Class": "#EF4444",
}

REGION_COLORS = {
    "Atlantic": "#6366F1",
    "Gulf": "#EC4899",
    "Interior": "#F59E0B",
    "Pacific": "#10B981",
}

_LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"]),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor=COLORS["card"],
        font_size=13,
        font_family="Inter, sans-serif",
    ),
)


def _apply_layout(fig, title: str = "", height: int = 400, **kwargs):
    """Apply consistent layout to a figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=COLORS["text"])),
        height=height,
        **_LAYOUT_DEFAULTS,
        **kwargs,
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.1)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.1)", zeroline=False)
    return fig


# ──────────────────────────────────────────────────────────
# Executive Overview Charts
# ──────────────────────────────────────────────────────────

def chart_monthly_shipments(monthly: pd.DataFrame) -> go.Figure:
    """Monthly shipment volume trend."""
    if monthly.empty:
        return _empty_figure("No data available")
    fig = px.area(
        monthly, x="Year-Month", y="Shipments",
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_traces(
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.15)",
        line=dict(width=2.5),
    )
    return _apply_layout(fig, "Monthly Shipment Volume", height=350)


def chart_lead_time_by_factory(df: pd.DataFrame) -> go.Figure:
    """Average lead time by factory (horizontal bar)."""
    if df.empty:
        return _empty_figure("No data available")
    factory_lt = (
        df.groupby("Factory")["Shipping Lead Time"]
        .mean()
        .sort_values()
        .reset_index()
    )
    fig = px.bar(
        factory_lt, x="Shipping Lead Time", y="Factory",
        orientation="h",
        color="Factory",
        color_discrete_map=FACTORY_COLORS,
        text=factory_lt["Shipping Lead Time"].round(1),
    )
    fig.update_traces(textposition="outside", textfont_size=12)
    return _apply_layout(
        fig, "Average Order-to-Ship Lead Time by Factory",
        height=350, showlegend=False,
        xaxis_title="Average Lead Time (days)",
        yaxis_title="",
    )


def chart_delay_rate_by_region(df: pd.DataFrame) -> go.Figure:
    """Delay rate by region (donut chart)."""
    if df.empty:
        return _empty_figure("No data available")
    region_stats = df.groupby("Region").agg(
        Total=("Row ID", "count"),
        Delayed=("Delay Flag", "sum"),
    ).reset_index()
    region_stats["Delay_Rate"] = (
        region_stats["Delayed"] / region_stats["Total"] * 100
    ).round(1)

    fig = px.bar(
        region_stats.sort_values("Delay_Rate", ascending=True),
        x="Delay_Rate", y="Region", orientation="h",
        color="Region", color_discrete_map=REGION_COLORS,
        text="Delay_Rate",
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%", textposition="outside",
        textfont_size=12,
    )
    return _apply_layout(
        fig, "Delay Rate by Region", height=300,
        showlegend=False,
        xaxis_title="Delay Rate (%)", yaxis_title="",
    )


def chart_shipments_by_region(df: pd.DataFrame) -> go.Figure:
    """Shipment volume by region (bar)."""
    if df.empty:
        return _empty_figure("No data available")
    region_vol = df["Region"].value_counts().reset_index()
    region_vol.columns = ["Region", "Shipments"]
    fig = px.bar(
        region_vol.sort_values("Shipments"),
        x="Shipments", y="Region", orientation="h",
        color="Region", color_discrete_map=REGION_COLORS,
        text="Shipments",
    )
    fig.update_traces(textposition="outside", textfont_size=12)
    return _apply_layout(
        fig, "Shipment Volume by Region", height=300,
        showlegend=False,
        xaxis_title="Shipments", yaxis_title="",
    )


# ──────────────────────────────────────────────────────────
# Route Efficiency Charts
# ──────────────────────────────────────────────────────────

def chart_route_leaderboard(
    route_metrics: pd.DataFrame, top_n: int = 15
) -> go.Figure:
    """Route efficiency leaderboard (horizontal bar)."""
    if route_metrics.empty:
        return _empty_figure("No data available")
    display = route_metrics.head(top_n).copy()
    route_col = display.columns[0]
    fig = px.bar(
        display.sort_values("Efficiency_Score"),
        x="Efficiency_Score", y=route_col, orientation="h",
        color="Efficiency_Score",
        color_continuous_scale="Viridis",
        hover_data=["Total_Shipments", "Avg_Lead_Time", "Delay_Rate"],
    )
    return _apply_layout(
        fig, f"Top {top_n} Routes by Efficiency Score",
        height=max(350, top_n * 28),
        xaxis_title="Efficiency Score", yaxis_title="",
        coloraxis_colorbar_title="Score",
    )


def chart_route_scatter(route_metrics: pd.DataFrame) -> go.Figure:
    """Scatter: Lead Time vs Delay Rate, sized by volume."""
    if route_metrics.empty:
        return _empty_figure("No data available")
    route_col = route_metrics.columns[0]
    fig = px.scatter(
        route_metrics,
        x="Avg_Lead_Time", y="Delay_Rate",
        size="Total_Shipments",
        color="Efficiency_Score",
        color_continuous_scale="RdYlGn",
        hover_name=route_col,
        hover_data=["Total_Shipments", "Avg_Lead_Time", "Delay_Rate"],
        size_max=40,
    )
    return _apply_layout(
        fig, "Route Performance: Lead Time vs Delay Rate",
        height=450,
        xaxis_title="Average Lead Time (days)",
        yaxis_title="Delay Rate (%)",
        coloraxis_colorbar_title="Efficiency",
    )


def chart_efficiency_distribution(route_metrics: pd.DataFrame) -> go.Figure:
    """Histogram of route efficiency scores."""
    if route_metrics.empty:
        return _empty_figure("No data available")
    fig = px.histogram(
        route_metrics, x="Efficiency_Score", nbins=25,
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_traces(
        marker_line_color=COLORS["text"],
        marker_line_width=0.5,
    )
    return _apply_layout(
        fig, "Distribution of Route Efficiency Scores", height=350,
        xaxis_title="Efficiency Score", yaxis_title="Number of Routes",
    )


# ──────────────────────────────────────────────────────────
# Geographic Charts
# ──────────────────────────────────────────────────────────

def chart_us_choropleth(
    state_metrics: pd.DataFrame,
    metric: str = "Avg_Lead_Time",
    title: str = "Average Lead Time by State",
) -> go.Figure:
    """US state-level choropleth map."""
    if state_metrics.empty:
        return _empty_figure("No data available")

    # Filter to US states only and add abbreviation
    us_states = state_metrics[
        state_metrics["Country"] == "United States"
    ].copy()
    us_states["State_Abbrev"] = us_states["State/Province"].map(US_STATE_ABBREV)
    us_states = us_states.dropna(subset=["State_Abbrev"])

    # Color scale based on metric
    if metric in ["Avg_Lead_Time", "Delay_Rate"]:
        color_scale = "YlOrRd"  # Higher = worse
    elif metric == "Efficiency_Score":
        color_scale = "RdYlGn"  # Higher = better
    else:
        color_scale = "Blues"  # Neutral

    fig = go.Figure(
        go.Choropleth(
            locations=us_states["State_Abbrev"],
            z=us_states[metric].round(2),
            locationmode="USA-states",
            colorscale=color_scale,
            colorbar_title=metric.replace("_", " "),
            text=us_states["State/Province"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                + metric.replace("_", " ")
                + ": %{z:.2f}<br>"
                + "Shipments: %{customdata[0]:,}<br>"
                "<extra></extra>"
            ),
            customdata=us_states[["Shipments"]].values,
        )
    )
    fig.update_layout(
        geo=dict(
            scope="usa",
            bgcolor="rgba(0,0,0,0)",
            lakecolor="rgba(0,0,0,0)",
            landcolor=COLORS["card"],
            showlakes=True,
        ),
    )
    return _apply_layout(fig, title, height=500)


def chart_factory_map(df: pd.DataFrame) -> go.Figure:
    """Map showing factory locations."""
    if df.empty:
        return _empty_figure("No data available")

    from src.feature_engineering import FACTORY_COORDINATES
    factories = pd.DataFrame([
        {"Factory": name, "Latitude": coords["lat"], "Longitude": coords["lon"]}
        for name, coords in FACTORY_COORDINATES.items()
    ])

    # Add shipment counts
    factory_counts = df["Factory"].value_counts().reset_index()
    factory_counts.columns = ["Factory", "Shipments"]
    factories = factories.merge(factory_counts, on="Factory", how="left")
    factories["Shipments"] = factories["Shipments"].fillna(0).astype(int)

    fig = go.Figure()
    fig.add_trace(
        go.Scattergeo(
            lon=factories["Longitude"],
            lat=factories["Latitude"],
            text=factories.apply(
                lambda r: f"{r['Factory']}<br>Shipments: {r['Shipments']:,}",
                axis=1,
            ),
            marker=dict(
                size=factories["Shipments"] / factories["Shipments"].max() * 30 + 8,
                color=[FACTORY_COLORS.get(f, COLORS["primary"]) for f in factories["Factory"]],
                line=dict(width=1, color="white"),
            ),
            hoverinfo="text",
            name="Factories",
        )
    )
    fig.update_layout(
        geo=dict(
            scope="usa",
            bgcolor="rgba(0,0,0,0)",
            lakecolor="rgba(0,0,0,0)",
            landcolor=COLORS["card"],
            showlakes=True,
        ),
    )
    return _apply_layout(fig, "Factory Locations", height=400)


# ──────────────────────────────────────────────────────────
# Ship Mode Charts
# ──────────────────────────────────────────────────────────

def chart_ship_mode_volume(mode_metrics: pd.DataFrame) -> go.Figure:
    """Ship mode volume (pie chart)."""
    if mode_metrics.empty:
        return _empty_figure("No data available")
    fig = px.pie(
        mode_metrics, values="Shipments", names="Ship Mode",
        color="Ship Mode", color_discrete_map=SHIP_MODE_COLORS,
        hole=0.45,
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont_size=12,
    )
    return _apply_layout(fig, "Shipment Volume by Ship Mode", height=380)


def chart_ship_mode_lead_time(mode_metrics: pd.DataFrame) -> go.Figure:
    """Ship mode average lead time comparison."""
    if mode_metrics.empty:
        return _empty_figure("No data available")
    fig = px.bar(
        mode_metrics, x="Ship Mode", y="Avg_Lead_Time",
        color="Ship Mode", color_discrete_map=SHIP_MODE_COLORS,
        text=mode_metrics["Avg_Lead_Time"].round(2),
    )
    fig.update_traces(textposition="outside", textfont_size=13)
    return _apply_layout(
        fig, "Average Lead Time by Ship Mode", height=380,
        showlegend=False,
        xaxis_title="", yaxis_title="Average Lead Time (days)",
    )


def chart_ship_mode_delay(mode_metrics: pd.DataFrame) -> go.Figure:
    """Ship mode delay rate comparison."""
    if mode_metrics.empty:
        return _empty_figure("No data available")
    fig = px.bar(
        mode_metrics, x="Ship Mode", y="Delay_Rate",
        color="Ship Mode", color_discrete_map=SHIP_MODE_COLORS,
        text=mode_metrics["Delay_Rate"].round(1),
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%", textposition="outside",
        textfont_size=13,
    )
    return _apply_layout(
        fig, "Delay Rate by Ship Mode", height=380,
        showlegend=False,
        xaxis_title="", yaxis_title="Delay Rate (%)",
    )


def chart_lead_time_distribution(
    df: pd.DataFrame, by_mode: bool = True
) -> go.Figure:
    """Lead time distribution (histogram or box plot)."""
    if df.empty:
        return _empty_figure("No data available")
    if by_mode:
        fig = px.box(
            df, x="Ship Mode", y="Shipping Lead Time",
            color="Ship Mode", color_discrete_map=SHIP_MODE_COLORS,
            points="outliers",
        )
        return _apply_layout(
            fig, "Lead Time Distribution by Ship Mode", height=400,
            showlegend=False,
            xaxis_title="", yaxis_title="Lead Time (days)",
        )
    else:
        fig = px.histogram(
            df, x="Shipping Lead Time", nbins=15,
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig.update_traces(
            marker_line_color=COLORS["text"],
            marker_line_width=0.5,
        )
        return _apply_layout(
            fig, "Overall Lead Time Distribution", height=350,
            xaxis_title="Lead Time (days)",
            yaxis_title="Count",
        )


def chart_monthly_ship_mode(df: pd.DataFrame) -> go.Figure:
    """Monthly shipments by ship mode (stacked area)."""
    if df.empty:
        return _empty_figure("No data available")
    monthly = (
        df.groupby(["Year-Month", "Ship Mode"])
        .size()
        .reset_index(name="Shipments")
    )
    fig = px.area(
        monthly, x="Year-Month", y="Shipments",
        color="Ship Mode", color_discrete_map=SHIP_MODE_COLORS,
    )
    return _apply_layout(
        fig, "Monthly Shipments by Ship Mode", height=400,
        xaxis_title="", yaxis_title="Shipments",
    )


# ──────────────────────────────────────────────────────────
# Drill-Down Charts
# ──────────────────────────────────────────────────────────

def chart_route_monthly_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly trend for a specific route selection."""
    if df.empty:
        return _empty_figure("No data available")
    monthly = df.groupby("Year-Month").agg(
        Shipments=("Row ID", "count"),
        Avg_Lead_Time=("Shipping Lead Time", "mean"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["Year-Month"], y=monthly["Shipments"],
        name="Shipments",
        marker_color=COLORS["primary"],
        opacity=0.7,
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Year-Month"], y=monthly["Avg_Lead_Time"],
        name="Avg Lead Time",
        line=dict(color=COLORS["accent"], width=3),
        yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title="Shipments", side="left"),
        yaxis2=dict(title="Avg Lead Time (days)", side="right", overlaying="y"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return _apply_layout(
        fig, "Monthly Performance Trend", height=380,
        xaxis_title="",
    )


def chart_product_mix(df: pd.DataFrame) -> go.Figure:
    """Product mix for a filtered dataset (pie chart)."""
    if df.empty:
        return _empty_figure("No data available")
    product_counts = df["Product Name"].value_counts().reset_index()
    product_counts.columns = ["Product Name", "Count"]
    fig = px.pie(
        product_counts, values="Count", names="Product Name",
        color_discrete_sequence=PALETTE,
        hole=0.4,
    )
    fig.update_traces(textinfo="percent+label", textfont_size=11)
    return _apply_layout(fig, "Product Mix", height=380)


# ──────────────────────────────────────────────────────────
# Time Analysis Charts
# ──────────────────────────────────────────────────────────

def chart_monthly_lead_time(monthly: pd.DataFrame) -> go.Figure:
    """Monthly average lead time trend."""
    if monthly.empty:
        return _empty_figure("No data available")
    fig = px.line(
        monthly, x="Year-Month", y="Avg_Lead_Time",
        color_discrete_sequence=[COLORS["accent"]],
        markers=True,
    )
    fig.update_traces(line=dict(width=2.5))
    return _apply_layout(
        fig, "Monthly Average Order-to-Ship Lead Time", height=350,
        xaxis_title="", yaxis_title="Average Lead Time (days)",
    )


def chart_monthly_delay_rate(monthly: pd.DataFrame) -> go.Figure:
    """Monthly delay rate trend."""
    if monthly.empty:
        return _empty_figure("No data available")
    fig = px.line(
        monthly, x="Year-Month", y="Delay_Rate",
        color_discrete_sequence=[COLORS["danger"]],
        markers=True,
    )
    fig.update_traces(line=dict(width=2.5))
    return _apply_layout(
        fig, "Monthly Delay Rate", height=350,
        xaxis_title="", yaxis_title="Delay Rate (%)",
    )


# ──────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────

def _empty_figure(message: str = "No data available") -> go.Figure:
    """Create a placeholder figure for empty data states."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color=COLORS["muted"]),
    )
    return _apply_layout(fig, "", height=300)
