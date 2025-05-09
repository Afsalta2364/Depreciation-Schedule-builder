import streamlit as st
import pandas as pd
from datetime import date
import sys, os

# Ensure module is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from depreciation_methods import straight_line_monthly, straight_line_yearly
from gaap_rules import get_useful_life

st.title("📉 Depreciation Schedule Builder")

# Input Section
gaap = st.selectbox("Select GAAP", ["US GAAP", "IFRS"])
asset_type = st.selectbox("Asset Type", ["Building", "Vehicle", "Machinery", "Furniture"])
method = st.selectbox("Depreciation Method", ["Straight-Line"])
calculation_mode = st.radio("Calculation Mode", ["Yearly", "Monthly"])

cost = st.number_input("Asset Cost", min_value=0.0, value=10000.0)
salvage = st.number_input("Salvage Value", min_value=0.0, value=1000.0)

default_life = get_useful_life(gaap, asset_type)
life_years = st.number_input("Useful Life (Years)", min_value=1, value=default_life or 5)

start_date = st.date_input("Asset In-Service Date", value=date.today())

if calculation_mode == "Monthly":
    end_date = st.date_input("End of Depreciation Period", value=start_date.replace(year=start_date.year + life_years))

# Generate button
if st.button("Generate Depreciation Schedule"):
    if method == "Straight-Line":
        if calculation_mode == "Monthly":
            schedule = straight_line_monthly(cost, salvage, start_date, end_date)
        else:
            schedule = straight_line_yearly(cost, salvage, life_years)
    else:
        st.error("Only Straight-Line is implemented.")
        schedule = []

    df = pd.DataFrame(schedule)
    st.subheader("📋 Depreciation Schedule")
    st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv, file_name="depreciation_schedule.csv", mime="text/csv")
