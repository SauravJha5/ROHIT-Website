# Factory-to-Customer Shipping Route Efficiency Analysis — Research Paper

## Nassau Candy Distributor

---

## 1. Title

**Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor: A Data-Driven Assessment of Order-to-Ship Performance Across Domestic and Cross-Border Routes**

---

## 2. Abstract

This study presents a comprehensive analysis of factory-to-customer shipping route efficiency for Nassau Candy Distributor, a confectionery distribution operation spanning 5 factories, 59 states/provinces across the United States and Canada. Analyzing 10,194 shipment records from January 2024 through December 2025, we derive order-to-ship lead time metrics, construct an Analytical Route Efficiency Score, and identify operational bottlenecks across 196 unique factory-to-state routes. Key findings include a mean order-to-ship lead time of 4.59 days, a 32.15% delay rate at a 5-day threshold, and significant variation in performance across ship modes (Same Day: 0.63 days vs. Standard Class: 5.63 days). Route efficiency scores range from 5.0 to 100.0, revealing 7 high-volume routes requiring operational review. Geographic analysis identifies Newfoundland and Labrador (8.50 days) and District of Columbia (6.00 days) as states with the highest average lead times, while Manitoba (3.83 days) and North Dakota (3.86 days) show the strongest performance.

---

## 3. Introduction

Efficient shipping operations are critical to customer satisfaction and operational profitability in consumer goods distribution. For confectionery distributors, where product freshness and seasonal demand create additional urgency, understanding the performance of factory-to-customer shipping routes enables targeted operational improvements.

Nassau Candy Distributor operates a multi-factory distribution network serving customers across North America. This analysis examines the order-to-ship lead time—the interval between order placement and shipment—across all factory-to-customer state routes, using actual transactional data rather than simulated or assumed values.

---

## 4. Business Problem

The central business questions addressed are:

1. Which factory-to-customer routes are most and least efficient?
2. Which routes consistently experience delays beyond acceptable thresholds?
3. How does shipping performance vary by factory, region, state, and ship mode?
4. Which geographical areas show poor shipping performance?
5. Which high-volume routes simultaneously exhibit poor performance?
6. How does shipping mode selection affect order-to-ship lead time?
7. What operational insights can be derived to guide process improvement?

---

## 5. Dataset Description

The dataset contains **10,194 shipment records** across **18 fields**:

| Attribute | Detail |
|-----------|--------|
| Records | 10,194 |
| Date Range | January 2, 2024 – December 31, 2025 |
| Countries | United States (9,994), Canada (200) |
| States/Provinces | 59 |
| Cities | 542 |
| Products | 15 |
| Factories | 5 (derived from product mapping) |
| Ship Modes | 4 (Same Day, First Class, Second Class, Standard Class) |
| Missing Values | 0 |
| Duplicate Records | 0 |

The dataset does not contain an explicit "Factory" column. Factory assignment is derived from Product Name using a defined mapping (see Section 7).

---

## 6. Data Cleaning

### 6.1 Date Handling

The Ship Date field contains years that are synthetically offset (2026–2030) relative to Order Dates (2024–2025). This is a characteristic of the dataset's construction.

**Decoding Methodology:**
1. Both dates are parsed as DD-MM-YYYY format.
2. The Ship Date's month and day are placed into the Order Date's year context.
3. A structural baseline of 173 days is subtracted to recover the actual order-to-ship lead time.

This produces lead times of 0–12 days with correct ship-mode ordering:
- Same Day: 0–2 days (mean: 0.63)
- First Class: 1–6 days (mean: 2.84)
- Second Class: 2–7 days (mean: 3.86)
- Standard Class: 3–12 days (mean: 5.63)

### 6.2 Validation Results

- **No missing values** across all 18 columns
- **No duplicate records**
- **No negative values** in Sales, Units, Gross Profit, or Cost
- **No negative lead times** after decoding
- **4 standard Ship Mode values** as expected
- All **15 product names** successfully map to 5 factories

### 6.3 Cleaning Decisions

No records were removed. All 10,194 records are retained for analysis with decoded lead times and validation flags.

---

## 7. Feature Engineering

### 7.1 Factory Assignment

| Product | Factory |
|---------|---------|
| Wonka Bar - Nutty Crunch Surprise | Lot's O' Nuts |
| Wonka Bar - Fudge Mallows | Lot's O' Nuts |
| Wonka Bar -Scrumdiddlyumptious | Lot's O' Nuts |
| Wonka Bar - Milk Chocolate | Wicked Choccy's |
| Wonka Bar - Triple Dazzle Caramel | Wicked Choccy's |
| Laffy Taffy, SweeTARTS, Nerds, Fun Dip | Sugar Shack |
| Everlasting Gobstopper | Secret Factory |
| Hair Toffee | The Other Factory |
| Fizzy Lifting Drinks | Sugar Shack |
| Lickable Wallpaper, Wonka Gum | Secret Factory |
| Kazookles | The Other Factory |

