"""
Data Loader Module
==================
Handles loading the Nassau Candy dataset from CSV with caching.
"""

import pandas as pd
import streamlit as st
import os


@st.cache_data(show_spinner="Loading dataset...")
def load_dataset(filepath: str = None) -> pd.DataFrame:
    """
    Load the Nassau Candy Distributor dataset from CSV.

    Parameters
    ----------
    filepath : str, optional
        Path to the CSV file. Defaults to data/dataset.csv relative
        to the project root.

    Returns
    -------
    pd.DataFrame
        Raw dataframe as read from CSV.

    Raises
    ------
    FileNotFoundError
        If the dataset file does not exist at the specified path.
    """
    if filepath is None:
        # Resolve relative to this file's location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "data", "dataset.csv")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at: {filepath}\n"
            "Please ensure the CSV file is placed in the data/ directory."
        )

    df = pd.read_csv(filepath)

    # Validate minimum expected columns
    required_cols = [
        "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
        "Customer ID", "Country/Region", "City", "State/Province",
        "Division", "Region", "Product Name", "Sales", "Units",
        "Gross Profit", "Cost"
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset is missing expected columns: {missing_cols}\n"
            f"Found columns: {list(df.columns)}"
        )

    return df


def get_dataset_info(df: pd.DataFrame) -> dict:
    """
    Generate a summary dictionary of the dataset for display purposes.

    Parameters
    ----------
    df : pd.DataFrame
        The loaded dataset.

    Returns
    -------
    dict
        Dictionary containing row count, column count, data types,
        missing values, and duplicate information.
    """
    info = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
    }
    return info
