"""
Route Analysis Module
=====================
Computes route-level and factory-region-level aggregations,
the Analytical Route Efficiency Score, and bottleneck identification.
"""

import pandas as pd
import numpy as np


def compute_route_metrics(
    df: pd.DataFrame,
    route_col: str = "Route",
    threshold: int = 5,
) -> pd.DataFrame:
    """
    Aggregate shipment-level data to route-level metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered dataframe with Shipping Lead Time and Delay Flag.
    route_col : str
        Column to group by (e.g. 'Route' or 'Factory Region Route').
    threshold : int
        Delay threshold in days (for labeling purposes).

    Returns
    -------
    pd.DataFrame
        Route-level metrics including efficiency score.
    """
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby(route_col).agg(
        Total_Shipments=("Row ID", "count"),
        Avg_Lead_Time=("Shipping Lead Time", "mean"),
        Median_Lead_Time=("Shipping Lead Time", "median"),
        Min_Lead_Time=("Shipping Lead Time", "min"),
        Max_Lead_Time=("Shipping Lead Time", "max"),
        Std_Lead_Time=("Shipping Lead Time", "std"),
        Delay_Count=("Delay Flag", "sum"),
        Total_Sales=("Sales", "sum"),
        Avg_Sales=("Sales", "mean"),
        Total_Units=("Units", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum"),
        Avg_Gross_Profit=("Gross Profit", "mean"),
    ).reset_index()

    # Fill NaN std (routes with 1 shipment) with 0
    agg["Std_Lead_Time"] = agg["Std_Lead_Time"].fillna(0)

    # Delay Rate
    agg["Delay_Rate"] = (
        agg["Delay_Count"] / agg["Total_Shipments"] * 100
    ).round(2)

    # Extract Factory and State/Region from route string
    if route_col == "Route" or route_col == "Factory State Route":
        parts = agg[route_col].str.split(" → ", expand=True)
        agg["Factory"] = parts[0]
        agg["State"] = parts[1]
        # Map State to Region from the original data
        state_region = df.drop_duplicates("State/Province")[
            ["State/Province", "Region"]
        ].set_index("State/Province")["Region"]
        agg["Region"] = agg["State"].map(state_region)
    elif route_col == "Factory Region Route":
        parts = agg[route_col].str.split(" → ", expand=True)
        agg["Factory"] = parts[0]
        agg["Region"] = parts[1]

    # Compute Efficiency Score
    agg = _compute_efficiency_score(agg)

    # Round numeric columns
    numeric_cols = agg.select_dtypes(include=[np.number]).columns
    agg[numeric_cols] = agg[numeric_cols].round(2)

    # Sort by efficiency score descending
    agg = agg.sort_values("Efficiency_Score", ascending=False).reset_index(
        drop=True
    )

    return agg


def _compute_efficiency_score(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Analytical Route Efficiency Score.

    Methodology
    -----------
    The score combines two normalized components:

    1. Lead Time Score (weight: 0.7):
       Measures how a route's average lead time compares to the best
       and worst routes in the dataset.

       Lead Time Score = 100 × (Max_Avg_LT - Route_Avg_LT)
                              / (Max_Avg_LT - Min_Avg_LT)

       A route with the lowest average lead time scores 100;
       the highest scores 0.

    2. Delay Performance Score (weight: 0.3):
       Derived from the delay rate.

       Delay Score = 100 - Delay_Rate

       A route with 0% delays scores 100; 100% delays scores 0.

    Final Score:
       Efficiency Score = 0.7 × Lead Time Score + 0.3 × Delay Score

    Edge Cases:
    - If all routes have the same average lead time (max == min),
      Lead Time Score defaults to 100 for all routes.
    - Routes with only 1 shipment have Std = 0; they are scored
      normally but should be interpreted with caution.

    This score is an analytical construct for comparative ranking.
    It is NOT an official Nassau Candy KPI.
    """
    max_lt = agg["Avg_Lead_Time"].max()
    min_lt = agg["Avg_Lead_Time"].min()

    if max_lt == min_lt:
        agg["Lead_Time_Score"] = 100.0
    else:
        agg["Lead_Time_Score"] = (
            100 * (max_lt - agg["Avg_Lead_Time"]) / (max_lt - min_lt)
        )

    agg["Delay_Score"] = 100 - agg["Delay_Rate"]

    agg["Efficiency_Score"] = (
        0.7 * agg["Lead_Time_Score"] + 0.3 * agg["Delay_Score"]
    )

    return agg


def get_top_bottom_routes(
    route_metrics: pd.DataFrame,
    n: int = 10,
    min_shipments: int = 5,
) -> tuple:
    """
    Get top N and bottom N routes by Efficiency Score.

    Parameters
    ----------
    route_metrics : pd.DataFrame
        Route-level metrics from compute_route_metrics.
    n : int
        Number of top/bottom routes to return.
    min_shipments : int
        Minimum shipment count filter. Routes below this threshold
        are excluded from ranking but a warning flag is added.

    Returns
    -------
    tuple of (pd.DataFrame, pd.DataFrame, int)
        - Top N routes
        - Bottom N routes
        - Number of routes excluded by min_shipments filter
    """
    if route_metrics.empty:
        empty = pd.DataFrame()
        return empty, empty, 0

    qualified = route_metrics[
        route_metrics["Total_Shipments"] >= min_shipments
    ].copy()
    excluded = len(route_metrics) - len(qualified)

    top = qualified.nlargest(n, "Efficiency_Score").reset_index(drop=True)
    top.index = top.index + 1  # 1-based ranking
    top.index.name = "Rank"

    bottom = qualified.nsmallest(n, "Efficiency_Score").reset_index(drop=True)
    bottom.index = bottom.index + 1
    bottom.index.name = "Rank"

    return top, bottom, excluded


def identify_bottlenecks(
    route_metrics: pd.DataFrame,
    volume_percentile: float = 75,
    lead_time_percentile: float = 75,
) -> dict:
    """
    Identify shipping bottlenecks using transparent methodology.

    Methodology
    -----------
    A. High Lead-Time Routes: Routes with average lead time above
       the specified percentile.

    B. High Delay-Rate Routes: Routes with delay rate above
       the specified percentile.

    C. High-Volume + Poor-Performance Routes: Routes above BOTH
       the volume percentile AND the lead-time percentile.
       These are the most operationally impactful bottlenecks.

    D. Factory Performance: Factories ranked by average route
       lead time across their routes.

    Parameters
    ----------
    route_metrics : pd.DataFrame
        Route-level metrics from compute_route_metrics.
    volume_percentile : float
        Percentile threshold for "high volume" (default: 75th).
    lead_time_percentile : float
        Percentile threshold for "high lead time" (default: 75th).

    Returns
    -------
    dict
        Dictionary with keys: high_lead_time, high_delay_rate,
        high_volume_poor_perf, factory_performance.
    """
    if route_metrics.empty:
        return {
            "high_lead_time": pd.DataFrame(),
            "high_delay_rate": pd.DataFrame(),
            "high_volume_poor_perf": pd.DataFrame(),
            "factory_performance": pd.DataFrame(),
        }

    lt_threshold = route_metrics["Avg_Lead_Time"].quantile(
        lead_time_percentile / 100
    )
    vol_threshold = route_metrics["Total_Shipments"].quantile(
        volume_percentile / 100
    )
    dr_threshold = route_metrics["Delay_Rate"].quantile(
        lead_time_percentile / 100
    )

    # A. High lead-time routes
    high_lt = route_metrics[
        route_metrics["Avg_Lead_Time"] >= lt_threshold
    ].copy()

    # B. High delay-rate routes
    high_dr = route_metrics[
        route_metrics["Delay_Rate"] >= dr_threshold
    ].copy()

    # C. High volume + poor performance
    high_vol_poor = route_metrics[
        (route_metrics["Total_Shipments"] >= vol_threshold)
        & (route_metrics["Avg_Lead_Time"] >= lt_threshold)
    ].copy()

    # D. Factory-level performance
    if "Factory" in route_metrics.columns:
        factory_perf = (
            route_metrics.groupby("Factory")
            .agg(
                Routes=("Total_Shipments", "count"),
                Total_Shipments=("Total_Shipments", "sum"),
                Avg_Lead_Time=("Avg_Lead_Time", "mean"),
                Avg_Delay_Rate=("Delay_Rate", "mean"),
                Avg_Efficiency=("Efficiency_Score", "mean"),
            )
            .reset_index()
            .sort_values("Avg_Lead_Time", ascending=False)
        )
    else:
        factory_perf = pd.DataFrame()

    return {
        "high_lead_time": high_lt,
        "high_delay_rate": high_dr,
        "high_volume_poor_perf": high_vol_poor,
        "factory_performance": factory_perf,
        "thresholds": {
            "lead_time": round(lt_threshold, 2),
            "volume": round(vol_threshold, 2),
            "delay_rate": round(dr_threshold, 2),
        },
    }


def compute_ship_mode_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ship-mode-level aggregation.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered dataframe.

    Returns
    -------
    pd.DataFrame
        Ship mode metrics.
    """
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby("Ship Mode").agg(
        Shipments=("Row ID", "count"),
        Avg_Lead_Time=("Shipping Lead Time", "mean"),
        Median_Lead_Time=("Shipping Lead Time", "median"),
        Min_Lead_Time=("Shipping Lead Time", "min"),
        Max_Lead_Time=("Shipping Lead Time", "max"),
        Std_Lead_Time=("Shipping Lead Time", "std"),
        Delay_Count=("Delay Flag", "sum"),
        Total_Sales=("Sales", "sum"),
        Avg_Sales=("Sales", "mean"),
        Total_Units=("Units", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum"),
    ).reset_index()

    agg["Delay_Rate"] = (
        agg["Delay_Count"] / agg["Shipments"] * 100
    ).round(2)

    agg["Std_Lead_Time"] = agg["Std_Lead_Time"].fillna(0)

    # Sort by average lead time
    mode_order = {"Same Day": 0, "First Class": 1, "Second Class": 2, "Standard Class": 3}
    agg["_sort"] = agg["Ship Mode"].map(mode_order)
    agg = agg.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)

    return agg


def compute_time_series(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute monthly time series metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered dataframe.

    Returns
    -------
    pd.DataFrame
        Monthly aggregated metrics.
    """
    if df.empty:
        return pd.DataFrame()

    monthly = df.groupby("Year-Month").agg(
        Shipments=("Row ID", "count"),
        Avg_Lead_Time=("Shipping Lead Time", "mean"),
        Median_Lead_Time=("Shipping Lead Time", "median"),
        Delay_Count=("Delay Flag", "sum"),
        Total_Sales=("Sales", "sum"),
        Total_Units=("Units", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum"),
    ).reset_index()

    monthly["Delay_Rate"] = (
        monthly["Delay_Count"] / monthly["Shipments"] * 100
    ).round(2)

    monthly = monthly.sort_values("Year-Month").reset_index(drop=True)

    return monthly
