# Jubilant FoodWorks Limited (NSE/BSE: JUBLFOOD)
### Enterprise Retail Intelligence Suite & Spatial Analytics Dashboard

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Dash%20%7C%20Plotly-E95420.svg)](https://dash.plotly.com/)
[![Engine](https://img.shields.io/badge/engine-Polars%20Fast%20Analytics-CD792C.svg)](https://pola.rs/)
[![Design System](https://img.shields.io/badge/design-Industrial%20Bento%20Grid-black.svg)]()

An executive-grade retail intelligence and enterprise performance analytics suite designed for **Jubilant FoodWorks Limited** (`NSE/BSE: JUBLFOOD`), India's largest food service company operating iconic brands:
* **Domino's Pizza India**
* **Popeyes**
* **Dunkin'**
* **Hong's Kitchen**
* **DP Eurasia** (Turkey, Azerbaijan, Georgia)

---

## 🍕 Key Modules & Features

1. **Executive "So What" Strategic Insights Panel**:
   - Automated natural-language synthesis of quarter-over-quarter and year-over-year operational dynamics.
   - Dynamic strategic recommendations and margin alerts.

2. **Financial & Margin Decomposition**:
   - Waterfall analysis of gross margin, employee expenses, occupancy costs, royalties, and EBITDA margins.
   - Consolidated vs. brand-level margin trajectories across 16 operating quarters.

3. **Store Dynamics & Network Expansion**:
   - Store openings, closures, net additions, and spatial network density.
   - SSSG (Same-Store Sales Growth) benchmarking across mature vs. ramping store cohorts.

4. **Channel & Digital Order Mix**:
   - Delivery vs. Dine-in vs. Takeaway volume and GMV contribution.
   - Digital app adoption, MAU engagement, and direct-to-consumer order penetration.

5. **Operational Fact Table (High-Speed AG-Grid)**:
   - Interactive, sortable, filterable enterprise data table with CSV export capabilities.

6. **Supply Chain & Cost Breakdown**:
   - Input commodity inflation sensitivities (dairy, flour, poultry, packaging).
   - Commissary network utilization and logistics cost ratios.

7. **Brand & Format Performance Benchmarks**:
   - Cross-brand comparative matrices analyzing revenue yield per store, ramp trajectories, and payback periods.

---

## ⚡ High-Performance Tech Stack

- **Query Engine**: [Polars](https://pola.rs/) (`pl.LazyFrame` / `pl.scan_csv`) for sub-millisecond aggregations and streaming data queries.
- **Frontend / Application**: [Plotly Dash](https://dash.plotly.com/) + [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/).
- **Data Grid**: [Dash AG Grid](https://dash.plotly.com/dash-ag-grid) with responsive column pinning, formatting, and numeric filtering.
- **Visual Aesthetic**: Industrial Bento Grid architecture with tailored glassmorphic cards and typography.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
python jubilant_foodworks_dashboard.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8050
```

---

## 📂 Project Architecture

```
JubilantFoodworks-Project/
├── jubilant_foodworks_dashboard.py   # Primary Dash enterprise application
├── jubilant_master.csv               # Historical & operational dataset across quarters
├── jubilant_geography.csv            # Regional & spatial store distribution data
├── requirements.txt                  # Python package dependencies
├── .gitignore                        # Git exclusion rules
├── .streamlit/
│   └── config.toml                   # Streamlit runtime configuration
└── assets/
    ├── custom_style.css              # Industrial bento grid design tokens & CSS
    ├── jubilant_logo.svg             # Vector brandmark
    ├── jubilant_logo_dark.svg        # Dark theme brand asset
    └── jubilant_logo_light.svg       # Light theme brand asset
```

---

## 📄 License
Internal Enterprise Analytics — Jubilant FoodWorks Limited.
