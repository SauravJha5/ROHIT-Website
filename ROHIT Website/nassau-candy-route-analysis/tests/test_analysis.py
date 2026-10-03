"""
Test Suite for Nassau Candy Route Analysis
==========================================
Validates data pipeline, calculations, and edge cases.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_dataset_loading():
    """Test that the dataset loads successfully."""
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "dataset.csv"
    )
    df = pd.read_csv(filepath)
    assert len(df) > 0, "Dataset should not be empty"
    assert len(df.columns) == 18, f"Expected 18 columns, got {len(df.columns)}"
    print(f"✓ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def test_date_parsing(df):
    """Test date parsing logic."""
    order_dates = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
    ship_dates = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")

    assert order_dates.isna().sum() == 0, "All Order Dates should parse"
    assert ship_dates.isna().sum() == 0, "All Ship Dates should parse"
    print(f"✓ All dates parsed successfully")
    print(f"  Order Date range: {order_dates.min().date()} to {order_dates.max().date()}")
    print(f"  Ship Date range: {ship_dates.min().date()} to {ship_dates.max().date()}")


def test_factory_mapping(df):
    """Test product → factory mapping."""
    from src.feature_engineering import PRODUCT_FACTORY_MAP

    products = df["Product Name"].unique()
    unmapped = [p for p in products if p not in PRODUCT_FACTORY_MAP]

    assert len(unmapped) == 0, f"Unmapped products: {unmapped}"
    print(f"✓ All {len(products)} products mapped to factories")

    # Verify mapping completeness
    for product, factory in PRODUCT_FACTORY_MAP.items():
        if product in products:
            assert factory in [
                "Lot's O' Nuts", "Wicked Choccy's", "Sugar Shack",
                "Secret Factory", "The Other Factory"
            ], f"Invalid factory '{factory}' for product '{product}'"
    print(f"✓ All factory assignments are valid")


def test_lead_time_calculation():
    """Test the date decoding and lead time calculation."""
    from src.data_cleaning import clean_dataset

    filepath = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "dataset.csv"
    )
    df_raw = pd.read_csv(filepath)

    # Mock st.cache_data for non-Streamlit context
    import streamlit as st
    df_clean, report = clean_dataset.__wrapped__(df_raw)

    # Lead time should be non-negative
    negative_lt = (df_clean["Shipping Lead Time"] < 0).sum()
    assert negative_lt == 0, f"{negative_lt} records have negative lead time"
    print(f"✓ No negative lead times")

    # Lead time should be in reasonable range (0-12 days)
    max_lt = df_clean["Shipping Lead Time"].max()
    assert max_lt <= 15, f"Max lead time {max_lt} exceeds reasonable range"
    print(f"✓ Lead time range: {df_clean['Shipping Lead Time'].min()}-{max_lt} days")

    # Ship mode ordering should be correct
    mode_lt = df_clean.groupby("Ship Mode")["Shipping Lead Time"].mean()
    assert mode_lt["Same Day"] < mode_lt["First Class"], "Same Day should be faster than First Class"
    assert mode_lt["First Class"] < mode_lt["Second Class"], "First Class should be faster than Second Class"
    assert mode_lt["Second Class"] < mode_lt["Standard Class"], "Second Class should be faster than Standard Class"
    print(f"✓ Ship mode ordering is correct:")
    for mode in ["Same Day", "First Class", "Second Class", "Standard Class"]:
        print(f"  {mode}: {mode_lt[mode]:.2f} days avg")

    return df_clean


def test_delay_calculation(df_clean):
    """Test delay flag calculation."""
    from src.feature_engineering import apply_delay_flag

    # Test with threshold = 5
    df_delayed = apply_delay_flag(df_clean, threshold=5)
    total = len(df_delayed)
    delayed = df_delayed["Delay Flag"].sum()
    delay_rate = delayed / total * 100

    assert "Delay Flag" in df_delayed.columns, "Delay Flag column should exist"
    assert set(df_delayed["Delay Flag"].unique()).issubset({0, 1}), "Delay Flag should be 0 or 1"
    print(f"✓ Delay calculation (threshold=5): {delayed}/{total} delayed ({delay_rate:.1f}%)")

    # Test with threshold = 0 (everything > 0 is delayed)
    df_d0 = apply_delay_flag(df_clean, threshold=0)
    same_day_zero = df_d0[
        (df_d0["Ship Mode"] == "Same Day") & (df_d0["Shipping Lead Time"] == 0)
    ]
    if len(same_day_zero) > 0:
        assert (same_day_zero["Delay Flag"] == 0).all(), "Same-day with 0 lead time should not be delayed"
    print(f"✓ Delay threshold=0 test passed")

    return df_delayed


def test_route_aggregation(df):
    """Test route-level aggregation."""
    from src.feature_engineering import engineer_features, apply_delay_flag
    from src.route_analysis import compute_route_metrics

    df_feat, _ = engineer_features.__wrapped__(df)
    df_feat = apply_delay_flag(df_feat, threshold=5)

    route_metrics = compute_route_metrics(df_feat, "Route", 5)

    assert len(route_metrics) > 0, "Should have at least one route"
    assert "Efficiency_Score" in route_metrics.columns, "Should have efficiency score"
    assert route_metrics["Efficiency_Score"].between(0, 100).all(), "Scores should be 0-100"
    assert (route_metrics["Total_Shipments"] > 0).all(), "All routes should have shipments"
    print(f"✓ Route aggregation: {len(route_metrics)} routes computed")
    print(f"  Efficiency score range: {route_metrics['Efficiency_Score'].min():.1f} - {route_metrics['Efficiency_Score'].max():.1f}")

    return route_metrics


def test_efficiency_score(route_metrics):
    """Test efficiency score properties."""
    # Scores should be between 0 and 100
    assert route_metrics["Efficiency_Score"].min() >= 0, "Min score should be >= 0"
    assert route_metrics["Efficiency_Score"].max() <= 100, "Max score should be <= 100"

    # Routes with lower avg lead time should generally have higher scores
    # (not strictly due to delay rate component)
    corr = route_metrics["Avg_Lead_Time"].corr(route_metrics["Efficiency_Score"])
    assert corr < 0, "Lead time and efficiency should be negatively correlated"
    print(f"✓ Efficiency score validation passed (LT-score correlation: {corr:.3f})")


def test_empty_filter_handling():
    """Test that analytics handle empty DataFrames gracefully."""
    from src.route_analysis import (
        compute_route_metrics,
        compute_ship_mode_analysis,
        compute_time_series,
        get_top_bottom_routes,
        identify_bottlenecks,
    )
    from src.metrics import compute_kpis, compute_state_metrics

    empty_df = pd.DataFrame()

    # These should return empty results without errors
    assert compute_route_metrics(empty_df).empty
    assert compute_ship_mode_analysis(empty_df).empty
    assert compute_time_series(empty_df).empty
    assert compute_state_metrics(empty_df).empty

    kpis = compute_kpis(empty_df)
    assert kpis["total_shipments"] == 0

    top, bottom, excl = get_top_bottom_routes(empty_df)
    assert top.empty and bottom.empty

    bottlenecks = identify_bottlenecks(empty_df)
    assert bottlenecks["high_lead_time"].empty

    print(f"✓ Empty filter handling: all analytics return gracefully")


def test_ship_mode_analysis(df):
    """Test ship mode analysis."""
    from src.feature_engineering import engineer_features, apply_delay_flag
    from src.route_analysis import compute_ship_mode_analysis

    df_feat, _ = engineer_features.__wrapped__(df)
    df_feat = apply_delay_flag(df_feat, threshold=5)
    mode_metrics = compute_ship_mode_analysis(df_feat)

    assert len(mode_metrics) == 4, "Should have 4 ship modes"
    expected_modes = {"Same Day", "First Class", "Second Class", "Standard Class"}
    assert set(mode_metrics["Ship Mode"]) == expected_modes
    print(f"✓ Ship mode analysis: {len(mode_metrics)} modes analyzed")
    for _, row in mode_metrics.iterrows():
        print(f"  {row['Ship Mode']}: {int(row['Shipments'])} shipments, {row['Avg_Lead_Time']:.2f} avg LT")


def test_geographic_metrics(df):
    """Test state-level metrics."""
    from src.feature_engineering import engineer_features, apply_delay_flag
    from src.metrics import compute_state_metrics

    df_feat, _ = engineer_features.__wrapped__(df)
    df_feat = apply_delay_flag(df_feat, threshold=5)
    state_metrics = compute_state_metrics(df_feat)

    assert len(state_metrics) > 0, "Should have state metrics"
    assert "Efficiency_Score" in state_metrics.columns
    us_states = state_metrics[state_metrics["Country"] == "United States"]
    assert len(us_states) >= 49, f"Expected ≥49 US states, got {len(us_states)}"
    print(f"✓ Geographic metrics: {len(state_metrics)} states/provinces")
    print(f"  US states: {len(us_states)}, Canadian provinces: {len(state_metrics) - len(us_states)}")


# ──────────────────────────────────────────────────────────
# Run All Tests
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("NASSAU CANDY ROUTE ANALYSIS — TEST SUITE")
    print("=" * 60)

    errors = []
    df = None
    df_clean = None
    df_delayed = None
    route_metrics = None

    try:
        print("\n--- Test 1: Dataset Loading ---")
        df = test_dataset_loading()
    except Exception as e:
        errors.append(f"Dataset Loading: {e}")
        print(f"✗ {e}")

    if df is not None:
        try:
            print("\n--- Test 2: Date Parsing ---")
            test_date_parsing(df)
        except Exception as e:
            errors.append(f"Date Parsing: {e}")
            print(f"✗ {e}")

        try:
            print("\n--- Test 3: Factory Mapping ---")
            test_factory_mapping(df)
        except Exception as e:
            errors.append(f"Factory Mapping: {e}")
            print(f"✗ {e}")

    try:
        print("\n--- Test 4: Lead Time Calculation ---")
        df_clean = test_lead_time_calculation()
    except Exception as e:
        errors.append(f"Lead Time Calculation: {e}")
        print(f"✗ {e}")

    if df_clean is not None:
        try:
            print("\n--- Test 5: Delay Calculation ---")
            df_delayed = test_delay_calculation(df_clean)
        except Exception as e:
            errors.append(f"Delay Calculation: {e}")
            print(f"✗ {e}")

        try:
            print("\n--- Test 6: Route Aggregation ---")
            route_metrics = test_route_aggregation(df_clean)
        except Exception as e:
            errors.append(f"Route Aggregation: {e}")
            print(f"✗ {e}")

        if route_metrics is not None:
            try:
                print("\n--- Test 7: Efficiency Score ---")
                test_efficiency_score(route_metrics)
            except Exception as e:
                errors.append(f"Efficiency Score: {e}")
                print(f"✗ {e}")

        try:
            print("\n--- Test 9: Ship Mode Analysis ---")
            test_ship_mode_analysis(df_clean)
        except Exception as e:
            errors.append(f"Ship Mode Analysis: {e}")
            print(f"✗ {e}")

        try:
            print("\n--- Test 10: Geographic Metrics ---")
            test_geographic_metrics(df_clean)
        except Exception as e:
            errors.append(f"Geographic Metrics: {e}")
            print(f"✗ {e}")

    try:
        print("\n--- Test 8: Empty Filter Handling ---")
        test_empty_filter_handling()
    except Exception as e:
        errors.append(f"Empty Filter Handling: {e}")
        print(f"✗ {e}")

    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"FAILED — {len(errors)} test(s) failed:")
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("ALL 10 TESTS PASSED ✓")
    print("=" * 60)
