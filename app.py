import streamlit as st
import pandas as pd
from datetime import date, timedelta # timedelta not used, but often imported with date
import datetime # Required for MINYEAR, MAXYEAR
from dateutil.relativedelta import relativedelta

# ------------------ Depreciation Logic ------------------
def generate_all_potential_periods(start_date, useful_life_years, mode):
    """Generates all potential period start dates over the full useful life."""
    if mode == "Monthly":
        num_total_periods = useful_life_years * 12
        return [start_date + relativedelta(months=i) for i in range(num_total_periods)]
    else: # Yearly
        num_total_periods = useful_life_years
        return [start_date + relativedelta(years=i) for i in range(num_total_periods)]

def depreciation_row(asset_name, cost, salvage, start_date, useful_life_years, mode, provision_as_of_date):
    depreciable_base = cost - salvage
    if depreciable_base < 0:
        depreciable_base = 0 

    all_potential_periods = generate_all_potential_periods(start_date, useful_life_years, mode)
    num_total_potential_periods = len(all_potential_periods)

    if num_total_potential_periods == 0:
        return {"Asset": asset_name, "Total Depreciation": 0.00, "Cost": cost, "Salvage": salvage}, "N/A" # Added Cost/Salvage for NBV

    if mode == "Monthly":
        if useful_life_years * 12 == 0:
             dep_per_period_unrounded = 0.0
        else:
            dep_per_period_unrounded = depreciable_base / (useful_life_years * 12)
        potential_labels = [p.strftime("%b %Y") for p in all_potential_periods]
    else: # Yearly
        if useful_life_years == 0:
            dep_per_period_unrounded = 0.0
        else:
            dep_per_period_unrounded = depreciable_base / useful_life_years
        potential_labels = [p.strftime("%Y") for p in all_potential_periods]

    all_potential_dep_values = [round(dep_per_period_unrounded, 2)] * num_total_potential_periods
    
    if num_total_potential_periods > 0 and depreciable_base > 0:
        current_sum_full_life = sum(all_potential_dep_values)
        diff_full_life = round(depreciable_base - current_sum_full_life, 2)
        all_potential_dep_values[-1] += diff_full_life
        all_potential_dep_values[-1] = round(all_potential_dep_values[-1], 2)

    actual_labels_for_schedule = []
    actual_dep_values_for_schedule = []

    for i in range(num_total_potential_periods):
        period_start_date = all_potential_periods[i]
        # For monthly, depreciation is recognized at the end of the month.
        # For yearly, depreciation is recognized at the end of the year.
        # The 'period_start_date' marks the beginning of the period.
        # We consider depreciation for periods fully completed by or on the provision_as_of_date.
        # A simple way is to check if the *start* of the period is on or before the provision date.
        # More accurately, for monthly, if provision date is mid-month, that month's dep might be counted or not.
        # Current logic: if period starts on/before provision_as_of_date, it's included.
        # This means if provision date is Jan 15, Jan depreciation is included if schedule is monthly.
        if period_start_date <= provision_as_of_date:
            actual_labels_for_schedule.append(potential_labels[i])
            actual_dep_values_for_schedule.append(all_potential_dep_values[i])
        else:
            break 
    
    total_depreciation_up_to_provision = round(sum(actual_dep_values_for_schedule), 2)

    row_data = dict(zip(actual_labels_for_schedule, actual_dep_values_for_schedule))
    row_data["Asset"] = asset_name
    row_data["Total Depreciation"] = total_depreciation_up_to_provision
    # Pass through cost and salvage for Net Book Value summary, simplifies data flow
    row_data["Original Cost"] = cost 
    row_data["Original Salvage"] = salvage
    
    final_period_label_for_asset = actual_labels_for_schedule[-1] if actual_labels_for_schedule else "N/A"
    
    return row_data, final_period_label_for_asset

# ------------------ Constants ------------------
ASSET_TYPES = [
    "Building", "Vehicle", "Machinery", "Furniture", "Computer Equipment",
    "Office Equipment", "Leasehold Improvements", "Land Improvements",
    "Software", "Intangible Asset (e.g., Patent)"
]

GAAP_USEFUL_LIVES = {
    "US GAAP": {"Building": 40, "Vehicle": 5, "Machinery": 10, "Furniture": 7, "Computer Equipment": 5, "Office Equipment": 7, "Leasehold Improvements": 15, "Land Improvements": 15, "Software": 3, "Intangible Asset (e.g., Patent)": 10},
    "IFRS": {"Building": 30, "Vehicle": 7, "Machinery": 8, "Furniture": 5, "Computer Equipment": 4, "Office Equipment": 5, "Leasehold Improvements": 10, "Land Improvements": 10, "Software": 3, "Intangible Asset (e.g., Patent)": 10},
    "Indian GAAP": {"Building": 60, "Vehicle": 8, "Machinery": 15, "Furniture": 10, "Computer Equipment": 3, "Office Equipment": 5, "Leasehold Improvements": 10, "Land Improvements": 10, "Software": 6, "Intangible Asset (e.g., Patent)": 10} 
}

