import streamlit as st
import pandas as pd
from datetime import date
from gaap_rules import get_useful_life
from depreciation-methods import straight_line_monthly, straight_line_yearly

st.title("Depreciation Calculator")

# Step 1: Inputs
gaap = st.selectbox("Select GAAP", ["US GAAP", "IFRS"])
asset_type = st.selectbox("Asset Type", ["Building", "Vehicle", "Machinery", "Furniture"])
method = st.selectbox("Depreciation Method", ["Straight-Line"])
calc_type = st.radio("Calculation Type", ["Yearly", "Monthly"])

cost = st.number_input("Asset Cost", min_value=0.0)
salvage = st.number_input("Salvage Value", min_value=0.0)

default_life = get_useful_life(gaap, asset_type)
life_input = st.number_input("Useful Life (Years)", value=default_life if default_life else 5, min_value=1)

start_date = st.date_input("In-Service Date", value=date.today())

if calc_type == "Monthly":
    end_date = st.date_input("End of Depreciation Period", value=start_date.replace(year=start_date.year + life_input))

# Step 2: Run
if st.button("Generate Schedule"):
    if method == "Straight-Line":
        if calc_type == "Monthly":
            schedule = straight_line_monthly(cost, salvage, start_date, end_date)
        else:
            schedule = straight_line_yearly(cost, salvage, life_input)
    else:
        schedule = []

    df = pd.DataFrame(schedule)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv, file_name="depreciation_schedule.csv", mime="text/csv")
