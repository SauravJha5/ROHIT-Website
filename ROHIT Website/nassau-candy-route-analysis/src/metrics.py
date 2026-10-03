"""
Metrics Module
==============
Computes KPI cards and summary statistics for the dashboard.
"""

import pandas as pd
import numpy as np


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute executive-level KPI metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered and delay-flagged dataframe.

    Returns
    -------
    dict
        Dictionary of KPI values.
    """
    if df.empty:
        return {
            "total_shipments": 0,
            "avg_lead_time": 0,
            "median_lead_time": 0,
            "delay_rate": 0,
            "total_routes": 0,
            "total_sales": 0,
            "total_gross_profit": 0,
            "total_units": 0,
            "total_customers": 0,
            "total_states": 0,
            "total_factories": 0,
        }

    total_shipments = len(df)
    delay_count = int(df["Delay Flag"].sum())

    return {
        "total_shipments": total_shipments,
        "avg_lead_time": round(df["Shipping Lead Time"].mean(), 2),
        "median_lead_time": int(df["Shipping Lead Time"].median()),
        "delay_rate": round(delay_count / total_shipments * 100, 2)
        if total_shipments > 0
        else 0,
        "delay_count": delay_count,
        "total_routes": df["Route"].nunique(),
        "total_sales": round(df["Sales"].sum(), 2),
        "total_gross_profit": round(df["Gross Profit"].sum(), 2),
        "total_units": int(df["Units"].sum()),
        "total_customers": df["Customer ID"].nunique(),
        "total_states": df["State/Province"].nunique(),
        "total_factories": df["Factory"].nunique(),
        "total_products": df["Product Name"].nunique(),
    }


def generate_key_findings(
    df: pd.DataFrame,
    route_metrics: pd.DataFrame,
    kpis: dict,
    threshold: int,
) -> list:
    """
    Generate key findings text from actual computed data.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered dataframe.
    route_metrics : pd.DataFrame
        Route-level metrics.
    kpis : dict
        KPI dictionary.
    threshold : int
        Delay threshold in days.

    Returns
    -------
    list of str
        Key findings as bullet-point strings.
    """
    findings = []

    if df.empty or route_metrics.empty:
        return ["No data available for analysis."]

    # 1. Overall performance
    findings.append(
        f"Across **{kpis['total_shipments']:,}** shipments, the average "
        f"order-to-ship lead time is **{kpis['avg_lead_time']} days** "
        f"with a **{kpis['delay_rate']}%** delay rate "
        f"(threshold: >{threshold} days)."
    )

    # 2. Ship mode insight
    mode_lt = df.groupby("Ship Mode")["Shipping Lead Time"].mean()
    fastest = mode_lt.idxmin()
    slowest = mode_lt.idxmax()
    findings.append(
        f"**{fastest}** shipping has the lowest average lead time "
        f"({mode_lt[fastest]:.1f} days), while **{slowest}** has the "
        f"highest ({mode_lt[slowest]:.1f} days)."
    )

    # 3. Factory insight
    factory_lt = df.groupby("Factory")["Shipping Lead Time"].mean()
    best_factory = factory_lt.idxmin()
    worst_factory = factory_lt.idxmax()
    if best_factory != worst_factory:
        findings.append(
            f"Routes originating from **{worst_factory}** show higher "
            f"average lead times ({factory_lt[worst_factory]:.1f} days) "
            f"compared to **{best_factory}** "
            f"({factory_lt[best_factory]:.1f} days)."
        )

    # 4. Region insight
    region_lt = df.groupby("Region")["Shipping Lead Time"].mean()
    worst_region = region_lt.idxmax()
    best_region = region_lt.idxmin()
    findings.append(
        f"The **{worst_region}** region has the highest average lead time "
        f"({region_lt[worst_region]:.1f} days), while **{best_region}** "
        f"has the lowest ({region_lt[best_region]:.1f} days)."
    )

    # 5. Route concentration
    qualified = route_metrics[route_metrics["Total_Shipments"] >= 5]
    if not qualified.empty:
        top_route = qualified.nlargest(1, "Efficiency_Score").iloc[0]
        bottom_route = qualified.nsmallest(1, "Efficiency_Score").iloc[0]
        route_col = [c for c in qualified.columns if "Route" in c or c == qualified.columns[0]][0]
        findings.append(
            f"Most efficient route: **{top_route[route_col]}** "
            f"(score: {top_route['Efficiency_Score']:.1f}, "
            f"{int(top_route['Total_Shipments'])} shipments). "
            f"Least efficient: **{bottom_route[route_col]}** "
            f"(score: {bottom_route['Efficiency_Score']:.1f}, "
            f"{int(bottom_route['Total_Shipments'])} shipments)."
        )

    # 6. Volume concentration
    top_states = df["State/Province"].value_counts().head(3)
    state_str = ", ".join(
        [f"**{s}** ({c:,})" for s, c in top_states.items()]
    )
    findings.append(
        f"Top states by shipment volume: {state_str}."
    )

    return findings


def compute_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute state-level metrics for geographic analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered dataframe.

    Returns
    -------
    pd.DataFrame
        State-level aggregated metrics.
    """
    if df.empty:
        return pd.DataFrame()

    state_agg = df.groupby("State/Province").agg(
        Shipments=("Row ID", "count"),
        Avg_Lead_Time=("Shipping Lead Time", "mean"),
        Median_Lead_Time=("Shipping Lead Time", "median"),
        Delay_Count=("Delay Flag", "sum"),
        Total_Sales=("Sales", "sum"),
        Total_Units=("Units", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum"),
        Region=("Region", "first"),
        Country=("Country/Region", "first"),
    ).reset_index()

    state_agg["Delay_Rate"] = (
        state_agg["Delay_Count"] / state_agg["Shipments"] * 100
    ).round(2)

    # Compute state-level efficiency score (same methodology as route-level)
    max_lt = state_agg["Avg_Lead_Time"].max()
    min_lt = state_agg["Avg_Lead_Time"].min()

    if max_lt == min_lt:
        state_agg["Efficiency_Score"] = 100.0
    else:
        lt_score = 100 * (max_lt - state_agg["Avg_Lead_Time"]) / (
            max_lt - min_lt
        )
        delay_score = 100 - state_agg["Delay_Rate"]
        state_agg["Efficiency_Score"] = (
            0.7 * lt_score + 0.3 * delay_score
        ).round(2)

    return state_agg


# US State abbreviation mapping for Plotly choropleth
US_STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

# Canadian province abbreviations
CA_PROVINCE_ABBREV = {
    "Alberta": "AB", "British Columbia": "BC", "Manitoba": "MB",
    "New Brunswick": "NB", "Newfoundland and Labrador": "NL",
    "Nova Scotia": "NS", "Ontario": "ON", "Prince Edward Island": "PE",
    "Quebec": "QC", "Saskatchewan": "SK",
}
