import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ------------------ GAAP Logic ------------------
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

# ------------------ Depreciation Logic ------------------
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

# ------------------ UI Constants ------------------
ASSET_TYPES = [
    "Building", "Vehicle", "Machinery", "Furniture", "Computer Equipment",
    "Office Equipment", "Leasehold Improvements", "Land Improvements",
    "Software", "Intangible Asset (e.g., Patent)"
]

GAAP_OPTIONS = ["US GAAP", "IFRS", "Indian GAAP", "UK GAAP", "Canadian GAAP", "Custom GAAP"]

DEPRECIATION_METHODS = [
    "Straight-Line", "Double Declining Balance", "150% Declining Balance",
    "Sum-of-the-Years’ Digits", "Units of Production", "MACRS (US Tax)", "Custom (Manual Rate)"
]

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="📉 Depreciation Calculator", layout="centered")
st.title("📉 Depreciation Schedule Builder")
st.markdown("This tool helps you calculate **monthly or yearly depreciation schedules** based on various GAAP standards.")

with st.form("depreciation_form"):
    col1, col2 = st.columns(2)
    with col1:
        gaap = st.selectbox("📘 Select GAAP", GAAP_OPTIONS, help="Choose the accounting standard to apply.")
        asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES)
        method = st.selectbox("🧮 Depreciation Method", DEPRECIATION_METHODS)
    with col2:
        mode = st.radio("📆 Calculation Mode", ["Yearly", "Monthly"])
        cost = st.number_input("💰 Asset Cost", min_value=0.0, value=10000.0)
        salvage = st.number_input("♻️ Salvage Value", min_value=0.0, value=1000.0)

    default_life = get_useful_life(gaap, asset_type)
    life_years = st.number_input("📅 Useful Life (Years)", min_value=1, value=default_life or 5)

    start_date = st.date_input("📍 In-Service Date", value=date.today())
    if mode == "Monthly":
        end_date = st.date_input("🏁 End Date", value=start_date.replace(year=start_date.year + life_years))

    submit = st.form_submit_button("📊 Generate Schedule")

if submit:
    if method == "Straight-Line":
        if mode == "Monthly":
            schedule = straight_line_monthly(cost, salvage, start_date, end_date)
        else:
            schedule = straight_line_yearly(cost, salvage, life_years)
    else:
        st.warning(f"⚠️ The method '{method}' is not implemented yet.")
        schedule = [{"Period": f"Year {i}", "Depreciation Expense": 0,
                     "Accumulated Depreciation": 0, "Book Value": cost}
                    for i in range(1, life_years + 1)]

    df = pd.DataFrame(schedule)
    st.success("✅ Schedule generated successfully!")
    st.subheader("📋 Depreciation Schedule")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Summary")
    total_dep = df["Depreciation Expense"].sum()
    final_book = df.iloc[-1]["Book Value"]
    st.markdown(f"""
    - **Total Depreciation**: `${total_dep:,.2f}`  
    - **Final Book Value**: `${final_book:,.2f}`  
    - **Total Periods**: `{len(df)}`  
    """)

    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Download CSV", data=csv, file_name="depreciation_schedule.csv")
