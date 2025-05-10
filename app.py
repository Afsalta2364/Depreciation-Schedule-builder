import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ------------------ Depreciation Logic ------------------
def generate_months(start_date, months):
    return [start_date + relativedelta(months=i) for i in range(months)]

def straight_line_monthly_row(asset_name, cost, salvage, start_date, useful_life):
    months = useful_life * 12
    monthly_dep = (cost - salvage) / months
    month_labels = [d.strftime("%b %Y") for d in generate_months(start_date, months)]
    dep_values = [round(monthly_dep, 2)] * months
    total = round(monthly_dep * months, 2)
    row = dict(zip(month_labels, dep_values))
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
st.set_page_config("📆 Monthly Depreciation - Multi Asset")
st.title("📆 Monthwise Depreciation Schedule (Wide Format)")

num_assets = st.number_input("How many assets to add?", min_value=1, max_value=10, value=2, step=1)

asset_inputs = []

for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1}"):
        asset_name = st.text_input(f"Asset Name #{i+1}", value=f"Asset_{i+1}", key=f"name_{i}")
        gaap = st.selectbox("GAAP", ["US GAAP", "IFRS", "Indian GAAP"], key=f"gaap_{i}")
        asset_type = st.selectbox("Asset Type", ASSET_TYPES, key=f"type_{i}")
        cost = st.number_input("Cost", min_value=0.0, value=10000.0, key=f"cost_{i}")
        salvage = st.number_input("Salvage Value", min_value=0.0, value=1000.0, key=f"salvage_{i}")
        start_date = st.date_input("In-Service Date", value=date.today(), key=f"date_{i}")
        default_life = GAAP_USEFUL_LIVES.get(gaap, {}).get(asset_type, 5)
        life = st.number_input("Useful Life (Years)", min_value=1, value=default_life, key=f"life_{i}")

        asset_inputs.append({
            "name": asset_name,
            "cost": cost,
            "salvage": salvage,
            "start_date": start_date,
            "useful_life": life
        })

# ------------------ Generate Schedule ------------------
if st.button("📊 Generate Monthly Schedules"):
    all_rows = []

    for asset in asset_inputs:
        row = straight_line_monthly_row(
            asset_name=asset["name"],
            cost=asset["cost"],
            salvage=asset["salvage"],
            start_date=asset["start_date"],
            useful_life=asset["useful_life"]
        )
        all_rows.append(row)

    df = pd.DataFrame(all_rows).set_index("Asset")
    df = df.fillna(0)

    st.success("✅ Monthly depreciation schedules generated!")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Summary")
    st.markdown(f"- **Total Assets:** {len(df)}")
    st.markdown(f"- **Total Depreciation (All Assets):** `${df['Total Depreciation'].sum():,.2f}`")

    csv = df.reset_index().to_csv(index=False).encode()
    st.download_button("⬇️ Download CSV", data=csv, file_name="monthly_wide_depreciation.csv")