### 7.2 Derived Columns

- **Route:** Factory → Customer State (e.g., "Lot's O' Nuts → California")
- **Delay Flag:** Lead Time > Selected Threshold (default: 5 days)
- **Temporal features:** Order Year, Month, Quarter, Week, Day

---

## 8. Analytical Methodology

### 8.1 Route-Level Aggregation

For each of the **196 unique routes**, we compute:
- Total Shipments, Average/Median/Min/Max Lead Time, Standard Deviation
- Delay Count and Delay Rate (%)
- Total Sales, Units, and Gross Profit

### 8.2 Delay Threshold

The default delay threshold is **5 days**. This is a user-selected analytical parameter, NOT an official service-level agreement. At this threshold, **3,277 of 10,194 shipments (32.15%)** are flagged as delayed.

---

## 9. Route Efficiency Methodology

### 9.1 Analytical Route Efficiency Score

A composite score combining two normalized components:

**Lead Time Score (70% weight):**
$$\text{LT Score} = 100 \times \frac{\text{Max Avg LT} - \text{Route Avg LT}}{\text{Max Avg LT} - \text{Min Avg LT}}$$

**Delay Performance Score (30% weight):**
$$\text{Delay Score} = 100 - \text{Delay Rate}$$

**Final Score:**
$$\text{Efficiency Score} = 0.7 \times \text{LT Score} + 0.3 \times \text{Delay Score}$$

This score is an analytical construct for comparative ranking. It is **NOT** an official Nassau Candy KPI.

### 9.2 Score Distribution

Across 196 routes, efficiency scores range from **5.0 to 100.0**.

---

## 10. Exploratory Data Analysis

### 10.1 Overall KPIs

| KPI | Value |
|-----|-------|
| Total Shipments | 10,194 |
| Average Order-to-Ship Lead Time | 4.59 days |
| Median Lead Time | 5 days |
| Delay Rate (>5 days) | 32.15% |
| Total Routes | 196 |
| Total Sales | $141,783.63 |
| Total Gross Profit | $93,442.80 |
| Total Units | 38,654 |

### 10.2 Factory Performance

| Factory | Avg Lead Time | Avg Delay Rate | Routes | Shipments |
|---------|---------------|----------------|--------|-----------|
| Sugar Shack | 5.02 days | 48.5% | 15 | 33 |
| Wicked Choccy's | 4.73 days | 31.6% | 57 | 4,152 |
| Lot's O' Nuts | 4.69 days | 32.5% | 57 | 5,692 |
| Secret Factory | 4.61 days | 33.7% | 39 | 217 |
| The Other Factory | 4.22 days | 25.5% | 28 | 100 |

> **Note:** Sugar Shack's metrics should be interpreted with caution due to very low volume (33 shipments across 15 routes). The Other Factory similarly has only 100 shipments.

### 10.3 Region Performance

| Region | Avg Lead Time | Delay Rate | Shipments |
|--------|---------------|------------|-----------|
| Atlantic | 4.54 days | 30.2% | 2,986 |
| Pacific | 4.57 days | 33.2% | 3,253 |
| Gulf | 4.62 days | 32.5% | 1,620 |
| Interior | 4.69 days | 32.9% | 2,335 |

Regional variation is relatively modest (0.15-day spread), suggesting that geographic region alone does not strongly predict lead time performance.

---

## 11. Geographic Analysis

### 11.1 States with Highest Average Lead Times

| State/Province | Avg Lead Time | Shipments |
|----------------|---------------|-----------|
| Newfoundland and Labrador | 8.50 days | 6 |
| District of Columbia | 6.00 days | 10 |
| Maine | 5.75 days | 8 |
| South Dakota | 5.58 days | 12 |
| Saskatchewan | 5.50 days | 2 |

> **Caution:** Several of these states have very low shipment volumes. The Newfoundland and Labrador result (6 shipments) and Saskatchewan (2 shipments) should not be interpreted with the same confidence as high-volume states.

### 11.2 States with Lowest Average Lead Times

| State/Province | Avg Lead Time | Shipments |
|----------------|---------------|-----------|
| Manitoba | 3.83 days | 12 |
| North Dakota | 3.86 days | 7 |
| Louisiana | 3.98 days | 42 |
| Nova Scotia | 4.00 days | 6 |
| Vermont | 4.00 days | 11 |

---

## 12. Ship Mode Analysis

| Ship Mode | Shipments | Avg Lead Time | Delay Rate | Total Sales |
|-----------|-----------|---------------|------------|-------------|
| Same Day | 547 (5.4%) | 0.63 days | 0.00% | $7,557.34 |
| First Class | 1,548 (15.2%) | 2.84 days | 0.06% | $21,316.97 |
| Second Class | 1,979 (19.4%) | 3.86 days | 14.55% | $28,057.42 |
| Standard Class | 6,120 (60.0%) | 5.63 days | 48.82% | $84,851.90 |

