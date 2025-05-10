import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ------------------ Depreciation Logic ------------------
def generate_periods(start_date, months, mode):
    if mode == "Monthly":
        return [start_date + relativedelta(months=i) for i in range(months)]
    else:
        return [start_date + relativedelta(years=i) for i in range(months // 12)]

def depreciation_row(asset_name, cost, salvage, start_date, useful_life, mode):
    months = useful_life * 12
    periods = generate_periods(start_date, months, mode)

    if mode == "Monthly":
        dep_per_period = (cost - salvage) / months
        labels = [p.strftime("%b %Y") for p in periods]
    else:
        dep_per_period = (cost - salvage) / useful_life
        labels = [p.strftime("%Y") for p in periods]

    dep_values = [round(dep_per_period, 2)] * len(labels)
    total = round(sum(dep_values), 2)
    row = dict(zip(labels, dep_values))
    row["Asset"] = asset_name
    row["Total Depreciation"] = total
    return row

# ------------------ Constants ------------------
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

# ------------------ UI ------------------
st.set_page_config(page_title="📊 Depreciation Calculator", layout="wide")

st.title("📊 Depreciation Schedule Builder")
st.markdown("Design and download **monthly or yearly depreciation schedules** for multiple assets with GAAP-specific logic.")
st.divider()

mode = st.radio("📆 Select Schedule Mode", ["Monthly", "Yearly"], horizontal=True)

num_assets = st.number_input("🔢 Number of Assets", min_value=1, max_value=10, value=2, step=1)
asset_inputs = []

for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1}"):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(f"Asset Name", value=f"Asset_{i+1}", key=f"name_{i}")
            cost = st.number_input("💰 Cost", min_value=0.0, value=10000.0, key=f"cost_{i}")
            start_date = st.date_input("📍 In-Service Date", value=date.today(), key=f"date_{i}")
        with col2:
            gaap = st.selectbox("📘 GAAP", ["US GAAP", "IFRS", "Indian GAAP"], key=f"gaap_{i}")
            asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES, key=f"type_{i}")
            salvage = st.number_input("♻️ Salvage Value", min_value=0.0, value=1000.0, key=f"salvage_{i}")
            default_life = GAAP_USEFUL_LIVES.get(gaap, {}).get(asset_type, 5)
            life = st.number_input("📅 Useful Life (Years)", min_value=1, value=default_life, key=f"life_{i}")

        asset_inputs.append({
            "name": asset_name,
            "cost": cost,
            "salvage": salvage,
            "start_date": start_date,
            "useful_life": life
        })

# ------------------ Generate Schedule ------------------
if st.button("📊 Generate Depreciation Schedule"):
    all_rows = []

    for asset in asset_inputs:
        row = depreciation_row(
            asset_name=asset["name"],
            cost=asset["cost"],
            salvage=asset["salvage"],
            start_date=asset["start_date"],
            useful_life=asset["useful_life"],
            mode=mode
        )
        all_rows.append(row)

    df = pd.DataFrame(all_rows).set_index("Asset")

    # Sort columns chronologically
    period_cols = [col for col in df.columns if col != "Total Depreciation"]
    sort_fmt = "%b %Y" if mode == "Monthly" else "%Y"
    sorted_cols = sorted(period_cols, key=lambda d: pd.to_datetime(d, format=sort_fmt))
    df = df[sorted_cols + ["Total Depreciation"]]

    # ------------------ Display ------------------
    st.subheader("📋 Full Depreciation Schedule")
    st.dataframe(df, use_container_width=True)

    # ------------------ Summary ------------------
    st.subheader("📈 Asset Summary Overview")
    last_period_col = df.columns[-2] if "Total Depreciation" in df.columns else df.columns[-1]

    summary_data = []
    for asset, row in df.iterrows():
        asset_input = next(a for a in asset_inputs if a["name"] == asset)
        summary_data.append({
            "Asset": asset,
            "Useful Life (Years)": asset_input["useful_life"],
            "Total Depreciation": row["Total Depreciation"],
            "Final Period": last_period_col
        })

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

    # Totals
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🧮 Total Assets:** `{len(df)}`")
    with col2:
        st.markdown(f"**💵 Total Depreciation:** `${df['Total Depreciation'].sum():,.2f}`")

    # Export
    csv = df.reset_index().to_csv(index=False).encode()
    st.download_button("⬇️ Download CSV", data=csv, file_name=f"{mode.lower()}_depreciation_schedule.csv")
