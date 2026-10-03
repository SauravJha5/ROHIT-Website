# 🍬 Nassau Candy Distributor — Factory-to-Customer Shipping Route Efficiency Analysis

A professional data analytics project analyzing shipping route performance for Nassau Candy Distributor. Built with Python, Pandas, Plotly, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple.svg)](https://plotly.com)

---

## 📋 Project Overview

This project analyzes factory-to-customer shipping performance across Nassau Candy Distributor's distribution network, spanning 5 factories, 196 routes, and 59 states/provinces in the US and Canada.

The analysis answers:
- Which factory-to-customer routes are most/least efficient?
- Which routes consistently experience delays?
- How does shipping performance vary by factory, region, state, and ship mode?
- Which geographical areas have poor shipping performance?
- Which high-volume routes have poor performance?
- How does shipping mode affect order-to-ship lead time?

---

## 💼 Business Problem

Efficient shipping operations directly impact customer satisfaction and profitability. This project provides data-driven insights into:

- **Route-level performance** across 196 factory-to-state routes
- **Bottleneck identification** for high-volume routes with elevated lead times
- **Ship mode optimization** opportunities
- **Geographic performance patterns** across US states and Canadian provinces

---

## 🎯 Objectives

1. Compute order-to-ship lead time for all 10,194 shipments
2. Derive factory assignments from product mapping
3. Build transparent route efficiency scoring methodology
4. Create interactive dashboard for stakeholder exploration
5. Identify actionable bottlenecks and operational insights
6. Document methodology and findings

---

## 📊 Dataset

| Attribute | Detail |
|-----------|--------|
| Records | 10,194 |
| Date Range | Jan 2024 – Dec 2025 |
| Countries | US (9,994) + Canada (200) |
| States/Provinces | 59 |
| Products | 15 |
| Factories | 5 (derived) |
| Ship Modes | 4 |

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Dashboard | Streamlit |
| Data Format | CSV |

---

## 🏗️ Architecture

```
Raw CSV Data
    ↓
Data Loader (data_loader.py)
    ↓
Data Cleaning (data_cleaning.py)
  - Date parsing & decoding
  - Validation
    ↓
Feature Engineering (feature_engineering.py)
  - Factory mapping
  - Temporal features
  - Route identifiers
  - Delay flags
    ↓
Route Analysis (route_analysis.py)
  - Route aggregation
  - Efficiency scoring
  - Bottleneck detection
  - Ship mode analysis
    ↓
Streamlit Dashboard (app.py)
  - 5 interactive pages
  - Global filters
  - Plotly charts
```

---

## 📐 Methodology

### Order-to-Ship Lead Time
Measures the number of days between order date and ship date. This is NOT delivery time to customer (no delivery date exists in the dataset).

### Analytical Route Efficiency Score
A composite score (0-100) combining:
- **Lead Time Score** (70% weight): Normalized average lead time
- **Delay Score** (30% weight): Derived from delay rate

This is an analytical construct, not an official KPI.

### Delay Threshold
User-adjustable (default: 5 days). Not an official SLA.

### Bottleneck Identification
Routes above the 75th percentile in BOTH shipment volume AND average lead time are flagged as bottlenecks.

---

## 📈 Key Performance Indicators

| KPI | Value |
|-----|-------|
| Avg Lead Time | 4.59 days |
| Delay Rate (>5d) | 32.15% |
| Total Routes | 196 |
| Total Sales | $141,783.63 |
| Gross Profit | $93,442.80 |

---

## 🖥️ Dashboard Features

### Page 1: Executive Overview
KPI cards, monthly trends, factory comparison, regional breakdown, key findings

### Page 2: Route Efficiency
Route leaderboard, top/bottom routes, scatter analysis, efficiency distribution, bottleneck detection

### Page 3: Geographic Analysis
Interactive US choropleth map, factory locations, state-level metrics, regional comparison

### Page 4: Ship Mode Analysis
Volume distribution, lead time comparison, delay rates, distributions, monthly trends

### Page 5: Route Drill-Down
Factory → State → Ship Mode selection, route KPIs, product mix, monthly performance, order-level table

### Global Filters (Sidebar)
Date range, Region, State, Factory, Ship Mode, Delay threshold slider

---

## 📁 Project Structure

```
nassau-candy-route-analysis/
│
├── app.py                      # Streamlit dashboard application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── data/
│   └── dataset.csv             # Nassau Candy dataset
│
├── src/
│   ├── __init__.py             # Package init
│   ├── data_loader.py          # Dataset loading with caching
│   ├── data_cleaning.py        # Date decoding & validation
│   ├── feature_engineering.py  # Factory mapping & features
│   ├── route_analysis.py       # Route metrics & efficiency
│   ├── metrics.py              # KPIs & state metrics
│   └── visualizations.py       # Plotly chart library
│
├── tests/
│   └── test_analysis.py        # Validation test suite
│
└── docs/
    ├── research_paper.md       # Full research paper
    └── executive_summary.md    # Executive summary
```

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/nassau-candy-route-analysis.git
cd nassau-candy-route-analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Run tests:**
```bash
python tests/test_analysis.py
```

---

## 💡 Example Usage

1. Launch the dashboard with `streamlit run app.py`
2. Use sidebar filters to select date range, region, factory, and ship mode
3. Adjust the delay threshold slider to see how different thresholds affect delay rates
4. Navigate between tabs to explore different analytical perspectives
5. Use the Route Drill-Down page to investigate specific factory-to-state routes
6. Expand methodology sections for transparent scoring explanations

---

## 🔍 Key Insights

1. **Standard Class shipping** accounts for 60% of volume but 48.82% delay rate — the primary driver of overall delay metrics
2. **Ship mode selection is the strongest predictor** of lead time, more so than geography or factory
3. **7 high-volume bottleneck routes** identified for potential operational review
4. **Regional variation is modest** (0.15-day spread), indicating consistent geographic coverage
5. **Route efficiency scores range from 5.0 to 100.0**, enabling clear prioritization

---

## ⚠️ Limitations

- Measures **order-to-ship time only**, not delivery time
- Delay threshold is **analytical**, not an official SLA
- Factory assignment is **derived** from product mapping
- Low-volume routes have **limited statistical reliability**
- **Correlation ≠ causation** for observed patterns

---

## 🔮 Future Improvements

- Incorporate delivery date data for end-to-end analysis
- Add shipping cost data for cost-efficiency optimization
- Implement time-series forecasting for lead time trends
- Add customer segmentation analysis
- Build automated alerting for performance degradation
- Seasonal decomposition for peak-period analysis

---

## 📄 License

This project is for portfolio/educational purposes.

---

*All statistics in this project are computed from the actual dataset. No results are fabricated.*