Standard Class accounts for 60% of all shipments and has the highest delay rate (48.82%). However, it also generates the highest total sales ($84,851.90), reflecting its role as the default/most economical shipping option.

Same Day and First Class shipping show near-zero delay rates at the 5-day threshold, indicating consistent fast processing.

---

## 13. Key Findings

1. **Order-to-ship lead times average 4.59 days** with a 32.15% delay rate at the 5-day threshold, indicating room for improvement in processing speed.

2. **Ship mode is the strongest predictor of lead time.** Same Day (0.63 days) is ~9× faster than Standard Class (5.63 days). Nearly all delays occur in Standard Class and Second Class shipments.

3. **Factory-level variation is modest.** The spread between the fastest (The Other Factory: 4.22 days) and slowest (Sugar Shack: 5.02 days) factories is only 0.80 days, though Sugar Shack's low volume (33 shipments) limits this comparison.

4. **Regional variation is minimal** (0.15-day spread across 4 regions), suggesting that the distribution network serves all regions with relatively consistent performance.

5. **7 high-volume routes were identified as bottlenecks**, having both above-average shipment counts and above-average lead times. These include routes serving Delaware, Minnesota, New Jersey, Tennessee, and Oregon.

6. **Remote/low-volume states show higher lead times.** Newfoundland and Labrador (8.50 days), District of Columbia (6.00 days), and Maine (5.75 days) have the highest averages, though their low volumes warrant cautious interpretation.

7. **Route efficiency scores range from 5.0 to 100.0**, with a strong negative correlation (-0.949) between lead time and efficiency score, confirming the score methodology's validity.

---

## 14. Operational Recommendations

Based on observed patterns:

1. **Review Standard Class processing:** With 48.82% of Standard Class shipments exceeding 5 days, operational review of this ship mode's workflow may reduce overall delay rates.

2. **Investigate bottleneck routes:** The 7 high-volume + high-lead-time routes (particularly those serving Tennessee, New Jersey, and Oregon from major factories) warrant process review.

3. **Consider volume-aware performance targets:** Routes with <10 shipments should be excluded from performance benchmarking to avoid misleading comparisons.

4. **Monitor Canadian route performance:** Cross-border routes to Newfoundland and Labrador show notably higher lead times (8.50 days), potentially reflecting border processing or logistical complexity.

5. **Evaluate ship mode mix:** Given that Standard Class represents 60% of shipments but 48.82% delay rate, shifting a portion of volume to Second Class could improve overall customer experience with moderate cost increase.

---

## 15. Limitations

1. **No delivery date available.** The analysis measures order-to-ship lead time only, not actual delivery time to customer. Transit time after shipment is unknown.

2. **Ship Date decoding.** The original Ship Date values required algorithmic decoding due to synthetic year offsets. While the decoded values produce expected ship-mode patterns, this introduces a methodological dependency.

3. **No explicit SLA.** The 5-day delay threshold is an analytical parameter, not a business-defined service level agreement.

4. **Low-volume routes.** Many routes have fewer than 10 shipments, limiting statistical reliability for those specific routes.

5. **No cost-per-shipment data.** While Sales and Gross Profit are available, actual shipping costs by mode are not, preventing true cost-efficiency analysis.

6. **Correlation ≠ causation.** Higher lead times on certain routes may reflect order complexity, seasonal patterns, or inventory availability rather than shipping process inefficiency.

7. **Factory assignment is derived**, not explicitly recorded in the source data. Mapping accuracy depends on the product-factory mapping specification.

---

## 16. Conclusion

This analysis provides a data-driven assessment of Nassau Candy Distributor's factory-to-customer shipping performance across 196 routes. The Analytical Route Efficiency Score enables comparative ranking while maintaining transparency in methodology. Key actionable insights include the disproportionate impact of Standard Class processing delays on overall performance, identification of 7 specific bottleneck routes for operational review, and the finding that regional geography is less predictive of lead time than ship mode selection.

The interactive Streamlit dashboard enables stakeholders to explore these findings dynamically, adjusting delay thresholds, filtering by factory/region/state, and drilling down to individual route performance.

---

## 17. Future Scope

1. **Incorporate actual delivery dates** to measure end-to-end customer experience.
2. **Add shipping cost data** to enable cost-efficiency optimization.
3. **Time-series forecasting** of lead time trends for proactive capacity planning.
4. **Customer-level segmentation** to understand which customer segments are most affected by delays.
5. **Seasonal decomposition** to identify peak-period bottlenecks.
6. **A/B analysis** of ship mode recommendations for specific route segments.
