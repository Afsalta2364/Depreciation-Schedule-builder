import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ------------ Depreciation Logic ------------
def straight_line_yearly(cost, salvage, life_years, start_year, asset_name):
    annual = (cost - salvage) / life_years
    acc = 0
    rows = []
    for i in range(life_years):
        acc += annual
        book = cost - acc
        rows.append({
            "Asset": asset_name,
            "Period": f"Year {start_year + i}",
            "Depreciation Expense": round(annual, 2),
            "Accumulated Depreciation": round(acc, 2),
            "Book Value": round(book, 2)
        })
    return rows

# ------------ Constants ------------
ASSET_TYPES = [
    "Building", "Vehicle", "Machinery", "Furniture", "Computer Equipment",
    "Office Equipment", "Leasehold Improvements", "Land Improvements",
    "Software", "Intangible Asset (e.g., Patent)"
]
GAAP_USEFUL_LIVES = {
    "US GAAP": {"Building": 40, "Vehicle": 5, "Machinery": 10, "Furniture": 7},
    "IFRS": {"Building": 30, "Vehicle": 7, "Machinery": 8, "Furniture": 5},
    "Indian GAAP": {"Building": 30, "Vehicle": 8, "Machinery": 10, "Furniture": 6}
}

# ------------ UI Setup ------------
st.set_page_config("📦 Multi-Asset Depreciation Calculator")
st.title("📦 Multi-Asset Depreciation Calculator")

num_assets = st.number_input("How many assets to add?", min_value=1, max_value=10, value=2, step=1)

asset_inputs = []

# ------------ Dynamic Asset Input Forms ------------
for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1} Details"):
        asset_name = st.text_input(f"Asset Name #{i+1}", value=f"Asset_{i+1}", key=f"asset_name_{i}")
        gaap = st.selectbox("GAAP", ["US GAAP", "IFRS", "Indian GAAP"], key=f"gaap_{i}")
        asset_type = st.selectbox("Asset Type", ASSET_TYPES, key=f"type_{i}")
        cost = st.number_input("Asset Cost", min_value=0.0, value=10000.0, key=f"cost_{i}")
        salvage = st.number_input("Salvage Value", min_value=0.0, value=1000.0, key=f"salvage_{i}")
        start_date = st.date_input("In-Service Date", value=date.today(), key=f"date_{i}")
        default_life = GAAP_USEFUL_LIVES.get(gaap, {}).get(asset_type, 5)
        life = st.number_input(f"Useful Life (years) for {asset_type} under {gaap}", min_value=1, value=default_life, key=f"life_{i}")

        asset_inputs.append({
            "Asset": asset_name,
            "GAAP": gaap,
            "Asset Type": asset_type,
            "Cost": cost,
            "Salvage": salvage,
            "Start Date": start_date,
            "Useful Life": life
        })

# ------------ Generate Button ------------
if st.button("📊 Generate Depreciation Schedules"):
    all_rows = []
    for asset in asset_inputs:
        rows = straight_line_yearly(
            cost=asset["Cost"],
            salvage=asset["Salvage"],
            life_years=int(asset["Useful Life"]),
            start_year=asset["Start Date"].year,
            asset_name=asset["Asset"]
        )
        all_rows.extend(rows)

    if all_rows:
        df = pd.DataFrame(all_rows)
        st.success("✅ Schedules generated for all assets!")
        st.dataframe(df, use_container_width=True)

        st.subheader("📈 Summary")
        summary = df.groupby("Asset").agg({
            "Depreciation Expense": "sum",
            "Book Value": "last"
        }).rename(columns={
            "Depreciation Expense": "Total Depreciation",
            "Book Value": "Final Book Value"
        })
        st.dataframe(summary)

        csv = df.to_csv(index=False).encode()
        st.download_button("⬇️ Download Combined CSV", csv, "multi_asset_schedule.csv", "text/csv")
    else:
        st.warning("No schedules generated.")
