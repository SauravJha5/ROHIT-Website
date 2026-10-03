"""
Feature Engineering Module
===========================
Creates derived columns including Factory assignment, temporal features,
delay flags, route identifiers, and the Analytical Route Efficiency Score.
"""

import pandas as pd
import numpy as np
import streamlit as st


# ──────────────────────────────────────────────────────────
# Product → Factory Mapping
# ──────────────────────────────────────────────────────────
PRODUCT_FACTORY_MAP = {
    # Chocolate → Lot's O' Nuts
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    # Chocolate → Wicked Choccy's
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    # Sugar → Sugar Shack
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    # Sugar → Secret Factory
    "Everlasting Gobstopper": "Secret Factory",
    # Sugar → The Other Factory
    "Hair Toffee": "The Other Factory",
    # Other → Sugar Shack
    "Fizzy Lifting Drinks": "Sugar Shack",
    # Other → Secret Factory
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    # Other → The Other Factory
    "Kazookles": "The Other Factory",
}

FACTORY_COORDINATES = {
    "Lot's O' Nuts": {"lat": 32.881893, "lon": -111.768036},
    "Wicked Choccy's": {"lat": 32.076176, "lon": -81.088371},
    "Sugar Shack": {"lat": 48.11914, "lon": -96.18115},
    "Secret Factory": {"lat": 41.446333, "lon": -90.565487},
    "The Other Factory": {"lat": 35.1175, "lon": -89.971107},
}

# Factory category (for display)
FACTORY_DIVISION = {
    "Lot's O' Nuts": "Chocolate",
    "Wicked Choccy's": "Chocolate",
    "Sugar Shack": "Sugar / Other",
    "Secret Factory": "Sugar / Other",
    "The Other Factory": "Sugar / Other",
}


@st.cache_data(show_spinner="Engineering features...")
def engineer_features(df: pd.DataFrame) -> tuple:
    """
    Create all derived columns for analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataframe from data_cleaning module.

    Returns
    -------
    tuple of (pd.DataFrame, dict)
        - DataFrame with new feature columns
        - Feature engineering report
    """
    report = {"unmapped_products": [], "factories_assigned": {}}
    df = df.copy()

    # ── 1. Factory Assignment ──
    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY_MAP)

    unmapped = df[df["Factory"].isna()]["Product Name"].unique()
    if len(unmapped) > 0:
        report["unmapped_products"] = list(unmapped)
        df.loc[df["Factory"].isna(), "Factory"] = "Unknown Factory"

    factory_counts = df["Factory"].value_counts().to_dict()
    report["factories_assigned"] = factory_counts

    # ── 2. Factory Coordinates ──
    df["Factory Latitude"] = df["Factory"].map(
        lambda f: FACTORY_COORDINATES.get(f, {}).get("lat", None)
    )
    df["Factory Longitude"] = df["Factory"].map(
        lambda f: FACTORY_COORDINATES.get(f, {}).get("lon", None)
    )

    # ── 3. Temporal Features ──
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%B")
    df["Order Week"] = df["Order Date"].dt.isocalendar().week.astype(int)
    df["Order Day"] = df["Order Date"].dt.day
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)

    # ── 4. Route Identifiers ──
    df["Route"] = df["Factory"] + " → " + df["State/Province"]
    df["Factory Region Route"] = df["Factory"] + " → " + df["Region"]
    df["Factory State Route"] = df["Route"]  # Alias for clarity

    # ── 5. Country flag ──
    df["Is US"] = df["Country/Region"] == "United States"

    return df, report


def apply_delay_flag(df: pd.DataFrame, threshold: int = 5) -> pd.DataFrame:
    """
    Apply delay flags based on the selected lead-time threshold.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'Shipping Lead Time' column.
    threshold : int
        Number of days above which a shipment is considered delayed.

    Returns
    -------
    pd.DataFrame
        DataFrame with 'Delay Flag' column added.
    """
    df = df.copy()
    df["Delay Flag"] = (df["Shipping Lead Time"] > threshold).astype(int)
    return df
