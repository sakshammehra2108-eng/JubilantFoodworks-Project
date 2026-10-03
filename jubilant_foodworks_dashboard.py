"""
===============================================================================
 JUBILANT FOODWORKS LIMITED (NSE/BSE: JUBLFOOD)
 BESPOKE ENTERPRISE RETAIL INTELLIGENCE SUITE ("SPATIAL INTELLIGENCE SUITE")
 
 Visual Design: Nothing OS Industrial Aesthetic x Apple SF Spatial Hybrid
 High-Performance Core: Polars (pl.LazyFrame / pl.scan_csv) + Dash + AG-Grid
===============================================================================
"""

from __future__ import annotations

import os
import numpy as np
import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

# -----------------------------------------------------------------------------
# 0. GLOBAL BRAND ARCHITECTURE & DESIGN CONSTANTS
# -----------------------------------------------------------------------------
COMPANY = "Jubilant FoodWorks Limited"
TICKER = "NSE/BSE: JUBLFOOD"
TOTAL = "Total (Consolidated)"

BRANDS = ["Domino's India", "Popeyes", "Dunkin'", "Hong's Kitchen", "DP Eurasia"]
INDIA_BRANDS = ["Domino's India", "Popeyes", "Dunkin'", "Hong's Kitchen"]
INTL_BRANDS = ["DP Eurasia"]

# High-contrast brand palette
BRAND_COLORS = {
    "Domino's India": "#0B648F",
    "Popeyes": "#F26722",
    "Dunkin'": "#E11383",
    "Hong's Kitchen": "#C9A227",
    "DP Eurasia": "#1F2A44",
    TOTAL: "#38BDF8",
}

N_Q = 16
HIST_Q = 4
KP_T = [0, 4, 8, 12, 15]

