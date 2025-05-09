import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ------------------ GAAP Logic ------------------
GAAP_USEFUL_LIVES = {
    "US GAAP": {
        "Building": 40,
        "Vehicle": 5,
        "Machinery": 10,
        "Furniture": 7
    },
    "IFRS": {
        "Building": 30,
        "Vehicle": 7,
        "Machinery": 8,
        "Furniture": 5
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

# ------------------ Streamlit App ------------------
st.title("📉 Depreciation Schedule Builder")

gaap = st.selectbox("Select GAAP", ["US GAAP", "IFRS"])
asset_type = st.selectbox("Asset Type", ["Building", "Vehicle", "Machinery", "Furniture"])
method = st.selectbox("Depreciation Method", ["Straight-Line"])
mode = st.radio("Calculation Mode", ["Yearly", "Monthly"])

cost = st.number_input("Asset Cost", min_value=0.0, value=10000.0)
salvage = st.number_input("Salvage Value", min_value=0.0, value=1000.0)

default_life = get_useful_life(gaap, asset_type)
life_years = st.number_input("Useful Life (Years)", min_value=1, value=default_life or 5)

start_date = st.date_input("Asset In-Service Date", value=date.today())
if mode == "Monthly":
    end_date = st.date_input("End of Depreciation Period", value=start_date.replace(year=start_date.year + life_years))

if st.button("Generate Depreciation Schedule"):
    if method == "Straight-Line":
        if mode == "Monthly":
            schedule = straight_line_monthly(cost, salvage, start_date, end_date)
        else:
            schedule = straight_line_yearly(cost, salvage, life_years)
    else:
        st.error("Only Straight-Line is currently supported.")
        schedule = []

    df = pd.DataFrame(schedule)
    st.subheader("📋 Depreciation Schedule")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv, file_name="depreciation_schedule.csv")
