import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ------------------ GAAP Rules ------------------
GAAP_USEFUL_LIVES = {
    "US GAAP": {
        "Building": 40, "Vehicle": 5, "Machinery": 10, "Furniture": 7,
        "Computer Equipment": 5, "Office Equipment": 5, "Leasehold Improvements": 15,
        "Land Improvements": 20, "Software": 3, "Intangible Asset (e.g., Patent)": 10
    },
    "IFRS": {
        "Building": 30, "Vehicle": 7, "Machinery": 8, "Furniture": 5,
        "Computer Equipment": 4, "Office Equipment": 5, "Leasehold Improvements": 10,
        "Land Improvements": 20, "Software": 5, "Intangible Asset (e.g., Patent)": 8
    },
    "Indian GAAP": {
        "Building": 30, "Vehicle": 8, "Machinery": 10, "Furniture": 6,
        "Computer Equipment": 3, "Office Equipment": 5, "Leasehold Improvements": 10,
        "Land Improvements": 15, "Software": 6, "Intangible Asset (e.g., Patent)": 10
    }
}

def get_useful_life(gaap, asset_type):
    return GAAP_USEFUL_LIVES.get(gaap, {}).get(asset_type, None)

def straight_line_yearly(cost, salvage, life_years):
    annual = (cost - salvage) / life_years
    acc = 0
    schedule = []
    for year in range(1, life_years + 1):
        acc += annual
        book_value = cost - acc
        schedule.append({
            "Period": f"Year {year}",
            "Depreciation Expense": round(annual, 2),
            "Accumulated Depreciation": round(acc, 2),
            "Book Value": round(book_value, 2)
        })
    return schedule

def straight_line_monthly(cost, salvage, start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    monthly = (cost - salvage) / months
    acc = 0
    schedule = []
    current = start_date
    for _ in range(months):
        acc += monthly
        book_value = cost - acc
        schedule.append({
            "Period": current.strftime("%b %Y"),
            "Depreciation Expense": round(monthly, 2),
            "Accumulated Depreciation": round(acc, 2),
            "Book Value": round(book_value, 2)
        })
        current += relativedelta(months=1)
    return schedule

# ------------------ UI ------------------
st.set_page_config(page_title="📉 Depreciation Calculator", layout="centered")
st.title("📉 Depreciation Schedule Builder")

ASSET_TYPES = [
    "Building", "Vehicle", "Machinery", "Furniture", "Computer Equipment",
    "Office Equipment", "Leasehold Improvements", "Land Improvements",
    "Software", "Intangible Asset (e.g., Patent)"
]
GAAP_OPTIONS = ["US GAAP", "IFRS", "Indian GAAP", "UK GAAP", "Canadian GAAP", "Custom GAAP"]

DEPRECIATION_METHODS = [
    "Straight-Line", "Double Declining Balance", "Sum-of-the-Years’ Digits",
    "Units of Production", "MACRS (US Tax)", "Custom (Manual Rate)"
]

# Live GAAP + Asset selection
gaap = st.selectbox("📘 Select GAAP", GAAP_OPTIONS)
asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES)

# Reactive useful life
default_life = get_useful_life(gaap, asset_type)
useful_life = st.number_input(
    f"📅 Useful Life (Years) (Default: {default_life or 'N/A'})",
    min_value=1,
    value=default_life or 5
)

# Form for inputs
with st.form("depreciation_form"):
    method = st.selectbox("🧮 Depreciation Method", DEPRECIATION_METHODS)
    mode = st.radio("📆 Calculation Mode", ["Yearly", "Monthly"])
    cost = st.number_input("💰 Asset Cost", min_value=0.0, value=10000.0)
    salvage = st.number_input("♻️ Salvage Value", min_value=0.0, value=1000.0)
    start_date = st.date_input("📍 In-Service Date", value=date.today())

    end_date = None
    if mode == "Monthly":
        auto_end = st.checkbox("🧮 Auto-calculate End Date", value=True)
        if auto_end:
            end_date = start_date.replace(year=start_date.year + useful_life)
        else:
            end_date = st.date_input("🏁 Enter Custom End Date")

    submit = st.form_submit_button("📊 Generate Schedule")

# ------------------ Output ------------------
if submit:
    if method == "Straight-Line":
        if mode == "Monthly":
            if not end_date:
                st.error("Please provide an end date.")
            else:
                schedule = straight_line_monthly(cost, salvage, start_date, end_date)
        else:
            schedule = straight_line_yearly(cost, salvage, useful_life)
    else:
        st.warning(f"⚠️ '{method}' not yet implemented. Showing placeholder.")
        schedule = [{"Period": f"Year {i}", "Depreciation Expense": 0,
                     "Accumulated Depreciation": 0, "Book Value": cost}
                    for i in range(1, useful_life + 1)]

    df = pd.DataFrame(schedule)
    st.success("✅ Schedule generated successfully!")
    st.subheader("📋 Depreciation Schedule")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Summary")
    st.markdown(f"""
    - **Useful Life Used**: `{useful_life}` years  
    - **Total Depreciation**: `${df['Depreciation Expense'].sum():,.2f}`  
    - **Final Book Value**: `${df.iloc[-1]['Book Value']:,.2f}`  
    - **Total Periods**: `{len(df)}`  
    """)

    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Download CSV", data=csv, file_name="depreciation_schedule.csv")