CSV_DATA_PATH = os.path.join(os.path.dirname(__file__), "jubilant_master.csv")
GEO_DATA_PATH = os.path.join(os.path.dirname(__file__), "jubilant_geography.csv")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# -----------------------------------------------------------------------------
# 1. POLARS HIGH-PERFORMANCE DATA INITIALIZATION & QUERY LAYER
# -----------------------------------------------------------------------------
BRAND_CFG = {
    "Domino's India": dict(
        revenue=[1015, 1290, 1345, 1405, 1395, 1450, 1490, 1485,
                 1480, 1500, 1575, 1530, 1555, 1550, 1640, 1605],
        start_stores=1370,
        gross_openings=[34, 42, 52, 48, 62, 51, 46, 52, 51, 58, 68, 63, 52, 68, 66, 70],
        closures=[6, 7, 7, 6, 7, 6, 6, 7, 6, 8, 8, 8, 7, 8, 8, 8],
        sssg=[24.0, 7.5, 5.2, 0.8, -2.8, -3.9, -1.5, -2.7, -2.9, -3.7, -1.2, 0.6],
        cogs=[25.8, 26.8, 25.6, 24.8, 24.5],
        staff=[13.0, 13.2, 13.8, 14.2, 14.4],
        occupancy=[11.5, 11.2, 11.8, 12.0, 12.2],
        royalty=[3.2, 3.2, 3.3, 3.3, 3.3],
        other=[23.3, 22.6, 23.7, 24.7, 24.9],
    ),
    "Popeyes": dict(
        revenue=[14, 17, 20, 23, 28, 34, 38, 42, 44, 47, 51, 48, 54, 58, 66, 67],
        start_stores=14,
        gross_openings=[4, 4, 5, 5, 6, 7, 7, 8, 7, 7, 7, 7, 7, 7, 7, 7],
        closures=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        sssg=[18.0, 12.0, 9.5, 6.0, 4.0, 1.5, 3.5, 2.0, 5.0, 8.5, 9.0, 7.0],
        cogs=[32.0, 32.5, 31.5, 30.5, 30.0],
        staff=[21.0, 20.5, 19.5, 19.0, 18.8],
        occupancy=[17.5, 16.5, 15.5, 15.0, 14.7],
        royalty=[4.0, 4.0, 4.0, 4.0, 4.0],
        other=[36.5, 34.5, 32.5, 31.0, 30.3],
    ),
    "Dunkin'": dict(
        revenue=[9, 11, 12, 12, 14, 16, 17, 17, 22, 24, 25, 24, 24, 25, 28, 28],
        start_stores=22,
        gross_openings=[1, 2, 2, 3, 4, 3, 4, 3, 4, 4, 3, 3, 3, 4, 4, 3],
        closures=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        sssg=[10.0, 7.0, 5.0, 3.0, 2.0, -1.0, 1.0, -2.0, -3.0, -1.0, 2.0, 1.5],
        cogs=[34.0, 35.0, 34.5, 33.5, 33.0],
        staff=[24.0, 23.0, 22.0, 21.5, 21.0],
        occupancy=[18.5, 18.0, 17.5, 17.0, 16.8],
        royalty=[4.0, 4.0, 4.0, 4.0, 4.0],
        other=[39.5, 38.0, 36.5, 35.0, 34.2],
    ),
    "Hong's Kitchen": dict(
        revenue=[2, 2.5, 3, 3.5, 4, 5, 6, 7, 7, 7.5, 7.5, 8, 8, 8, 8.5, 8.5],
        start_stores=3,
        gross_openings=[2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
        closures=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        sssg=[12.0, 6.0, 3.0, 1.0, -2.0, -4.0, -1.0, -3.0, -2.0, 0.0, 1.0, 2.0],
        cogs=[34.0, 33.5, 33.0, 32.5, 32.0],
        staff=[28.0, 27.0, 26.0, 25.0, 24.5],
        occupancy=[21.0, 20.0, 19.0, 18.0, 17.5],
        royalty=[3.5, 3.5, 3.5, 3.5, 3.5],
        other=[45.5, 42.5, 39.5, 38.5, 37.0],
    ),
    "DP Eurasia": dict(
        revenue=[195, 225, 235, 245, 255, 275, 285, 290,
                 290, 300, 320, 308, 325, 340, 375, 371],
        start_stores=540,
        gross_openings=[13, 15, 18, 17, 13, 16, 18, 18, 13, 16, 17, 19, 13, 16, 17, 19],
        closures=[3, 3, 4, 3, 3, 4, 4, 4, 3, 4, 4, 4, 3, 4, 4, 4],
        sssg=[18.0, 22.0, 24.0, 21.0, 19.0, 16.5, 14.0, 12.5, 10.5, 9.0, 8.0, 7.5],
        cogs=[29.0, 30.5, 29.5, 28.8, 28.5],
        staff=[15.0, 15.5, 16.2, 16.8, 17.0],
        occupancy=[12.0, 11.8, 12.0, 12.2, 12.4],
        royalty=[3.0, 3.0, 3.0, 3.0, 3.0],
        other=[23.5, 22.7, 23.0, 23.6, 23.6],
    ),
}

def ensure_master_data():
    if not os.path.exists(CSV_DATA_PATH):
        rng = np.random.default_rng(2025)
        t = np.arange(N_Q)
        records = []
        for brand, c in BRAND_CFG.items():
            rev = np.array(c["revenue"], dtype=float)
            cogs_p = np.interp(t, KP_T, c["cogs"]) + rng.normal(0, 0.1, N_Q)
            staff_p = np.interp(t, KP_T, c["staff"]) + rng.normal(0, 0.08, N_Q)
            occ_p = np.interp(t, KP_T, c["occupancy"]) + rng.normal(0, 0.06, N_Q)
            roy_p = np.interp(t, KP_T, c["royalty"])
            other_p = np.interp(t, KP_T, c["other"]) + rng.normal(0, 0.1, N_Q)
            net_adds = np.array(c["gross_openings"]) - np.array(c["closures"])
            stores = c["start_stores"] + np.cumsum(net_adds)
            sssg = np.r_[np.full(HIST_Q, np.nan), c["sssg"]]

            for i in range(N_Q):
                r = rev[i]
                cogs_a = r * cogs_p[i] / 100.0
                staff_a = r * staff_p[i] / 100.0
                occ_a = r * occ_p[i] / 100.0
                roy_a = r * roy_p[i] / 100.0
                oth_a = r * other_p[i] / 100.0
                ebitda_a = r - (cogs_a + staff_a + occ_a + roy_a + oth_a)
                base_mau = 7.5 + (i * 0.5) if brand == "Domino's India" else (0.4 + i * 0.05)

                records.append({
                    "t": int(t[i]),
                    "brand": brand,
                    "revenue": float(r),
                    "gross_openings": int(c["gross_openings"][i]),
                    "closures": int(c["closures"][i]),
                    "net_adds": int(net_adds[i]),
                    "stores": int(stores[i]),
                    "cogs_amt": float(cogs_a),
                    "staff_amt": float(staff_a),
                    "occupancy_amt": float(occ_a),
                    "royalty_amt": float(roy_a),
                    "other_opex_amt": float(oth_a),
                    "ebitda_amt": float(ebitda_a),
                    "sssg": float(sssg[i]) if not np.isnan(sssg[i]) else None,
                    "digital_maus": round(base_mau, 2),
                    "app_delivery_share": round(74.0 + (i * 0.9), 1),
                    "format_flagship_pct": 42.0,
                    "format_delivery_pct": 32.0,
                    "format_foodcourt_pct": 16.0,
                    "format_drivethru_pct": 10.0,
                    "channel_app_delivery_pct": round(46.0 + (i * 0.3), 1),
                    "channel_aggregators_pct": round(28.0 - (i * 0.1), 1),
                    "channel_dinein_pct": round(16.0 - (i * 0.15), 1),
                    "channel_takeaway_pct": round(10.0 - (i * 0.05), 1),
                })
        raw_df = pl.DataFrame(records)
        total_df = (
            raw_df.group_by("t")
            .agg([
                pl.col("revenue").sum(),
                pl.col("gross_openings").sum(),
                pl.col("closures").sum(),
                pl.col("net_adds").sum(),
                pl.col("stores").sum(),
                pl.col("cogs_amt").sum(),
                pl.col("staff_amt").sum(),
                pl.col("occupancy_amt").sum(),
                pl.col("royalty_amt").sum(),
                pl.col("other_opex_amt").sum(),
                pl.col("ebitda_amt").sum(),
                pl.col("digital_maus").sum(),
                pl.col("app_delivery_share").mean(),
                pl.col("format_flagship_pct").mean(),
                pl.col("format_delivery_pct").mean(),
                pl.col("format_foodcourt_pct").mean(),
                pl.col("format_drivethru_pct").mean(),
                pl.col("channel_app_delivery_pct").mean(),
                pl.col("channel_aggregators_pct").mean(),
                pl.col("channel_dinein_pct").mean(),
                pl.col("channel_takeaway_pct").mean(),
            ])
            .with_columns(pl.lit(TOTAL).alias("brand"))
        )
        weighted_sssg = (
            raw_df.filter(pl.col("sssg").is_not_null())
            .with_columns((pl.col("sssg") * pl.col("revenue")).alias("weighted"))
            .group_by("t")
            .agg((pl.col("weighted").sum() / pl.col("revenue").sum()).alias("sssg"))
        )
        total_df = total_df.join(weighted_sssg, on="t", how="left")
        combined_df = pl.concat([raw_df, total_df], how="diagonal")

        fy_s = 2022 + (combined_df["t"] // 4)
        q_s = (combined_df["t"] % 4) + 1
        quarter_labels = [f"Q{q_val} FY{fy_val % 100}" for q_val, fy_val in zip(q_s, fy_s)]

        combined_df = (
            combined_df.with_columns([
                pl.Series("quarter", quarter_labels),
                pl.Series("fy", [f"FY{fy_val % 100}" for fy_val in fy_s]),
                (pl.col("cogs_amt") / pl.col("revenue") * 100.0).alias("cogs_pct"),
                (pl.col("staff_amt") / pl.col("revenue") * 100.0).alias("staff_pct"),
                (pl.col("occupancy_amt") / pl.col("revenue") * 100.0).alias("occupancy_pct"),
                (pl.col("royalty_amt") / pl.col("revenue") * 100.0).alias("royalty_pct"),
                (pl.col("other_opex_amt") / pl.col("revenue") * 100.0).alias("other_opex_pct"),
                (100.0 - (pl.col("cogs_amt") / pl.col("revenue") * 100.0)).alias("gross_margin"),
                (pl.col("ebitda_amt") / pl.col("revenue") * 100.0).alias("ebitda_pct"),
                (pl.col("revenue") * 100.0 / pl.col("stores")).alias("sales_per_store_lakhs"),
                ((pl.col("revenue") * 10000000.0) / (pl.col("stores") * 90.0)).alias("ads_inr"),
            ])
            .sort(["brand", "t"])
            .with_columns([
                ((pl.col("revenue") / pl.col("revenue").shift(4).over("brand") - 1.0) * 100.0).alias("yoy"),
                ((pl.col("revenue") / pl.col("revenue").shift(1).over("brand") - 1.0) * 100.0).alias("qoq"),
            ])
        )
        combined_df.write_csv(CSV_DATA_PATH)

    if not os.path.exists(GEO_DATA_PATH):
        geo_records = [
            {"territory": "Delhi NCR", "region": "North India", "lat": 28.6139, "lon": 77.2090, "stores": 465, "revenue_cr": 420.5, "brand_focus": "Domino's India"},
            {"territory": "Mumbai MMR", "region": "West India", "lat": 19.0760, "lon": 72.8777, "stores": 395, "revenue_cr": 380.2, "brand_focus": "Domino's India"},
            {"territory": "Bengaluru Urban", "region": "South India", "lat": 12.9716, "lon": 77.5946, "stores": 330, "revenue_cr": 315.8, "brand_focus": "Domino's India"},
            {"territory": "Hyderabad Cyberabad", "region": "South India", "lat": 17.3850, "lon": 78.4867, "stores": 240, "revenue_cr": 225.4, "brand_focus": "Popeyes"},
            {"territory": "Kolkata Greater", "region": "East India", "lat": 22.5726, "lon": 88.3639, "stores": 185, "revenue_cr": 165.2, "brand_focus": "Hong's Kitchen"},
            {"territory": "Chennai Central", "region": "South India", "lat": 13.0827, "lon": 80.2707, "stores": 190, "revenue_cr": 172.6, "brand_focus": "Domino's India"},
            {"territory": "Pune Metropolitan", "region": "West India", "lat": 18.5204, "lon": 73.8567, "stores": 160, "revenue_cr": 145.8, "brand_focus": "Dunkin'"},
            {"territory": "Ahmedabad & Gandhinagar", "region": "West India", "lat": 23.0225, "lon": 72.5714, "stores": 145, "revenue_cr": 130.4, "brand_focus": "Domino's India"},
            {"territory": "Chandigarh Tricity", "region": "North India", "lat": 30.7333, "lon": 76.7794, "stores": 95, "revenue_cr": 92.5, "brand_focus": "Popeyes"},
            {"territory": "Jaipur Metropolitan", "region": "North India", "lat": 26.9124, "lon": 75.7873, "stores": 85, "revenue_cr": 78.2, "brand_focus": "Domino's India"},
            {"territory": "Lucknow Central", "region": "North India", "lat": 26.8467, "lon": 80.9462, "stores": 80, "revenue_cr": 72.8, "brand_focus": "Domino's India"},
            {"territory": "Kochi & Central Kerala", "region": "South India", "lat": 9.9312, "lon": 76.2673, "stores": 65, "revenue_cr": 58.4, "brand_focus": "Domino's India"},
            {"territory": "Istanbul Metropolitan", "region": "Eurasia (Turkey)", "lat": 41.0082, "lon": 28.9784, "stores": 380, "revenue_cr": 210.6, "brand_focus": "DP Eurasia"},
            {"territory": "Ankara Capital", "region": "Eurasia (Turkey)", "lat": 39.9334, "lon": 32.8597, "stores": 140, "revenue_cr": 76.5, "brand_focus": "DP Eurasia"},
            {"territory": "Izmir Aegean", "region": "Eurasia (Turkey)", "lat": 38.4237, "lon": 27.1428, "stores": 95, "revenue_cr": 52.4, "brand_focus": "DP Eurasia"},
            {"territory": "Baku Urban", "region": "Eurasia (Azerbaijan)", "lat": 40.4093, "lon": 49.8671, "stores": 55, "revenue_cr": 28.6, "brand_focus": "DP Eurasia"},
            {"territory": "Tbilisi Metro", "region": "Eurasia (Georgia)", "lat": 41.7151, "lon": 44.8271, "stores": 35, "revenue_cr": 18.2, "brand_focus": "DP Eurasia"},
        ]
        pl.DataFrame(geo_records).write_csv(GEO_DATA_PATH)

ensure_master_data()

METADATA_QUARTERS = [f"Q{(i % 4) + 1} FY{(2022 + i // 4) % 100}" for i in range(N_Q)]

# Polars Multi-Threaded Lazy Execution Engine
def query_brand_data(brand_name: str, t_from: int, t_to: int) -> pd.DataFrame:
    lf = pl.scan_csv(CSV_DATA_PATH)
    return (
        lf.filter(
            (pl.col("brand") == brand_name) &
            (pl.col("t") >= t_from) &
            (pl.col("t") <= t_to)
        )
        .sort("t")
        .collect()
        .to_pandas()
    )


def query_full_history(brand_name: str) -> pd.DataFrame:
    lf = pl.scan_csv(CSV_DATA_PATH)
    return lf.filter(pl.col("brand") == brand_name).sort("t").collect().to_pandas().set_index("t")


def query_all_brands(t_from: int, t_to: int) -> pd.DataFrame:
    lf = pl.scan_csv(CSV_DATA_PATH)
    return lf.filter(
        (pl.col("brand").is_in(BRANDS)) &
        (pl.col("t") >= t_from) &
        (pl.col("t") <= t_to)
    ).sort(["t", "brand"]).collect().to_pandas()


def query_geo_data() -> pd.DataFrame:
    return pl.scan_csv(GEO_DATA_PATH).collect().to_pandas()


def format_indian_num(num: float, decimals: int = 0) -> str:
    """Format numbers cleanly using standard Indian numbering system (e.g. 2,07,950)."""
    if pd.isna(num):
        return "N/A"
    is_neg = num < 0
    num = abs(num)
    if decimals > 0:
        base = f"{num:.{decimals}f}"
        int_part, dec_part = base.split(".")
    else:
        int_part = str(int(round(num)))
        dec_part = ""
    
    if len(int_part) <= 3:
        formatted = int_part
    else:
        last_three = int_part[-3:]
        remaining = int_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last_three
    
    if dec_part:
        formatted += "." + dec_part
    return ("-" if is_neg else "") + formatted

# Currency conversion engine
def convert_val(val: float, unit_mode: str) -> tuple[float, str]:
    if pd.isna(val):
        return 0.0, "N/A"
    if unit_mode in ["USD $ M", "$ USD", "$ Mn", "$ M"]:
        v = val * 0.1176
        return v, f"${v:,.1f}" if abs(v) < 100 else f"${v:,.0f}"
    elif unit_mode in ["INR L", "₹ Lakh"]:
        v = val * 100.0
        dec = 1 if abs(v % 1) > 1e-3 else 0
        return v, f"₹{format_indian_num(v, dec)}"
    dec = 1 if abs(val % 1) > 1e-3 else 0
    return val, f"₹{format_indian_num(val, dec)}"


def convert_ads(val_inr: float, unit_mode: str) -> str:
    if pd.isna(val_inr):
        return "N/A"
    if unit_mode in ["USD $ M", "$ USD", "$ Mn", "$ M"]:
        return f"${val_inr / 85.0:,.0f}"
    return f"₹{format_indian_num(val_inr)}"



# -----------------------------------------------------------------------------
# 2B. ADVANCED POLARS ANALYTICAL PIPELINES & EXECUTIVE INSIGHT GENERATOR
# -----------------------------------------------------------------------------
def compute_store_cohort_elasticity(brand_name: str, t_from: int, t_to: int) -> pd.DataFrame:
    """Polars quantitative pipeline calculating SSSG vs Net Store Growth Elasticity Ratio."""
    lf = pl.scan_csv(CSV_DATA_PATH)
    return (
        lf.filter(
            (pl.col("brand") == brand_name) &
            (pl.col("t") >= t_from) &
            (pl.col("t") <= t_to)
        )
        .sort("t")
        .with_columns([
            ((pl.col("net_adds") / pl.max_horizontal(pl.col("stores") - pl.col("net_adds"), pl.lit(1.0))) * 100.0).alias("net_store_growth_pct"),
        ])
        .with_columns([
            (pl.col("sssg") / pl.when(pl.col("net_store_growth_pct") == 0).then(0.001).otherwise(pl.col("net_store_growth_pct"))).alias("elasticity_ratio"),
            (pl.col("stores") * 0.78).round(0).alias("mature_cohort_stores"),
            (pl.col("stores") * 0.14).round(0).alias("ramping_cohort_stores"),
            (pl.col("stores") * 0.08).round(0).alias("new_formats_stores"),
        ])
        .collect()
        .to_pandas()
    )


def compute_multibrand_benchmarking(quarter_name: str) -> pd.DataFrame:
    """Polars multi-brand cross-sectional benchmarking pipeline."""
    lf = pl.scan_csv(CSV_DATA_PATH)
    return (
        lf.filter((pl.col("quarter") == quarter_name) & (pl.col("brand") != TOTAL))
        .select(["brand", "revenue", "gross_margin", "ebitda_pct", "ads_inr", "stores", "sssg"])
        .collect()
        .to_pandas()
    )


def generate_executive_insights(selected_brand: str, cur: pd.Series, prev_y: pd.Series, q_end: str, is_dark: bool):
    """Dynamic executive 'So What' insight generator driven by underlying operating signals."""
    sssg_val = cur["sssg"] if not pd.isna(cur["sssg"]) else 0.0
    net_adds_val = int(cur["net_adds"]) if not pd.isna(cur["net_adds"]) else 0
    stores_val = int(cur["stores"]) if not pd.isna(cur["stores"]) else 0
    gm_val = cur["gross_margin"] if not pd.isna(cur["gross_margin"]) else 75.0
    ebitda_val = cur["ebitda_pct"] if not pd.isna(cur["ebitda_pct"]) else 18.0
    yoy_val = cur["yoy"] if not pd.isna(cur["yoy"]) else 0.0
    rev_val = cur["revenue"] if not pd.isna(cur["revenue"]) else 0.0

    if selected_brand == "Popeyes":
        finding = f"Popeyes sales grew by {yoy_val:+.1f}% compared to last year across {stores_val} outlets, turning profitable at a {ebitda_val:.1f}% EBITDA margin in {q_end}."
        sowhat = "Fried chicken is catching on fast in Indian metros with strong customer demand, and the centralized kitchen network is now large enough to operate profitably."
        rec = "Accelerate opening new drive-thrus and metro stations in Bengaluru and Delhi-NCR, while locking in long-term poultry supply contracts to protect margins."
    elif selected_brand == "Dunkin'":
        finding = f"Coffee and beverages now make up 42% of sales, with gross margins at {gm_val:.1f}% across {stores_val} remodeled coffee stores in {q_end}."
        sowhat = "Focusing on younger coffee drinkers is lifting afternoon sales, but high street shop rents are still weighing down overall store profits."
        rec = "Stop opening expensive standalone street stores. Focus entirely on low-cost express kiosks inside busy Domino's outlets to share rent."
    elif selected_brand == "Hong's Kitchen":
        finding = f"Hong's Kitchen grew sales by {yoy_val:+.1f}% compared to last year across {stores_val} outlets, with customer repeat rates holding steady above 38%."
        sowhat = "Chinese food is India's second most popular eating-out choice with very few organized national chains, and individual store profits are proving solid."
        rec = "Expand into Mumbai and Pune by using Domino's existing central dough, sauce, and cold-chain delivery network."
    elif selected_brand == "DP Eurasia":
        finding = f"DP Eurasia operates {stores_val:,} stores across Turkey and Eurasia, bringing in ₹{format_indian_num(rev_val, 0)} Cr in quarterly revenue in {q_end}."
        sowhat = f"Regular menu price adjustments and adding coffee (COFFY) keep sales growing (+{sssg_val:.1f}%) and protect a 15%+ profit margin despite currency swings."
        rec = "Bring DP Eurasia's low-cost delivery routing tech over to Domino's India to cut local delivery costs by 8% to 12% per order."
    else:
        finding = f"Existing stores grew sales by {sssg_val:+.1f}% (SSSG), while {net_adds_val} new outlets were added in {q_end} to reach {stores_val:,} total locations."
        sowhat = "Opening new stores close to existing ones is expanding overall reach, but it is splitting local delivery orders and slightly eating into sales at older outlets."
        rec = "Pause adding Domino's outlets in saturated areas. Direct new store capital to Popeyes and Hong's Kitchen, and shift orders to the Domino's app to cut aggregator commissions."

    finding_badge_bg = "rgba(0, 240, 255, 0.15)" if is_dark else "rgba(2, 132, 199, 0.12)"
    finding_badge_color = "#00F0FF" if is_dark else "#0284C7"
    sowhat_badge_bg = "rgba(245, 158, 11, 0.15)" if is_dark else "rgba(217, 119, 6, 0.12)"
    sowhat_badge_color = "#F59E0B" if is_dark else "#D97706"
    rec_badge_bg = "rgba(16, 185, 129, 0.15)" if is_dark else "rgba(5, 150, 105, 0.12)"
    rec_badge_color = "#10B981" if is_dark else "#059669"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    return dbc.Row(
        className="g-3 align-items-stretch",
        children=[
            dbc.Col(
                lg=4, md=12,
                children=[
                    html.Div(
                        className="insight-block insight-finding p-3 rounded-3 h-100",
                        children=[
                            html.Div(
                                className="saint-card-header insight-card-header",
                                children=[
                                    html.Span("BARE FINDING", className="badge saint-badge insight-badge", style={"backgroundColor": finding_badge_bg, "color": finding_badge_color}),
                                ]
                            ),
                            html.P(finding, className="mb-0 small fw-semibold", style={"color": text_color, "lineHeight": "1.5"}),
                        ]
                    )
                ]
            ),
            dbc.Col(
                lg=4, md=12,
                children=[
                    html.Div(
                        className="insight-block insight-sowhat p-3 rounded-3 h-100",
                        children=[
                            html.Div(
                                className="saint-card-header insight-card-header",
                                children=[
                                    html.Span("SO WHAT", className="badge saint-badge insight-badge", style={"backgroundColor": sowhat_badge_bg, "color": sowhat_badge_color}),
                                ]
                            ),
                            html.P(sowhat, className="mb-0 small fw-semibold", style={"color": text_color, "lineHeight": "1.5"}),
                        ]
                    )
                ]
            ),
            dbc.Col(
                lg=4, md=12,
                children=[
                    html.Div(
                        className="insight-block insight-rec p-3 rounded-3 h-100",
                        children=[
                            html.Div(
                                className="saint-card-header insight-card-header",
                                children=[
                                    html.Span("STRATEGIC RECOMMENDATION", className="badge saint-badge insight-badge", style={"backgroundColor": rec_badge_bg, "color": rec_badge_color}),
                                ]
                            ),
                            html.P(rec, className="mb-0 small fw-semibold", style={"color": text_color, "lineHeight": "1.5"}),
                        ]
                    )
                ]
            ),
        ]
    )

# -----------------------------------------------------------------------------
# 2. PLOTLY CHART STYLING: NOTHING OS SPATIAL AESTHETIC (NO EMBEDDED TITLES)
# -----------------------------------------------------------------------------
def apply_spatial_layout(fig: go.Figure, theme: str = "dark", height: int = 370) -> go.Figure:
    """Consistent, publication-grade dark styling matching Nothing OS aesthetic without embedded titles."""
    is_dark = (theme == "dark")
    text_color = "#00F0FF" if is_dark else "#0F172A"
    primary_text = "#F8FAFC" if is_dark else "#0F172A"
    muted_color = "#94A3B8" if is_dark else "#64748B"
    grid_color = "rgba(255, 255, 255, 0.05)" if is_dark else "rgba(0, 0, 0, 0.05)"
    line_color = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.08)"

    fig.update_layout(
        title=None,
        font=dict(color=primary_text, family="'Inter', sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=muted_color, family="'Inter', sans-serif"),
        ),
        margin=dict(l=35, r=35, t=40, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0A0D14" if is_dark else "#FFFFFF",
            bordercolor="rgba(0, 240, 255, 0.4)" if is_dark else "rgba(0, 0, 0, 0.12)",
            font_size=11,
            font_color=primary_text,
            font_family="'JetBrains Mono', monospace",
        ),
        xaxis=dict(
            showgrid=False,
            linecolor=line_color,
            linewidth=1,
            tickfont=dict(size=10, color=muted_color, family="'Inter', sans-serif"),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            linecolor=line_color,
            linewidth=1,
            tickfont=dict(size=10, color=muted_color, family="'Inter', sans-serif"),
            zerolinecolor=line_color,
        ),
    )
    return fig


# -----------------------------------------------------------------------------
# 3. DASH APPLICATION & DIRECT INLINE CSS IN INDEX_STRING
# -----------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    assets_folder=ASSETS_DIR,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
)
app.title = "Jubilant FoodWorks | Spatial Intelligence Suite"

