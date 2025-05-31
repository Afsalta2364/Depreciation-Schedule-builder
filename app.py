import streamlit as st
import pandas as pd
from datetime import date
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
    if depreciable_base < 0: # Should be caught by UI validation, but defensive
        depreciable_base = 0.0

    # Generate all periods for the asset's full life
    all_potential_periods = generate_all_potential_periods(start_date, useful_life_years, mode)
    num_total_potential_periods = len(all_potential_periods)

    # Handle case where useful life might be too short (e.g. <1 year for yearly)
    # or if start_date implies no periods can be generated (though UI enforces useful_life >=1)
    if num_total_potential_periods == 0:
        return {
            "Asset": asset_name,
            "Total Depreciation": 0.00,
            "Original Cost": cost, # Pass through for NBV summary
            "Original Salvage": salvage # Pass through for NBV summary
        }, "N/A (No periods)"

    # Determine base depreciation per period over full life
    if mode == "Monthly":
        # useful_life_years >= 1, so useful_life_years * 12 >= 12 (no division by zero)
        dep_per_period_unrounded = depreciable_base / (useful_life_years * 12)
        potential_labels = [p.strftime("%b %Y") for p in all_potential_periods]
    else: # Yearly
        # useful_life_years >= 1 (no division by zero)
        dep_per_period_unrounded = depreciable_base / useful_life_years
        potential_labels = [p.strftime("%Y") for p in all_potential_periods]

    # Calculate depreciation for all potential periods, applying a plug for the last period of full life
    all_potential_dep_values = [round(dep_per_period_unrounded, 2)] * num_total_potential_periods
    
    # Adjust the very last period of the full useful life to ensure total dep = depreciable_base
    if num_total_potential_periods > 0 and depreciable_base > 0:
        current_sum_full_life = sum(all_potential_dep_values)
        diff_full_life = round(depreciable_base - current_sum_full_life, 2)
        all_potential_dep_values[-1] += diff_full_life
        all_potential_dep_values[-1] = round(all_potential_dep_values[-1], 2) # Ensure last value is also rounded

    # Now, filter these periods and values based on the provision_as_of_date
    actual_labels_for_schedule = []
    actual_dep_values_for_schedule = []

    for i in range(num_total_potential_periods):
        period_date = all_potential_periods[i] # This is the start date of the period
        
        # Include the period if its start date is on or before the provision_as_of_date.
        # Depreciation is recognized for periods that have effectively occurred by the provision_as_of_date.
        if period_date <= provision_as_of_date:
            actual_labels_for_schedule.append(potential_labels[i])
            actual_dep_values_for_schedule.append(all_potential_dep_values[i])
        else:
            # Stop including periods once they start after the provision date
            break 
    
    total_depreciation_up_to_provision = round(sum(actual_dep_values_for_schedule), 2)

    # Prepare the dictionary for the main schedule DataFrame
    row_data_for_schedule_df = dict(zip(actual_labels_for_schedule, actual_dep_values_for_schedule))
    row_data_for_schedule_df["Asset"] = asset_name
    row_data_for_schedule_df["Total Depreciation"] = total_depreciation_up_to_provision
    
    # Also include original cost and salvage in this dict to simplify data flow for NBV summary
    row_data_for_schedule_df["Original Cost"] = cost 
    row_data_for_schedule_df["Original Salvage"] = salvage
    
    final_included_period_label = actual_labels_for_schedule[-1] if actual_labels_for_schedule else "N/A"
    
    return row_data_for_schedule_df, final_included_period_label

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

# Define truly wide min/max for date inputs using Python's datetime capabilities
MIN_CALENDAR_DATE = datetime.date(datetime.MINYEAR, 1, 1)
MAX_CALENDAR_DATE = datetime.date(datetime.MAXYEAR, 12, 31)

