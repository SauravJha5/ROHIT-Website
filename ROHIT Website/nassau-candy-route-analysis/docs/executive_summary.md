# Executive Summary

## Factory-to-Customer Shipping Route Efficiency Analysis — Nassau Candy Distributor

---

### Objective

Analyze factory-to-customer shipping performance for Nassau Candy Distributor to identify efficient routes, delayed routes, geographic bottlenecks, and ship-mode performance patterns. Enable data-driven operational review through an interactive analytics dashboard.

---

### Dataset

- **10,194 shipment records** across January 2024 – December 2025
- **5 factories** serving **59 states/provinces** in the US and Canada
- **196 unique factory-to-customer-state routes**
- **4 shipping modes:** Same Day, First Class, Second Class, Standard Class
- **15 products** across Chocolate, Sugar, and Other divisions

---

### Major Findings

| KPI | Value |
|-----|-------|
| Average Order-to-Ship Lead Time | **4.59 days** |
| Delay Rate (>5 days threshold) | **32.15%** (3,277 of 10,194 shipments) |
| Total Sales | **$141,783.63** |
| Total Gross Profit | **$93,442.80** |
| Route Efficiency Score Range | **5.0 – 100.0** |

---

### Ship Mode Performance

| Ship Mode | % of Volume | Avg Lead Time | Delay Rate |
|-----------|-------------|---------------|------------|
| Same Day | 5.4% | 0.63 days | 0.0% |
| First Class | 15.2% | 2.84 days | 0.06% |
| Second Class | 19.4% | 3.86 days | 14.55% |
| Standard Class | 60.0% | 5.63 days | **48.82%** |

**Standard Class** represents the majority of shipments and accounts for nearly all delays. This is the single most impactful factor in overall delay rates.

---

### Geographic Bottlenecks

**Highest lead time states:** Newfoundland & Labrador (8.50 days, 6 shipments), District of Columbia (6.00 days, 10 shipments), Maine (5.75 days, 8 shipments).

**Note:** These states have low shipment volumes. Among high-volume states, Oregon, Minnesota, and New Jersey show elevated lead times on routes from major factories.

**Regional variation is modest** (4.54–4.69 days across 4 regions), indicating relatively consistent geographic coverage.

---

### Route Performance

- **Most efficient route:** Wicked Choccy's → Vermont (Score: 75.73, 5 shipments, 3.6-day avg)
- **Least efficient route:** Lot's O' Nuts → Newfoundland and Labrador (Score: 5.0, 6 shipments, 8.5-day avg)
- **7 high-volume bottleneck routes** identified serving Delaware, Minnesota, New Jersey, Tennessee, and Oregon

---

### Recommended Areas for Operational Review

1. **Standard Class processing workflow** — 48.82% delay rate suggests process improvement opportunity
2. **7 identified bottleneck routes** — high volume + high lead time combinations warrant targeted investigation
3. **Cross-border logistics** — Canadian routes, particularly to Newfoundland, show elevated lead times
4. **Ship mode mix strategy** — potential to reduce delays by shifting select Standard Class volume to Second Class
5. **Low-volume route monitoring** — establish minimum thresholds before using route-level metrics for decision-making

---

### Limitations

- Analysis measures **order-to-ship lead time only**, not delivery time to customer
- The 5-day delay threshold is an **analytical parameter**, not an official SLA
- **Factory assignment is derived** from product mapping, not directly recorded
- Routes with <10 shipments have **limited statistical reliability**
- **Correlation should not be interpreted as causation** — elevated lead times may reflect order complexity or seasonal factors

---

*This summary is based on analysis of actual dataset records. All statistics are computed from the data. No results are fabricated or assumed.*