# Backward compatibility shim
app.run_server = app.run

# Direct raw CSS string without f-string formatting placeholders
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box !important;
            }
            body { 
                background-color: var(--bg-canvas, #030407) !important; 
                background-image: radial-gradient(var(--dot-color, rgba(255, 255, 255, 0.08)) 1px, transparent 1px) !important;
                background-size: 24px 24px !important;
                font-family: 'Inter', sans-serif !important; 
                color: var(--text-primary, #F8FAFC) !important; 
                margin: 0 !important;
                padding: 0 !important;
                -webkit-font-smoothing: antialiased !important;
            }
            .card { 
                background: var(--bg-card, #0A0D14) !important; 
                border: 1px solid var(--border-subtle, #1E2638) !important; 
                border-radius: 12px !important; 
            }
            .form-select, select, option { 
                color: #0F172A !important;
                background-color: #FFFFFF !important; 
                font-weight: 600 !important;
                opacity: 1 !important;
                font-family: 'Inter', sans-serif !important;
            }
            [data-theme="dark"] .form-select, 
            [data-theme="dark"] select {
                color: #F8FAFC !important;
                background-color: rgba(18, 24, 38, 0.9) !important; 
                border: 1px solid rgba(255, 255, 255, 0.15) !important; 
            }
            [data-theme="dark"] option {
                color: #F8FAFC !important;
                background-color: #0A0D14 !important; 
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


# -----------------------------------------------------------------------------
# 4. DASHBOARD LAYOUT DEFINITION (BENTO GRID DESIGN)
# -----------------------------------------------------------------------------
app.layout = html.Div(
    id="theme-wrapper",
    **{"data-theme": "dark"},
    children=[
        # Client-side state stores
        dcc.Store(id="theme-store", data="dark"),
        dcc.Store(id="horizon-range-store", data=[HIST_Q, N_Q - 1]),

        dbc.Container(
            id="app-container",
            fluid=True,
            className="py-3 px-4",
            style={"paddingLeft": "28px", "paddingRight": "28px", "boxSizing": "border-box"},
            children=[
                # A. Executive Header Bar (Typographic Textmark with Nothing Red Live Dot)
                html.Div(
                    id="header-card",
                    className="bento-card header-tile header-container mb-3 py-3",
                    children=[
                        dbc.Row(
                            align="center",
                            className="g-3",
                            children=[
                                # Left: Brand Logo & Live Status
                                dbc.Col(
                                    lg=4, md=5, sm=12,
                                    children=[
                                        html.Div(
                                            style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "10px"},
                                            children=[
                                                html.Img(
                                                    src="/assets/jubilant_logo_dark.svg",
                                                    className="brand-logo-dark",
                                                    style={"height": "40px", "width": "auto", "objectFit": "contain"},
                                                    alt="Jubilant FoodWorks Logo",
                                                ),
                                                html.Img(
                                                    src="/assets/jubilant_logo_light.svg",
                                                    className="brand-logo-light",
                                                    style={"height": "40px", "width": "auto", "objectFit": "contain"},
                                                    alt="Jubilant FoodWorks Logo",
                                                ),
                                                html.Div(
                                                    id="ticker-pill-terminal",
                                                    className="ticker-terminal-pill ms-2",
                                                    children=[
                                                        html.Span(className="terminal-red-dot"),
                                                        html.Span(TICKER, className="ticker-code-text"),
                                                    ]
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                                # Center: Concept Selector (Custom Glass React-Select Dropdown)
                                dbc.Col(
                                    lg=3, md=4, sm=12,
                                    children=[
                                        dbc.Select(
                                            id="brand-dropdown",
                                            options=[{"label": b, "value": b} for b in [TOTAL] + BRANDS],
                                            value=TOTAL,
                                            className="form-select spatial-dropdown",
                                        )
                                    ]
                                ),
                                # Right Controls: Currency Scale & Theme Toggle
                                dbc.Col(
                                    lg=5, md=3, sm=12,
                                    className="d-flex justify-content-lg-end align-items-center gap-3 flex-wrap",
                                    children=[
                                        # Currency Segmented Capsule
                                        html.Div(
                                            className="segmented-capsule segmented-pill-container",
                                            children=[
                                                dbc.RadioItems(
                                                    id="currency-toggle",
                                                    options=[
                                                        {"label": "₹ Cr", "value": "₹ Cr"},
                                                        {"label": "₹ Lakh", "value": "₹ Lakh"},
                                                        {"label": "$ Mn", "value": "$ Mn"},
                                                    ],
                                                    value="₹ Cr",
                                                    inline=True,
                                                    className="segmented-radio-items",
                                                )
                                            ]
                                        ),
                                        # Theme Switcher Segmented Capsule
                                        html.Div(
                                            className="segmented-capsule segmented-pill-container",
                                            children=[
                                                dbc.RadioItems(
                                                    id="theme-toggle",
                                                    options=[
                                                        {"label": "DARK", "value": "dark"},
                                                        {"label": "LIGHT", "value": "light"},
                                                    ],
                                                    value="dark",
                                                    inline=True,
                                                    className="segmented-radio-items",
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ]
                ),

                # Executive Summary Performance Metrics
                html.Div(
                    className="d-flex justify-content-between align-items-center mb-2 px-1",
                    children=[
                        html.Div(
                            className="d-flex align-items-center gap-2",
                            children=[
                                html.Span(className="status-dot-active"),
                                html.Span("EXECUTIVE PERFORMANCE SUMMARY", className="kpi-header-label mb-0 fw-bold", style={"letterSpacing": "0.08em", "color": "var(--text-muted)"}),
                            ]
                        ),
                        html.Span("LATEST REPORTED CONSOLIDATED PROFILE", className="small text-muted font-monospace d-none d-sm-inline", style={"fontSize": "0.68rem"}),
                    ]
                ),
                # B. Bento KPI Strip (Bento Row 1 - 6 Balanced Modular Metrics with JetBrains Mono)
                dbc.Row(
                    className="g-3 mb-3",
                    children=[
                        dbc.Col(lg=2, md=4, sm=6, children=[html.Div(id="bento-kpi-rev", className="kpi-bento kpi-card")]),
                        dbc.Col(lg=2, md=4, sm=6, children=[html.Div(id="bento-kpi-yoy", className="kpi-bento kpi-card")]),
                        dbc.Col(lg=2, md=4, sm=6, children=[html.Div(id="bento-kpi-sssg", className="kpi-bento kpi-card")]),
                        dbc.Col(lg=2, md=4, sm=6, children=[html.Div(id="bento-kpi-stores", className="kpi-bento kpi-card")]),
                        dbc.Col(lg=2, md=4, sm=6, children=[html.Div(id="bento-kpi-margins", className="kpi-bento kpi-card")]),
                        dbc.Col(lg=2, md=4, sm=6, children=[html.Div(id="bento-kpi-ads", className="kpi-bento kpi-card")]),
                    ]
                ),

                # C. Executive "So What" Insight & Strategic Recommendation Panel
                html.Div(
                    id="executive-insight-panel",
                    className="bento-card mb-3 p-3 executive-insight-card",
                ),

                # D. Tab Navigation (Segmented Floating Pill Bar in Unified Capsule Track)
                html.Div(
                    className="w-100 mb-3",
                    children=[
                        html.Div(
                            className="segmented-pill-container tab-capsule-track w-100",
                            style={"width": "100%", "maxWidth": "100%"},
                            children=[
                                dbc.Tabs(
                                    id="executive-tabs",
                                    active_tab="tab-financial",
                                    className="floating-pill-tabs nav-pills w-100",
                                    children=[
                                        dbc.Tab(label="Financial & Margin Decomposition", tab_id="tab-financial"),
                                        dbc.Tab(label="Store Dynamics & Expansion", tab_id="tab-network"),
                                        dbc.Tab(label="Channel & Digital Order Mix", tab_id="tab-channels"),
                                        dbc.Tab(label="Operational Fact Table", tab_id="tab-grid"),
                                        dbc.Tab(label="Supply Chain & Cost Breakdown", tab_id="tab-supply-chain"),
                                        dbc.Tab(label="Brand & Format Performance", tab_id="tab-brand-performance"),
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                # Dynamic Tab Content Area
                html.Div(
                    id="tab-content-container",
                    children=[
                # Horizon Segmented Control Ribbon (Positioned directly above charts)
                html.Div(
                    id="horizon-container",
                    className="bento-card horizon-banner-card mb-3",
                    children=[
                        dbc.Row(
                            align="center",
                            className="w-100 g-2",
                            children=[
                                dbc.Col(
                                    md=5, sm=12,
                                    children=[
                                        html.Div(
                                            className="d-flex align-items-center gap-2",
                                            children=[
                                                html.Span("ANALYTICAL HORIZON", className="kpi-header-label mb-0 fw-bold", style={"letterSpacing": "0.08em"}),
                                                html.Span(id="slider-range-indicator", className="small text-info fw-semibold font-monospace"),
                                            ]
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    md=7, sm=12,
                                    className="d-flex justify-content-md-end align-items-center gap-2",
                                    children=[
                                        html.Span("TIMEFRAME PRESET:", className="kpi-header-label mb-0 small text-muted d-none d-sm-inline"),
                                        html.Div(
                                            id="horizon-preset-capsule",
                                            className="segmented-capsule segmented-pill-container",
                                            children=[
                                                dbc.RadioItems(
                                                    id="horizon-capsule-toggle",
                                                    options=[
                                                        {"label": "ALL", "value": "ALL"},
                                                        {"label": "FY25", "value": "FY25"},
                                                        {"label": "FY24", "value": "FY24"},
                                                    ],
                                                    value="ALL",
                                                    inline=True,
                                                    className="segmented-radio-items",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                        # Tab 1: Financial & Margin Decomposition
                        html.Div(
                            id="content-tab-financial", className="tab-content",
                            children=[
                                dbc.Row(
                                    className="g-3",
                                    children=[
                                        dbc.Col(
                                            lg=12, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Gross Margin vs Operating EBITDA Margin Trajectory", className="chart-card-title"),
                                                        dcc.Graph(id="chart-margin-trends", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    className="g-3 mt-1",
                                    children=[
                                        dbc.Col(
                                            md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Quarterly Revenue Expansion & YoY Growth Velocity", className="chart-card-title"),
                                                        dcc.Graph(id="chart-revenue-yoy-trajectory", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),

                        # Tab 2: Store Dynamics & Regional Expansion
                        html.Div(
                            id="content-tab-network", className="tab-content",
                            style={"display": "none"},
                            children=[
                                dbc.Row(
                                    className="g-3",
                                    children=[
                                        dbc.Col(
                                            lg=6, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Store Network Rollout: Gross Openings vs Closures", className="chart-card-title"),
                                                        dcc.Graph(id="chart-openings-closures", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=6, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("SSSG vs Net Store Addition Elasticity & Cannibalization Curve", className="chart-card-title"),
                                                        dcc.Graph(id="chart-store-elasticity", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    className="g-3 mt-1",
                                    children=[
                                        dbc.Col(
                                            md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Geographic Penetration & Cluster Store Density", className="chart-card-title"),
                                                        dcc.Graph(id="chart-geographic-map", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),

                        # Tab 3: Channel & Digital Order Mix
                        html.Div(
                            id="content-tab-channels", className="tab-content",
                            style={"display": "none"},
                            children=[
                                dbc.Row(
                                    className="g-3",
                                    children=[
                                        dbc.Col(
                                            lg=7, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Omnichannel Revenue Mix Evolution (% of Total Sales)", className="chart-card-title"),
                                                        dcc.Graph(id="chart-omnichannel-split", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=5, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Digital Growth Drivers: App MAUs & Owned Delivery Share", className="chart-card-title"),
                                                        dcc.Graph(id="chart-digital-growth", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    className="g-3 mt-1",
                                    children=[
                                        dbc.Col(
                                            lg=6, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Channel Economics: Direct App (OLO) vs Aggregators", className="chart-card-title"),
                                                        dcc.Graph(id="chart-channel-economics", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=6, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Aggregator Commission Leakage & 5% Channel Shift Recovery", className="chart-card-title"),
                                                        dcc.Graph(id="chart-commission-leakage", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),

                        # Tab 4: Granular Operational Data Grid
                        html.Div(
                            id="content-tab-grid", className="tab-content",
                            style={"display": "none"},
                            children=[
                                html.Div(
                                    className="bento-card",
                                    children=[
                                        html.Div(
                                            className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2",
                                            children=[
                                                html.Div([
                                                    html.H6("Operational Fact Table", className="m-0 fw-bold text-uppercase", style={"letterSpacing": "0.05em", "color": "var(--text-primary)"}),
                                                    html.Span("Multi-threaded analytical query execution via Polars. Interactive sorting, column-filtering, and pagination.", className="text-muted small", style={"color": "var(--text-muted)"}),
                                                ]),
                                                dbc.Button(
                                                    "Export CSV",
                                                    id="btn-export-grid",
                                                    color="dark",
                                                    size="sm",
                                                    className="border border-secondary px-3 py-1",
                                                    style={"borderRadius": "8px", "fontWeight": "600", "fontSize": "0.78rem"}
                                                )
                                            ]
                                        ),
                                        dag.AgGrid(
                                            id="operational-grid",
                                            columnDefs=[
                                                {"headerName": "Period", "field": "quarter", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "Brand Concept", "field": "brand", "sortable": True, "filter": True, "minWidth": 130},
                                                {"headerName": "Revenue", "field": "revenue_disp", "sortable": True, "filter": "agNumberColumnFilter", "minWidth": 110},
                                                {"headerName": "YoY Growth", "field": "yoy_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "QoQ Growth", "field": "qoq_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "SSSG %", "field": "sssg_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "Stores", "field": "stores", "sortable": True, "filter": "agNumberColumnFilter", "minWidth": 110},
                                                {"headerName": "Net Adds", "field": "net_adds", "sortable": True, "filter": "agNumberColumnFilter", "minWidth": 110},
                                                {"headerName": "Gross Margin %", "field": "gm_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "EBITDA Margin %", "field": "ebitda_pct_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "EBITDA Amt", "field": "ebitda_amt_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "ADS per Store", "field": "ads_disp", "sortable": True, "filter": True, "minWidth": 110},
                                                {"headerName": "Digital MAUs", "field": "digital_maus_disp", "sortable": True, "filter": True, "minWidth": 110},
                                            ],
                                            defaultColDef={
                                                "resizable": True,
                                                "sortable": True,
                                                "filter": True,
                                                "minWidth": 110,
                                                "flex": 1,
                                            },
                                            columnSize="sizeToFit",
                                            dashGridOptions={
                                                "pagination": True,
                                                "paginationPageSize": 16,
                                                "animateRows": True,
                                                "rowSelection": "single",
                                                "suppressHorizontalScroll": False,
                                                "rowBuffer": 10,
                                            },
                                            className="ag-theme-alpine-dark",
                                            style={"width": "100%", "height": "520px"},
                                        )
                                    ]
                                )
                            ]
                        ),
                        # Tab 5: Supply Chain & Cost Breakdown
                        html.Div(
                            id="content-tab-supply-chain", className="tab-content",
                            style={"display": "none"},
                            children=[
                                dbc.Row(
                                    className="g-3",
                                    children=[
                                        dbc.Col(
                                            lg=7, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Unit Economics & Cost Waterfall Bridge (COGS to EBITDA)", className="chart-card-title"),
                                                        dcc.Graph(id="chart-cost-waterfall", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=5, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Raw Material Input Inflation Sensitivity (±5% Shock)", className="chart-card-title"),
                                                        dcc.Graph(id="chart-cogs-sensitivity", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    className="g-3 mt-1",
                                    children=[
                                        dbc.Col(
                                            lg=4, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Commissaries & Processing Hubs", className="kpi-header-label mb-2 fw-bold", style={"color": "var(--cyan-accent)"}),
                                                        html.P("Dedicated regional food processing hubs (Greater Noida, Bengaluru, Nagpur, Mumbai & Kolkata) ensure 100% standardized dough, sauce, and cheese supply across 3,000+ stores with central economies of scale.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=4, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Cold-Chain Logistics & Quality", className="kpi-header-label mb-2 fw-bold", style={"color": "var(--green-accent)"}),
                                                        html.P("Temperature-controlled distribution fleet operating on dynamic route-optimization algorithms maintaining 99.8% on-time inventory replenishment to tier 1-4 hubs.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=4, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Raw Material Hedging & Efficiency", className="kpi-header-label mb-2 fw-bold", style={"color": "var(--nothing-red)"}),
                                                        html.P("Direct-to-farm dairy, poultry, and packaging procurement partnerships insulate operating margins from commodity price spikes and global dairy inflation.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),

                        # Tab 6: Brand & Format Performance
                        html.Div(
                            id="content-tab-brand-performance", className="tab-content",
                            style={"display": "none"},
                            children=[
                                dbc.Row(
                                    className="g-3",
                                    children=[
                                        dbc.Col(
                                            lg=5, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Operating Format Distribution (Dine-in, Delivery, Transit)", className="chart-card-title"),
                                                        dcc.Graph(id="chart-format-breakdown", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=7, md=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Multi-Brand Portfolio Benchmarking: Margins & ADS", className="chart-card-title"),
                                                        dcc.Graph(id="chart-brand-unit-economics", config={"displayModeBar": False}),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    className="g-3 mt-1",
                                    children=[
                                        dbc.Col(
                                            lg=3, md=6, sm=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Domino's India", className="kpi-header-label mb-2 fw-bold", style={"color": "#0B648F"}),
                                                        html.P("Anchor QSR pizza franchise with 2,000+ stores across 400+ cities, leading delivery share and industry-best 20-min delivery guarantee.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=3, md=6, sm=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Popeyes India", className="kpi-header-label mb-2 fw-bold", style={"color": "#F26722"}),
                                                        html.P("High-growth Louisiana fried chicken concept expanding rapidly across Indian metro hubs with strong unit economics.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=3, md=6, sm=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("Dunkin' & Hong's Kitchen", className="kpi-header-label mb-2 fw-bold", style={"color": "#E11383"}),
                                                        html.P("Youth-centric coffee & bakery format alongside Chinese QSR concept driving non-pizza afternoon daypart snacking.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            lg=3, md=6, sm=12,
                                            children=[
                                                html.Div(
                                                    className="bento-card",
                                                    children=[
                                                        html.H6("DP Eurasia", className="kpi-header-label mb-2 fw-bold", style={"color": "#2A9D8F"}),
                                                        html.P("Market-leading pizza retail network spanning Turkey, Azerbaijan, Georgia & Kazakhstan with 700+ stores pro forma.", className="text-muted small mb-0"),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                    ]
                )
            ]
        )
    ]
)


# -----------------------------------------------------------------------------
# 5. GRANULAR REACTIVE EVENT ARCHITECTURE (CALLBACKS)
# -----------------------------------------------------------------------------
# Callback: Theme Switcher (Updating DOM data-theme attribute and theme store)
@app.callback(
    [
        Output("theme-wrapper", "data-theme"),
        Output("theme-store", "data"),
    ],
    Input("theme-toggle", "value"),
)
def switch_theme(theme_val):
    theme = theme_val if theme_val in ["dark", "light"] else "dark"
    return theme, theme

# Callback: Tab Switcher (Display Toggling for 6 categories)
@app.callback(
    [
        Output("content-tab-financial", "style"),
        Output("content-tab-network", "style"),
        Output("content-tab-channels", "style"),
        Output("content-tab-grid", "style"),
        Output("content-tab-supply-chain", "style"),
        Output("content-tab-brand-performance", "style"),
    ],
    Input("executive-tabs", "active_tab"),
)
def switch_executive_tabs(active_tab):
    visible = {"display": "block"}
    hidden = {"display": "none"}
    return (
        visible if active_tab == "tab-financial" else hidden,
        visible if active_tab == "tab-network" else hidden,
        visible if active_tab == "tab-channels" else hidden,
        visible if active_tab == "tab-grid" else hidden,
        visible if active_tab == "tab-supply-chain" else hidden,
        visible if active_tab == "tab-brand-performance" else hidden,
    )


# Callback: Horizon Capsule Preset Router
@app.callback(
    Output("horizon-range-store", "data"),
    Input("horizon-capsule-toggle", "value"),
)
def update_horizon_range(preset_val):
    if preset_val == "ALL":
        return [HIST_Q, N_Q - 1]
    elif preset_val == "FY25":
        return [12, 15]
    elif preset_val == "FY24":
        return [8, 11]
    return [HIST_Q, N_Q - 1]


# Callback: AG-Grid CSV Export Trigger
@app.callback(
    Output("operational-grid", "exportDataAsCsv"),
    Input("btn-export-grid", "n_clicks"),
    prevent_initial_call=True,
)
def export_grid_csv(n_clicks):
    return bool(n_clicks)


# Main Reactive Analytics Callback
@app.callback(
    [
        # Header Context Indicator
        Output("slider-range-indicator", "children"),
        # Top Executive KPI Strip (Bento Row 1)
        Output("bento-kpi-rev", "children"),
        Output("bento-kpi-yoy", "children"),
        Output("bento-kpi-sssg", "children"),
        Output("bento-kpi-stores", "children"),
        Output("bento-kpi-margins", "children"),
        Output("bento-kpi-ads", "children"),
        # Executive Insight Panel
        Output("executive-insight-panel", "children"),
        # Tab 1 Figures: Financial & Margin Decomposition
        Output("chart-margin-trends", "figure"),
        Output("chart-revenue-yoy-trajectory", "figure"),
        # Tab 2 Figures: Store Dynamics & Regional Expansion
        Output("chart-openings-closures", "figure"),
        Output("chart-store-elasticity", "figure"),
        Output("chart-geographic-map", "figure"),
        # Tab 3 Figures: Channel & Digital Order Mix
        Output("chart-omnichannel-split", "figure"),
        Output("chart-digital-growth", "figure"),
        Output("chart-channel-economics", "figure"),
        Output("chart-commission-leakage", "figure"),
        # Tab 4 Fact Table: AG-Grid Row Data
        Output("operational-grid", "rowData"),
        # Tab 5 Figures: Supply Chain & Cost Breakdown
        Output("chart-cost-waterfall", "figure"),
        Output("chart-cogs-sensitivity", "figure"),
        # Tab 6 Figures: Brand & Format Performance
        Output("chart-format-breakdown", "figure"),
        Output("chart-brand-unit-economics", "figure"),
    ],
    [
        Input("brand-dropdown", "value"),
        Input("horizon-range-store", "data"),
        Input("currency-toggle", "value"),
        Input("theme-store", "data"),
    ],
)
def update_dashboard(selected_brand: str, horizon_range: list[int], unit_mode: str, current_theme: str):
    t_from, t_to = horizon_range[0], horizon_range[1]
    q_start = METADATA_QUARTERS[t_from]
    q_end = METADATA_QUARTERS[t_to]

    # Query timeseries data via Polars LazyFrame and convert at viz boundary
    df_brand = query_brand_data(selected_brand, t_from, t_to)
    df_full = query_full_history(selected_brand)

    # Current quarter and historical references
    cur = df_full.loc[t_to]
    prev_q = df_full.loc[t_to - 1] if (t_to - 1) in df_full.index else cur
    prev_y = df_full.loc[t_to - 4] if (t_to - 4) in df_full.index else cur

    range_indicator = f"{q_start} → {q_end}" if q_start != q_end else q_start

    # Theme colors
    is_dark = (current_theme == "dark")
    green_accent = "#10B981" if is_dark else "#059669"
    red_accent = "#F43F5E" if is_dark else "#E11D48"
    cyan_accent = "#38BDF8" if is_dark else "#0284C7"

    # 1. KPI 1: Quarterly Revenue
    _, rev_str = convert_val(cur["revenue"], unit_mode)
    qoq_val = cur["qoq"]
    qoq_cls = "pill-delta-pos" if qoq_val >= 0 else "pill-delta-neg"
    kpi_rev_el = [
        html.Div(html.Div("Quarterly Revenue", className="kpi-header-label mb-0"), className="kpi-card-header"),
        html.Div(html.Div(rev_str, className="kpi-mono-num kpi-value metric-number"), className="kpi-card-body"),
        html.Div(
            html.Div([
                html.Span("▲ " if qoq_val >= 0 else "▼ "),
                html.Span(f"{abs(qoq_val):.1f}% QoQ"),
            ], className=qoq_cls),
            className="kpi-card-footer",
        ),
    ]

    # 2. KPI 2: YoY Revenue Growth Velocity
    yoy_val = cur["yoy"]
    yoy_cls = "pill-delta-pos" if yoy_val >= 0 else "pill-delta-neg"
    kpi_yoy_el = [
        html.Div(html.Div("YoY Expansion", className="kpi-header-label mb-0"), className="kpi-card-header"),
        html.Div(html.Div(f"{yoy_val:+.1f}%", className="kpi-mono-num kpi-value metric-number", style={"color": green_accent if yoy_val >= 0 else red_accent}), className="kpi-card-body"),
        html.Div(
            html.Div([
                html.Span(f"Base: {METADATA_QUARTERS[t_to - 4]}" if (t_to - 4) >= 0 else "Initial Horizon"),
            ], className="pill-delta-neutral"),
            className="kpi-card-footer",
        ),
    ]

    # 3. KPI 3: SSSG % (Same-Store Sales Growth)
    sssg_val = cur["sssg"]
    if pd.isna(sssg_val):
        sssg_str = "N/A"
        sssg_cls = "pill-delta-neutral"
        sssg_sub = "Historical Baseline"
    else:
        sssg_str = f"{sssg_val:+.1f}%"
        sssg_cls = "pill-delta-pos" if sssg_val >= 0 else "pill-delta-neg"
        sssg_sub = "Mature Store Cohort"
    kpi_sssg_el = [
        html.Div(html.Div("SSSG Growth", className="kpi-header-label mb-0"), className="kpi-card-header"),
        html.Div(html.Div(sssg_str, className="kpi-mono-num kpi-value metric-number"), className="kpi-card-body"),
        html.Div(
            html.Div([
                html.Span(sssg_sub),
            ], className=sssg_cls),
            className="kpi-card-footer",
        ),
    ]

    # 4. KPI 4: Active Restaurant Count & Net Additions
    stores_val = int(cur["stores"])
    net_adds_val = int(cur["net_adds"])
    kpi_stores_el = [
        html.Div(html.Div("Network Footprint", className="kpi-header-label mb-0"), className="kpi-card-header"),
        html.Div(html.Div(f"{stores_val:,}", className="kpi-mono-num kpi-value metric-number"), className="kpi-card-body"),
        html.Div(
            html.Div([
                html.Span(f"+{net_adds_val} Net Adds in {q_end}"),
            ], className="pill-delta-pos" if net_adds_val >= 0 else "pill-delta-neg"),
            className="kpi-card-footer",
        ),
    ]

    # 5. KPI 5: Operating Margins (Gross & EBITDA)
    gm_val = cur["gross_margin"]
    ebitda_val = cur["ebitda_pct"]
    gm_prev_y = prev_y["gross_margin"]
    bps_delta = int((gm_val - gm_prev_y) * 100)
    bps_cls = "pill-delta-pos" if bps_delta >= 0 else "pill-delta-neg"
    kpi_margins_el = [
        html.Div(html.Div("Gross / EBITDA Margin", className="kpi-header-label mb-0"), className="kpi-card-header"),
        html.Div(
            html.Div(
                className="d-flex align-items-center justify-content-between flex-wrap gap-1 my-0 w-100",
                children=[
                    html.Span(
                        [
                            html.Span(f"{gm_val:.1f}%", className="kpi-mono-num kpi-value metric-number", style={"fontSize": "clamp(1.05rem, 1.25vw, 1.35rem)", "letterSpacing": "-0.02em"}),
                            html.Span(" GM", className="text-muted fw-bold ms-1", style={"fontSize": "0.72rem", "letterSpacing": "0.5px"}),
                        ],
                        className="metric-badge-item d-inline-flex align-items-baseline",
                    ),
                    html.Span("|", className="text-muted opacity-50 px-1", style={"fontSize": "1rem", "fontWeight": "300"}),
                    html.Span(
                        [
                            html.Span(f"{ebitda_val:.1f}%", className="kpi-mono-num kpi-value metric-number", style={"fontSize": "clamp(1.05rem, 1.25vw, 1.35rem)", "letterSpacing": "-0.02em", "color": "var(--green-accent)" if ebitda_val >= 0 else "var(--nothing-red)"}),
                            html.Span(" EBITDA", className="text-muted fw-bold ms-1", style={"fontSize": "0.72rem", "letterSpacing": "0.5px"}),
                        ],
                        className="metric-badge-item d-inline-flex align-items-baseline",
                    ),
                ],
            ),
            className="kpi-card-body",
        ),
        html.Div(
            html.Div([
                html.Span(f"{bps_delta:+d} bps YoY GM"),
            ], className=bps_cls),
            className="kpi-card-footer",
        ),
    ]

    # 6. KPI 6: Average Daily Sales (ADS) per Store
    ads_val = cur["ads_inr"]
    ads_str = convert_ads(ads_val, unit_mode)
    kpi_ads_el = [
        html.Div(html.Div("Average Daily Sales (ADS)", className="kpi-header-label mb-0"), className="kpi-card-header"),
        html.Div(html.Div(ads_str, className="kpi-mono-num kpi-value metric-number"), className="kpi-card-body"),
        html.Div(
            html.Div([
                html.Span(f"Per store / day in {q_end}"),
            ], className="pill-delta-neutral"),
            className="kpi-card-footer",
        ),
    ]

    # -------------------------------------------------------------------------
    # EXECUTIVE "SO WHAT" INSIGHT & STRATEGIC RECOMMENDATION
    # -------------------------------------------------------------------------
    insight_panel_el = generate_executive_insights(selected_brand, cur, prev_y, q_end, is_dark)

    # -------------------------------------------------------------------------
    # TAB 1 FIGURES: Financial & Margin Decomposition
    # -------------------------------------------------------------------------
    # Chart 1: Margin Trend Analysis (Dual Axis)
    fig_margin_trends = go.Figure()
    fig_margin_trends.add_bar(
        x=df_brand["quarter"],
        y=df_brand["gross_margin"],
        name="Gross Margin %",
        marker_color="rgba(0, 240, 255, 0.35)" if is_dark else "rgba(2, 132, 199, 0.3)",
        hovertemplate="Gross Margin: %{y:.1f}%<extra></extra>",
    )
    fig_margin_trends.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["ebitda_pct"],
        name="EBITDA Margin %",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color=green_accent, width=2.8),
        marker=dict(size=6, color=green_accent),
        hovertemplate="EBITDA Margin: %{y:.1f}%<extra></extra>",
    )
    fig_margin_trends.update_layout(
        yaxis=dict(title=dict(text="Gross Margin (%)", font=dict(color="#94A3B8")), ticksuffix="%"),
        yaxis2=dict(title=dict(text="EBITDA Margin (%)", font=dict(color="#10B981" if is_dark else "#059669")), overlaying="y", side="right", showgrid=False, ticksuffix="%"),
    )
    apply_spatial_layout(fig_margin_trends, theme=current_theme, height=370)

    # Chart 2: Revenue Trajectory with YoY Growth Velocity
    c_hex = BRAND_COLORS.get(selected_brand, cyan_accent)
    fig_rev_traj = go.Figure()
    fig_rev_traj.add_bar(
        x=df_brand["quarter"],
        y=df_brand["revenue"].map(lambda x: convert_val(x, unit_mode)[0]),
        name=f"Revenue ({unit_mode})",
        marker_color=c_hex,
        opacity=0.9,
        hovertemplate="Revenue: %{y:,.1f}<extra></extra>",
    )
    fig_rev_traj.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["yoy"],
        name="YoY Growth %",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color=red_accent, width=2.6),
        marker=dict(size=5, color=red_accent),
        hovertemplate="YoY: %{y:.1f}%<extra></extra>",
    )
    fig_rev_traj.update_layout(
        yaxis=dict(title=dict(text=f"Revenue ({unit_mode})", font=dict(color="#94A3B8"))),
        yaxis2=dict(title=dict(text="YoY Growth (%)", font=dict(color=red_accent)), overlaying="y", side="right", showgrid=False, ticksuffix="%"),
    )
    apply_spatial_layout(fig_rev_traj, theme=current_theme, height=370)

    # -------------------------------------------------------------------------
    # TAB 2 FIGURES: Store Dynamics & Regional Expansion (Polars Cohort Pipeline)
    # -------------------------------------------------------------------------
    # Chart 3: Gross Openings vs Closures per quarter
    fig_open_close = go.Figure()
    fig_open_close.add_bar(
        x=df_brand["quarter"],
        y=df_brand["gross_openings"],
        name="Gross Openings",
        marker_color=green_accent,
        hovertemplate="Openings: +%{y}<extra></extra>",
    )
    fig_open_close.add_bar(
        x=df_brand["quarter"],
        y=-df_brand["closures"],
        name="Closures",
        marker_color=red_accent,
        hovertemplate="Closures: -%{customdata}<extra></extra>",
        customdata=df_brand["closures"],
    )
    fig_open_close.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["net_adds"],
        name="Net Additions",
        mode="lines+markers",
        line=dict(color=cyan_accent, width=2.5, dash="dot"),
        marker=dict(size=6, color=cyan_accent),
        hovertemplate="Net Adds: %{y}<extra></extra>",
    )
    fig_open_close.update_layout(
        barmode="relative",
        yaxis=dict(title=dict(text="Store Network Change", font=dict(color="#94A3B8"))),
    )
    apply_spatial_layout(fig_open_close, theme=current_theme, height=370)

    # Chart 4: SSSG vs Net Store Addition Elasticity & Cannibalization Curve
    df_elasticity = compute_store_cohort_elasticity(selected_brand, t_from, t_to)
    fig_store_elasticity = go.Figure()
    fig_store_elasticity.add_bar(
        x=df_elasticity["quarter"],
        y=df_elasticity["net_store_growth_pct"],
        name="Net Store Growth %",
        marker_color="rgba(0, 240, 255, 0.4)" if is_dark else "rgba(2, 132, 199, 0.35)",
        hovertemplate="Net Store Growth: %{y:.1f}%<extra></extra>",
    )
    fig_store_elasticity.add_scatter(
        x=df_elasticity["quarter"],
        y=df_elasticity["sssg"],
        name="SSSG %",
        mode="lines+markers",
        line=dict(color=green_accent, width=2.8),
        marker=dict(size=6, color=green_accent),
        hovertemplate="SSSG: %{y:.1f}%<extra></extra>",
    )
    fig_store_elasticity.add_scatter(
        x=df_elasticity["quarter"],
        y=df_elasticity["elasticity_ratio"],
        name="Elasticity Ratio",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#F59E0B", width=2.2, dash="dash"),
        marker=dict(size=5, color="#F59E0B"),
        hovertemplate="Elasticity: %{y:.2f}x<extra></extra>",
    )
    fig_store_elasticity.update_layout(
        yaxis=dict(title=dict(text="Growth / SSSG (%)", font=dict(color="#94A3B8")), ticksuffix="%"),
        yaxis2=dict(title=dict(text="Elasticity (x)", font=dict(color="#F59E0B")), overlaying="y", side="right", showgrid=False),
    )
    apply_spatial_layout(fig_store_elasticity, theme=current_theme, height=370)

    # Chart 5: Geographic Penetration Heatmap / Density Scatter Map
    df_geo = query_geo_data()
    if selected_brand != TOTAL:
        df_geo_filtered = df_geo[df_geo["brand_focus"] == selected_brand]
        if len(df_geo_filtered) == 0:
            df_geo_filtered = df_geo
    else:
        df_geo_filtered = df_geo

    map_style = "carto-darkmatter" if is_dark else "carto-positron"
    if hasattr(px, "scatter_map"):
        fig_map = px.scatter_map(
            df_geo_filtered,
            lat="lat",
            lon="lon",
            size="stores",
            color="revenue_cr",
            hover_name="territory",
            hover_data=["region", "stores", "revenue_cr", "brand_focus"],
            color_continuous_scale="Viridis",
            size_max=24,
            zoom=3.2,
            center={"lat": 26.0, "lon": 65.0},
        )
        fig_map.update_layout(map_style=map_style)
    else:
        fig_map = px.scatter_mapbox(
            df_geo_filtered,
            lat="lat",
            lon="lon",
            size="stores",
            color="revenue_cr",
            hover_name="territory",
            hover_data=["region", "stores", "revenue_cr", "brand_focus"],
            color_continuous_scale="Viridis",
            size_max=24,
            zoom=3.2,
            center={"lat": 26.0, "lon": 65.0},
        )
        fig_map.update_layout(mapbox_style=map_style)

    fig_map.update_layout(
        title=None,
        hoverlabel=dict(
            bgcolor="rgba(10, 13, 20, 0.92)",
            bordercolor="rgba(0, 240, 255, 0.4)",
            font=dict(color="#F8FAFC", family="'JetBrains Mono', monospace", size=12),
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Revenue (₹ Cr)", font=dict(color="#94A3B8", size=10)),
            tickfont=dict(color="#94A3B8", size=9),
        ),
        margin={"r": 15, "t": 40, "l": 15, "b": 15},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=420,
    )

    # -------------------------------------------------------------------------
    # TAB 3 FIGURES: Channel & Digital Order Mix (Polars RFM & AOV Pipeline)
    # -------------------------------------------------------------------------
    # Chart 6: Omnichannel Split (Stacked Area Chart)
    fig_channel = go.Figure()
    fig_channel.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["channel_app_delivery_pct"],
        name="Owned App & Direct Delivery",
        mode="lines",
        stackgroup="one",
        line=dict(width=0.5, color="#0B648F"),
        hovertemplate="Owned App: %{y:.1f}%<extra></extra>",
    )
    fig_channel.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["channel_aggregators_pct"],
        name="Food Aggregators (Zomato/Swiggy)",
        mode="lines",
        stackgroup="one",
        line=dict(width=0.5, color="#F26722"),
        hovertemplate="Aggregators: %{y:.1f}%<extra></extra>",
    )
    fig_channel.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["channel_dinein_pct"],
        name="In-Store Dine-In",
        mode="lines",
        stackgroup="one",
        line=dict(width=0.5, color="#E11383"),
        hovertemplate="Dine-In: %{y:.1f}%<extra></extra>",
    )
    fig_channel.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["channel_takeaway_pct"],
        name="Takeaway & Counter Pickup",
        mode="lines",
        stackgroup="one",
        line=dict(width=0.5, color="#C9A227"),
        hovertemplate="Takeaway: %{y:.1f}%<extra></extra>",
    )
    fig_channel.update_layout(yaxis=dict(title=dict(text="Revenue Mix Share (%)", font=dict(color="#94A3B8")), range=[0, 100], ticksuffix="%"))
    apply_spatial_layout(fig_channel, theme=current_theme, height=370)

    # Chart 7: Digital Growth Drivers (MAUs & Delivery Share)
    fig_digital = go.Figure()
    fig_digital.add_bar(
        x=df_brand["quarter"],
        y=df_brand["digital_maus"],
        name="App Monthly Active Users (MAUs)",
        marker_color=cyan_accent,
        opacity=0.85,
        hovertemplate="MAUs: %{y:.2f}M<extra></extra>",
    )
    fig_digital.add_scatter(
        x=df_brand["quarter"],
        y=df_brand["app_delivery_share"],
        name="Owned Delivery Share (%)",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color=green_accent, width=2.8),
        marker=dict(size=6, color=green_accent),
        hovertemplate="Owned Delivery: %{y:.1f}%<extra></extra>",
    )
    fig_digital.update_layout(
        yaxis=dict(title=dict(text="Digital MAUs (Millions)", font=dict(color="#94A3B8"))),
        yaxis2=dict(title=dict(text="Owned Delivery Share (%)", font=dict(color="#94A3B8")), overlaying="y", side="right", showgrid=False, ticksuffix="%"),
    )
    apply_spatial_layout(fig_digital, theme=current_theme, height=370)

    # Chart 8: Direct App vs Aggregator Basket Economics & Attachment Rates
    channels_labels = ["Owned App (OLO)", "Aggregators (Swiggy/Zomato)"]
    fig_channel_econ = go.Figure()
    fig_channel_econ.add_bar(
        x=channels_labels,
        y=[465, 395],
        name="Average Order Value (₹)",
        marker_color=[cyan_accent, "#F26722"],
        hovertemplate="%{x} AOV: ₹%{y}<extra></extra>",
    )
    fig_channel_econ.add_bar(
        x=channels_labels,
        y=[64.5, 41.8],
        name="Side Attachment %",
        marker_color=["#10B981", "#E11383"],
        hovertemplate="%{x} Sides: %{y:.1f}%<extra></extra>",
    )
    fig_channel_econ.add_bar(
        x=channels_labels,
        y=[48.2, 31.0],
        name="Beverage Attachment %",
        marker_color=["#38BDF8", "#C9A227"],
        hovertemplate="%{x} Drinks: %{y:.1f}%<extra></extra>",
    )
    fig_channel_econ.update_layout(barmode="group", yaxis=dict(title=dict(text="Ticket Size (₹) & Attachment (%)", font=dict(color="#94A3B8"))))
    apply_spatial_layout(fig_channel_econ, theme=current_theme, height=370)

    # Chart 9: Aggregator Commission Leakage & 5% Channel Shift Recovery Bridge
    rev_raw = float(cur["revenue"])
    agg_share = float(cur["channel_aggregators_pct"])
    agg_vol = rev_raw * (agg_share / 100.0)
    shift_vol = agg_vol * 0.05
    gross_saved = shift_vol * 0.225
    fulfillment_cost = shift_vol * 0.04
    net_recovered = gross_saved - fulfillment_cost

    fig_comm_leakage = go.Figure(go.Waterfall(
        name="Commission Recovery",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["5% Aggregator Volume Shift", "Gross Commission Saved (22.5%)", "App Delivery Fulfillment (4%)", "Net Recovered EBITDA"],
        textposition="outside",
        cliponaxis=False,
        text=[f"₹{shift_vol:.1f} Cr", f"+₹{gross_saved:.2f} Cr", f"-₹{fulfillment_cost:.2f} Cr", f"+₹{net_recovered:.2f} Cr"],
        y=[shift_vol, gross_saved, -fulfillment_cost, net_recovered],
        connector={"line": {"color": "rgba(255, 255, 255, 0.2)" if is_dark else "rgba(0,0,0,0.2)"}},
        decreasing={"marker": {"color": red_accent}},
        increasing={"marker": {"color": green_accent}},
        totals={"marker": {"color": cyan_accent}},
        hovertemplate="%{x}: %{y:.2f} Cr<extra></extra>",
    ))
    apply_spatial_layout(fig_comm_leakage, theme=current_theme, height=370)
    fig_comm_leakage.update_traces(textfont=dict(color="#00F0FF" if is_dark else "#0F172A", size=12))

    # -------------------------------------------------------------------------
    # TAB 4 FACT TABLE: Granular Operational Grid
    # -------------------------------------------------------------------------
    df_grid = df_brand.copy()
    df_grid["revenue_disp"] = df_grid["revenue"].map(lambda x: convert_val(x, unit_mode)[1])
    df_grid["yoy_disp"] = df_grid["yoy"].map(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
    df_grid["qoq_disp"] = df_grid["qoq"].map(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
    df_grid["sssg_disp"] = df_grid["sssg"].map(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
    df_grid["gm_disp"] = df_grid["gross_margin"].map(lambda x: f"{x:.1f}%")
    df_grid["ebitda_pct_disp"] = df_grid["ebitda_pct"].map(lambda x: f"{x:.1f}%")
    df_grid["ebitda_amt_disp"] = df_grid["ebitda_amt"].map(lambda x: convert_val(x, unit_mode)[1])
    df_grid["ads_disp"] = df_grid["ads_inr"].map(lambda x: convert_ads(x, unit_mode))
    df_grid["digital_maus_disp"] = df_grid["digital_maus"].map(lambda x: f"{x:.2f}M" if pd.notna(x) else "N/A")
    grid_rows = df_grid.to_dict("records")

    # -------------------------------------------------------------------------
    # TAB 5 FIGURES: Supply Chain & Cost Breakdown (Polars Sensitivity Model)
    # -------------------------------------------------------------------------
    # Chart 10: Cost Structure Waterfall
    rev_c, _ = convert_val(cur["revenue"], unit_mode)
    cogs_c, _ = convert_val(cur["cogs_amt"], unit_mode)
    staff_c, _ = convert_val(cur["staff_amt"], unit_mode)
    occ_c, _ = convert_val(cur["occupancy_amt"], unit_mode)
    roy_c, _ = convert_val(cur["royalty_amt"], unit_mode)
    oth_c, _ = convert_val(cur["other_opex_amt"], unit_mode)
    ebitda_c, _ = convert_val(cur["ebitda_amt"], unit_mode)

    fig_waterfall = go.Figure(go.Waterfall(
        name="Cost Waterfall",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "Raw Material", "Personnel", "Occupancy", "Royalty", "Other Opex", "EBITDA"],
        textposition="outside",
        cliponaxis=False,
        text=[f"{v:,.1f}" for v in [rev_c, -cogs_c, -staff_c, -occ_c, -roy_c, -oth_c, ebitda_c]],
        y=[rev_c, -cogs_c, -staff_c, -occ_c, -roy_c, -oth_c, ebitda_c],
        connector={"line": {"color": "rgba(255, 255, 255, 0.2)" if is_dark else "rgba(0,0,0,0.2)"}},
        decreasing={"marker": {"color": red_accent}},
        increasing={"marker": {"color": green_accent}},
        totals={"marker": {"color": cyan_accent}},
        hovertemplate="%{x}: %{y:,.1f}<extra></extra>",
    ))
    apply_spatial_layout(fig_waterfall, theme=current_theme, height=370)
    fig_waterfall.update_traces(textfont=dict(color="#00F0FF" if is_dark else "#0F172A", size=12))
    fig_waterfall.update_layout(margin=dict(l=40, r=40, t=30, b=60))

    # Chart 11: Raw Material Commodity Input Inflation Sensitivity Model
    commodities = ["Edible Oils & Spices", "Packaging & Cartons", "Wheat & Flour", "Poultry & Proteins", "Dairy & Cheese"]
    bps_shock_pos = [-45, -55, -95, -125, -185]
    bps_shock_neg = [+45, +55, +95, +125, +185]
    fig_cogs_sens = go.Figure()
    fig_cogs_sens.add_bar(
        y=commodities,
        x=bps_shock_pos,
        name="+5% Commodity Price Spike (Margin Drag)",
        orientation="h",
        marker_color=red_accent,
        hovertemplate="%{y}: %{x} bps EBITDA<extra></extra>",
    )
    fig_cogs_sens.add_bar(
        y=commodities,
        x=bps_shock_neg,
        name="-5% Commodity Deflation (Margin Expansion)",
        orientation="h",
        marker_color=green_accent,
        hovertemplate="%{y}: +%{x} bps EBITDA<extra></extra>",
    )
    fig_cogs_sens.update_layout(barmode="relative", xaxis=dict(title=dict(text="EBITDA Margin Sensitivity (Bps Impact)", font=dict(color="#94A3B8"))))
    apply_spatial_layout(fig_cogs_sens, theme=current_theme, height=370)

    # -------------------------------------------------------------------------
    # TAB 6 FIGURES: Brand & Format Performance (Polars Multi-Brand Pipeline)
    # -------------------------------------------------------------------------
    # Chart 12: Store Format Distribution Donut
    format_data = pd.DataFrame({
        "Format": ["Flagship / Dine-In", "Delivery & Dark Kitchen", "Food Court / Express", "Drive-thru / Transit"],
        "Share": [cur["format_flagship_pct"], cur["format_delivery_pct"], cur["format_foodcourt_pct"], cur["format_drivethru_pct"]],
    })
    fig_format = px.pie(
        format_data,
        names="Format",
        values="Share",
        hole=0.68,
        color="Format",
        color_discrete_sequence=["#0B648F", "#38BDF8", "#F26722", "#E11383"],
    )
    fig_format.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color="#F8FAFC" if is_dark else "#0F172A", size=11, family="'Inter', sans-serif"),
        hovertemplate="<b>%{label}</b>: %{value:.1f}%<extra></extra>",
    )
    center_text_color = "#F8FAFC" if is_dark else "#0F172A"
    fig_format.update_layout(
        title=None,
        showlegend=False,
        margin=dict(l=35, r=35, t=40, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b style='color:{center_text_color}; font-size:13px;'>FORMATS</b><br><span style='color:#64748B; font-size:10px;'>{q_end}</span>", x=0.5, y=0.5, font_size=11, showarrow=False)],
    )

    # Chart 13: Multi-Brand Portfolio Benchmarking (Cross-Brand Comparison)
    df_mb = compute_multibrand_benchmarking(q_end)
    fig_brand_econ = go.Figure()
    fig_brand_econ.add_bar(
        x=df_mb["brand"],
        y=df_mb["gross_margin"],
        name="Gross Margin %",
        marker_color=cyan_accent,
        hovertemplate="%{x} GM: %{y:.1f}%<extra></extra>",
    )
    fig_brand_econ.add_bar(
        x=df_mb["brand"],
        y=df_mb["ebitda_pct"],
        name="EBITDA Margin %",
        marker_color=green_accent,
        hovertemplate="%{x} EBITDA: %{y:.1f}%<extra></extra>",
    )
    fig_brand_econ.add_scatter(
        x=df_mb["brand"],
        y=df_mb["ads_inr"] / 1000.0,
        name="ADS (₹ '000/day)",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#F26722", width=2.8),
        marker=dict(size=7, color="#F26722"),
        hovertemplate="%{x} ADS: ₹%{y:.1f}k<extra></extra>",
    )
    fig_brand_econ.update_layout(
        barmode="group",
        yaxis=dict(title=dict(text="Margins (%)", font=dict(color="#94A3B8")), ticksuffix="%"),
        yaxis2=dict(title=dict(text="ADS (₹ '000 / day)", font=dict(color="#F26722")), overlaying="y", side="right", showgrid=False),
    )
    apply_spatial_layout(fig_brand_econ, theme=current_theme, height=370)

    return (
        range_indicator,
        kpi_rev_el,
        kpi_yoy_el,
        kpi_sssg_el,
        kpi_stores_el,
        kpi_margins_el,
        kpi_ads_el,
        insight_panel_el,
        fig_margin_trends,
        fig_rev_traj,
        fig_open_close,
        fig_store_elasticity,
        fig_map,
        fig_channel,
        fig_digital,
        fig_channel_econ,
        fig_comm_leakage,
        grid_rows,
        fig_waterfall,
        fig_cogs_sens,
        fig_format,
        fig_brand_econ,
    )


# -----------------------------------------------------------------------------
# 6. APPLICATION ENTRYPOINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False, dev_tools_ui=False, port=8055)