# ------------------ UI ------------------
st.set_page_config(page_title="📊 Depreciation Calculator", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Depreciation Schedule Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Design and download <b>monthly or yearly straight-line depreciation schedules</b> for multiple assets with GAAP-suggested useful lives, calculated up to a specified provision date.</p>", unsafe_allow_html=True)
st.divider()

# --- Global Settings ---
col_mode, col_provision_date_ui = st.columns(2) # Renamed to avoid conflict
with col_mode:
    mode = st.radio("📆 Select Schedule Mode", ["Monthly", "Yearly"], horizontal=True, index=0)
with col_provision_date_ui:
    # Default provision date far in the future to show full schedule by default, clamped to max calendar date
    calculated_default_provision = date.today() + relativedelta(years=50)
    default_provision_date_val = min(calculated_default_provision, MAX_CALENDAR_DATE)

    provision_as_of_date_input = st.date_input(
        "📅 Depreciation Provision As Of",
        value=default_provision_date_val,
        min_value=MIN_CALENDAR_DATE,
        max_value=MAX_CALENDAR_DATE,
        help="Calculate depreciation up to this date. Schedules will be truncated accordingly."
    )

# --- Asset Inputs ---
num_assets = st.number_input("🔢 Number of Assets", min_value=1, max_value=25, value=1, step=1) # Max increased
asset_input_data_list = [] # Stores dicts of user inputs for each asset

for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1}"):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(f"Asset Name", value=f"Asset_{i+1}", key=f"name_{i}")
            cost = st.number_input("💰 Cost", min_value=0.0, value=10000.0, step=100.0, format="%.2f", key=f"cost_{i}")
            
            # Default start_date to today, ensuring it's within calendar limits (which it will be)
            default_start_date_val = date.today()
            start_date_input = st.date_input(
                f"📍 In-Service Date",
                value=default_start_date_val,
                min_value=MIN_CALENDAR_DATE,
                max_value=MAX_CALENDAR_DATE, # Can also be clamped by provision_as_of_date_input if desired
                key=f"date_{i}",
                help="The date the asset was placed in service."
            )
        with col2:
            gaap_standard = st.selectbox("📘 GAAP Standard", list(GAAP_USEFUL_LIVES.keys()), key=f"gaap_{i}")
            asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES, key=f"type_{i}")
            
            default_useful_life = GAAP_USEFUL_LIVES.get(gaap_standard, {}).get(asset_type, 5) # Default to 5 if type not found
            
            useful_life_years_input = st.number_input("📅 Useful Life (Years)", min_value=1, value=default_useful_life, step=1, key=f"life_{i}")
            salvage_value_input = st.number_input("♻️ Salvage Value", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=f"salvage_{i}")
            
            # UI Warnings
            if salvage_value_input > cost:
                st.warning(f"For Asset #{i+1}: Salvage value (${salvage_value_input:,.2f}) is greater than cost (${cost:,.2f}). Depreciable base will be $0.00.")
            if start_date_input > provision_as_of_date_input:
                st.warning(f"For Asset #{i+1}: In-Service Date ({start_date_input}) is after Provision As Of Date ({provision_as_of_date_input}). No depreciation will be calculated for this asset in the schedule.")

        asset_input_data_list.append({
            "id": i, # Unique ID for potential internal mapping if names are duplicated
            "name": asset_name,
            "cost": cost,
            # Ensure salvage value is not greater than cost for calculation, effectively capping it.
            "salvage": max(0.0, min(salvage_value_input, cost)), 
            "start_date": start_date_input,
            "useful_life": useful_life_years_input,
        })