# Define truly wide min/max for date inputs
MIN_CALENDAR_DATE = datetime.date(datetime.MINYEAR, 1, 1)
MAX_CALENDAR_DATE = datetime.date(datetime.MAXYEAR, 12, 31)

# ------------------ UI ------------------
st.set_page_config(page_title="📊 Depreciation Calculator", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Depreciation Schedule Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Design and download <b>monthly or yearly straight-line depreciation schedules</b> for multiple assets with GAAP-suggested useful lives, calculated up to a specified provision date.</p>", unsafe_allow_html=True)
st.divider()

# Global settings
col_mode, col_provision_date = st.columns(2)
with col_mode:
    mode = st.radio("📆 Select Schedule Mode", ["Monthly", "Yearly"], horizontal=True, index=0)
with col_provision_date:
    calculated_default_provision = date.today() + relativedelta(years=50)
    default_provision_date = min(calculated_default_provision, MAX_CALENDAR_DATE) # Ensure default is within bounds

    provision_as_of_date = st.date_input(
        "📅 Depreciation Provision As Of",
        value=default_provision_date,
        min_value=MIN_CALENDAR_DATE,
        max_value=MAX_CALENDAR_DATE,
        help="Calculate depreciation up to this date. Schedules will be truncated accordingly."
    )

num_assets = st.number_input("🔢 Number of Assets", min_value=1, max_value=20, value=1, step=1)
asset_inputs_list = []

for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1}"):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(f"Asset Name", value=f"Asset_{i+1}", key=f"name_{i}")
            cost = st.number_input("💰 Cost", min_value=0.0, value=10000.0, step=100.0, format="%.2f", key=f"cost_{i}")
            
            # Default start_date should also be within the calendar limits, which date.today() is.
            start_date_val = date.today() # Default to today
            start_date = st.date_input(
                f"📍 In-Service Date",
                value=start_date_val,
                min_value=MIN_CALENDAR_DATE,
                max_value=MAX_CALENDAR_DATE, # Or provision_as_of_date if you want to enforce start <= provision
                key=f"date_{i}",
                help="The date the asset was placed in service."
            )
        with col2:
            gaap_standard = st.selectbox("📘 GAAP Standard", list(GAAP_USEFUL_LIVES.keys()), key=f"gaap_{i}")
            asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES, key=f"type_{i}")
            
            default_useful_life = GAAP_USEFUL_LIVES.get(gaap_standard, {}).get(asset_type, 5) 
            
            useful_life_years = st.number_input("📅 Useful Life (Years)", min_value=1, value=default_useful_life, step=1, key=f"life_{i}")
            salvage_value = st.number_input("♻️ Salvage Value", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=f"salvage_{i}")
            
            if salvage_value > cost:
                st.warning(f"For Asset #{i+1}: Salvage value (${salvage_value:,.2f}) is greater than cost (${cost:,.2f}). Depreciable base will be zero.")
            if start_date > provision_as_of_date:
                st.warning(f"For Asset #{i+1}: In-Service Date ({start_date}) is after Provision As Of Date ({provision_as_of_date}). No depreciation will be calculated for this asset in the schedule.")

        asset_inputs_list.append({
            "id": i, 
            "name": asset_name,
            "cost": cost,
            "salvage": max(0, min(salvage_value, cost)), 
            "start_date": start_date,
            "useful_life": useful_life_years,
        })