# ------------------ Generate Schedule Button & Logic ------------------
if st.button("📊 Generate Depreciation Schedule", type="primary"):
    processed_asset_data_rows = [] # Stores the dicts returned by depreciation_row (includes dep values, cost, salvage)
    asset_summary_overview_list = [] 
    net_value_summary_list = []

    for asset_spec in asset_input_data_list:
        accumulated_depr_for_nbv = 0.0
        final_period_label_for_summary = "N/A"

        # If asset starts after provision date, no depreciation is calculated for the schedule
        if asset_spec["start_date"] > provision_as_of_date_input:
            # Still need a row structure for DataFrames, with 0 depreciation
            row_data_from_calc = {
                "Asset": asset_spec["name"], 
                "Total Depreciation": 0.0,
                "Original Cost": asset_spec["cost"], 
                "Original Salvage": asset_spec["salvage"] 
                # No period columns will be generated for this asset
            }
            final_period_label_for_summary = "N/A (Starts after Provision Date)"
            accumulated_depr_for_nbv = 0.0
        else:
            # Calculate depreciation
            row_data_from_calc, final_period_label_for_summary = depreciation_row(
                asset_name=asset_spec["name"],
                cost=asset_spec["cost"],
                salvage=asset_spec["salvage"],
                start_date=asset_spec["start_date"],
                useful_life_years=asset_spec["useful_life"],
                mode=mode,
                provision_as_of_date=provision_as_of_date_input
            )
            accumulated_depr_for_nbv = row_data_from_calc["Total Depreciation"]
        
        processed_asset_data_rows.append(row_data_from_calc)

        # For Asset Summary Overview table
        asset_summary_overview_list.append({
            "Asset": asset_spec["name"],
            "Useful Life (Years)": asset_spec["useful_life"],
            "Accumulated Depreciation (as of Provision Date)": accumulated_depr_for_nbv,
            "Final Included Period": final_period_label_for_summary
        })
        
        # For Net Value Summary table
        net_value_summary_list.append({
            "Asset": asset_spec["name"],
            "Cost": asset_spec["cost"], # Original cost from input
            "Accumulated Depreciation": accumulated_depr_for_nbv,
            "Net Book Value": asset_spec["cost"] - accumulated_depr_for_nbv
        })

    # --- Display Results ---
    if not processed_asset_data_rows:
        st.warning("No asset data processed. Please configure assets or check dates.")
    else:
        # Create DataFrame for the main depreciation schedule, then select display columns
        # This df contains all data, including Original Cost/Salvage which we'll drop for display
        main_schedule_df_full = pd.DataFrame(processed_asset_data_rows)
        
        # Columns to actually show in the main depreciation schedule table
        # Exclude 'Original Cost' and 'Original Salvage' helper columns from this specific display
        schedule_display_cols = ["Asset"] + \
                                [col for col in main_schedule_df_full.columns if col not in ["Asset", "Total Depreciation", "Original Cost", "Original Salvage"]] + \
                                ["Total Depreciation"]
        
        # Create a copy for display manipulation
        main_schedule_df_display = main_schedule_df_full.reindex(columns=schedule_display_cols).copy()

        if "Asset" in main_schedule_df_display.columns:
            main_schedule_df_display = main_schedule_df_display.set_index("Asset")
        
        # Sort period columns chronologically
        period_cols_in_schedule = [col for col in main_schedule_df_display.columns if col != "Total Depreciation"]
        
        if period_cols_in_schedule: # Only sort if there are period columns (e.g. not if all assets start after provision)
            sort_fmt = "%b %Y" if mode == "Monthly" else "%Y"
            try:
                # Handle potential non-date strings robustly if any somehow slip through
                valid_date_strings = [p for p in period_cols_in_schedule if isinstance(p, str)]
                sorted_period_cols = sorted(
                    valid_date_strings, 
                    key=lambda d: pd.to_datetime(d, format=sort_fmt, errors='coerce') # errors='coerce' turns unparseable to NaT
                )
                # Filter out any NaT that might result from coercion
                sorted_period_cols = [p for p in sorted_period_cols if pd.notna(pd.to_datetime(p, format=sort_fmt, errors='coerce'))]
            except Exception as e: # Broad exception for safety in sorting, though 'coerce' should handle most
                st.error(f"Error sorting period columns: {e}. Columns may appear unsorted.")
                sorted_period_cols = period_cols_in_schedule # Fallback to unsorted
        else:
            sorted_period_cols = []

        # Reconstruct DataFrame with sorted period columns and "Total Depreciation" at the end
        final_schedule_columns_order = sorted_period_cols + \
                                     (["Total Depreciation"] if "Total Depreciation" in main_schedule_df_display.columns else [])
        
        if final_schedule_columns_order: # Ensure there are columns to display
            main_schedule_df_display = main_schedule_df_display[final_schedule_columns_order]

        # 1. Full Depreciation Schedule
        st.markdown(f"<h3 style='text-align: center;'>📋 Full Depreciation Schedule (up to {provision_as_of_date_input.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
        if main_schedule_df_display.empty and not period_cols_in_schedule: # Special case: assets exist but no dep periods
             st.info("No depreciation periods to display based on the provision date and asset start dates.")
        else:
            st.dataframe(main_schedule_df_display.style.format(precision=2), use_container_width=True)


        # 2. Asset Summary Overview
        st.markdown("<h3 style='text-align: center;'>📈 Asset Summary Overview</h3>", unsafe_allow_html=True)
        summary_overview_df = pd.DataFrame(asset_summary_overview_list)
        if not summary_overview_df.empty:
            summary_overview_df = summary_overview_df[[
                "Asset", "Useful Life (Years)", 
                "Accumulated Depreciation (as of Provision Date)", 
                "Final Included Period"
            ]]
            st.dataframe(summary_overview_df.style.format({"Accumulated Depreciation (as of Provision Date)": "${:,.2f}"}), 
                         use_container_width=True, hide_index=True)
        else:
            st.info("No data for Asset Summary Overview.")

        # 3. Grand Totals for Schedule
        st.markdown("<h3 style='text-align: center;'>🧮 Schedule Grand Totals (up to Provision Date)</h3>", unsafe_allow_html=True)
        total_assets_in_schedule_display = len(main_schedule_df_display)
        # Sum 'Total Depreciation' from the display DF to reflect what's shown
        grand_total_accum_depr_schedule = main_schedule_df_display['Total Depreciation'].sum() if 'Total Depreciation' in main_schedule_df_display.columns and not main_schedule_df_display.empty else 0.0
        
        col_total1, col_total2 = st.columns(2)
        with col_total1:
            st.metric(label="Total Assets in Displayed Schedule", value=total_assets_in_schedule_display)
        with col_total2:
            st.metric(label="Grand Total Accumulated Depreciation (Schedule)", value=f"${grand_total_accum_depr_schedule:,.2f}")

        # 4. Net Value Summary
        st.markdown(f"<h3 style='text-align: center;'>💼 Net Value Summary (as of {provision_as_of_date_input.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
        if net_value_summary_list:
            net_value_df = pd.DataFrame(net_value_summary_list)
            
            if not net_value_df.empty:
                # Add Grand Total row for Net Value Summary
                nbv_total_row_data = {
                    "Asset": "<strong>Grand Total</strong>", # Using HTML for bold
                    "Cost": net_value_df["Cost"].sum(),
                    "Accumulated Depreciation": net_value_df["Accumulated Depreciation"].sum(),
                    "Net Book Value": net_value_df["Net Book Value"].sum()
                }
                nbv_total_row_df = pd.DataFrame([nbv_total_row_data])
                net_value_df_with_total = pd.concat([net_value_df, nbv_total_row_df], ignore_index=True)

            st.dataframe(net_value_df_with_total.style.format({
                "Cost": "${:,.2f}",
                "Accumulated Depreciation": "${:,.2f}",
                "Net Book Value": "${:,.2f}"
            }), use_container_width=True, hide_index=True, 
               column_config={"Asset": st.column_config.TextColumn(label="Asset", help="Asset Name or Grand Total")}) # Allows HTML in 'Asset'
        else:
            st.info("No data for Net Value Summary.")

        # 5. Export Option for the main schedule
        if not main_schedule_df_display.empty:
            csv_export_data = main_schedule_df_display.reset_index().to_csv(index=False, float_format='%.2f').encode('utf-8')
            st.download_button(
                label="⬇️ Download Full Schedule as CSV",
                data=csv_export_data,
                file_name=f"{mode.lower()}_depreciation_schedule_as_of_{provision_as_of_date_input.strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
else:
    st.info("ℹ️ Configure your assets above and click 'Generate Depreciation Schedule'.")