# ------------------ Generate Schedule ------------------
if st.button("📊 Generate Depreciation Schedule", type="primary"):
    all_asset_rows_for_df = [] # This will store dicts from depreciation_row
    summary_overview_data_list = [] 
    net_value_summary_data = []

    for asset_spec_data in asset_inputs_list:
        accumulated_depr_for_asset = 0.0 # Default for NBV if no dep
        final_period_label = "N/A"

        if asset_spec_data["start_date"] > provision_as_of_date:
            row_data_for_df = {
                "Asset": asset_spec_data["name"], 
                "Total Depreciation": 0.0,
                "Original Cost": asset_spec_data["cost"], # Needed for NBV
                "Original Salvage": asset_spec_data["salvage"] # For consistency
            }
            final_period_label = "N/A (Starts after Provision Date)"
            accumulated_depr_for_asset = 0.0
        else:
            row_data_for_df, final_period_label = depreciation_row(
                asset_name=asset_spec_data["name"],
                cost=asset_spec_data["cost"],
                salvage=asset_spec_data["salvage"],
                start_date=asset_spec_data["start_date"],
                useful_life_years=asset_spec_data["useful_life"],
                mode=mode,
                provision_as_of_date=provision_as_of_date
            )
            accumulated_depr_for_asset = row_data_for_df["Total Depreciation"]
        
        all_asset_rows_for_df.append(row_data_for_df)

        summary_overview_data_list.append({
            "Asset": asset_spec_data["name"],
            "Useful Life (Years)": asset_spec_data["useful_life"],
            "Total Depreciation (as of Provision Date)": accumulated_depr_for_asset,
            "Final Included Period": final_period_label
        })
        
        # Prepare data for Net Value Summary
        net_value_summary_data.append({
            "Asset": asset_spec_data["name"],
            "Cost": asset_spec_data["cost"],
            "Accumulated Depreciation": accumulated_depr_for_asset,
            "Net Book Value": asset_spec_data["cost"] - accumulated_depr_for_asset
        })


    if not all_asset_rows_for_df:
        st.warning("No asset data to generate schedule or all assets start after the provision date.")
    else:
        # Create DataFrame, remove helper columns before display
        depreciation_df_full_data = pd.DataFrame(all_asset_rows_for_df)
        
        # Columns for the main depreciation schedule display
        display_cols = ["Asset"] + \
                       [col for col in depreciation_df_full_data.columns if col not in ["Asset", "Total Depreciation", "Original Cost", "Original Salvage"]] + \
                       ["Total Depreciation"]
        
        depreciation_df_display = depreciation_df_full_data.reindex(columns=display_cols).copy()

        if "Asset" in depreciation_df_display.columns:
            depreciation_df_display = depreciation_df_display.set_index("Asset")
        
        period_cols = [col for col in depreciation_df_display.columns if col != "Total Depreciation"]
        
        if period_cols:
            sort_fmt = "%b %Y" if mode == "Monthly" else "%Y"
            try:
                valid_period_cols = [p for p in period_cols if isinstance(p, str)]
                # Using pd.to_datetime with errors='coerce' to handle potential non-date strings robustly
                sorted_period_cols = sorted(valid_period_cols, key=lambda d: pd.to_datetime(d, format=sort_fmt, errors='coerce'))
                sorted_period_cols = [p for p in sorted_period_cols if pd.notna(p)] 
            except Exception as e:
                st.error(f"Error sorting period columns: {e}. Columns may appear unsorted.")
                sorted_period_cols = period_cols 
        else:
            sorted_period_cols = []

        final_columns_order = sorted_period_cols + (["Total Depreciation"] if "Total Depreciation" in depreciation_df_display.columns else [])
        if final_columns_order:
            depreciation_df_display = depreciation_df_display[final_columns_order]

        st.markdown(f"<h3 style='text-align: center;'>📋 Full Depreciation Schedule (up to {provision_as_of_date.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
        st.dataframe(depreciation_df_display, use_container_width=True)

        st.markdown("<h3 style='text-align: center;'>📈 Asset Summary Overview</h3>", unsafe_allow_html=True)
        summary_overview_df = pd.DataFrame(summary_overview_data_list)
        if not summary_overview_df.empty:
            summary_overview_df = summary_overview_df[["Asset", "Useful Life (Years)", "Total Depreciation (as of Provision Date)", "Final Included Period"]]
            st.dataframe(summary_overview_df.style.format({"Total Depreciation (as of Provision Date)": "${:,.2f}"}), use_container_width=True, hide_index=True)

        st.markdown("<h3 style='text-align: center;'>🧮 Grand Totals (up to Provision Date)</h3>", unsafe_allow_html=True)
        total_num_assets_in_schedule = len(depreciation_df_display)
        grand_total_depreciation_value = depreciation_df_display['Total Depreciation'].sum() if 'Total Depreciation' in depreciation_df_display.columns and not depreciation_df_display.empty else 0.0
        
        col_total1, col_total2 = st.columns(2)
        with col_total1:
            st.metric(label="Total Assets in Schedule", value=total_num_assets_in_schedule)
        with col_total2:
            st.metric(label="Grand Total Accumulated Depreciation", value=f"${grand_total_depreciation_value:,.2f}")

        # ------------------ Net Value Summary Section ------------------
        st.markdown(f"<h3 style='text-align: center;'>💼 Net Value Summary (as of {provision_as_of_date.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
        if net_value_summary_data:
            net_value_df = pd.DataFrame(net_value_summary_data)
            
            if not net_value_df.empty:
                total_row_data = {
                    "Asset": "Grand Total",
                    "Cost": net_value_df["Cost"].sum(),
                    "Accumulated Depreciation": net_value_df["Accumulated Depreciation"].sum(),
                    "Net Book Value": net_value_df["Net Book Value"].sum()
                }
                total_row_df = pd.DataFrame([total_row_data])
                net_value_df = pd.concat([net_value_df, total_row_df], ignore_index=True)

            st.dataframe(net_value_df.style.format({
                "Cost": "${:,.2f}",
                "Accumulated Depreciation": "${:,.2f}",
                "Net Book Value": "${:,.2f}"
            }), use_container_width=True, hide_index=True)
        else:
            st.info("No data for Net Value Summary.")

        # ------------------ Export Option ------------------
        if not depreciation_df_display.empty:
            csv_export_data = depreciation_df_display.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Full Schedule as CSV",
                data=csv_export_data,
                file_name=f"{mode.lower()}_depreciation_schedule_as_of_{provision_as_of_date.strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
else:
    st.info("Configure your assets above and click 'Generate Depreciation Schedule'.")
