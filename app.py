import streamlit as st
import pandas as pd
from datetime import date, timedelta
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
    if depreciable_base < 0: # Should ideally be handled by salvage <= cost validation in UI
        depreciable_base = 0 

    all_potential_periods = generate_all_potential_periods(start_date, useful_life_years, mode)
    num_total_potential_periods = len(all_potential_periods)

    if num_total_potential_periods == 0: # e.g. useful_life_years is 0, though UI prevents < 1
        return {"Asset": asset_name, "Total Depreciation": 0}, "N/A"

    if mode == "Monthly":
        if useful_life_years * 12 == 0: # Should not happen with useful_life_years >= 1
             dep_per_period_unrounded = 0
        else:
            dep_per_period_unrounded = depreciable_base / (useful_life_years * 12)
        potential_labels = [p.strftime("%b %Y") for p in all_potential_periods]
    else: # Yearly
        if useful_life_years == 0: # Should not happen
            dep_per_period_unrounded = 0
        else:
            dep_per_period_unrounded = depreciable_base / useful_life_years
        potential_labels = [p.strftime("%Y") for p in all_potential_periods]

    # Calculate depreciation for all potential periods, with plug for full life
    all_potential_dep_values = [round(dep_per_period_unrounded, 2)] * num_total_potential_periods
    
    if num_total_potential_periods > 0 and depreciable_base > 0: # Ensure plug makes sense
        current_sum_full_life = sum(all_potential_dep_values)
        diff_full_life = round(depreciable_base - current_sum_full_life, 2)
        all_potential_dep_values[-1] += diff_full_life
        all_potential_dep_values[-1] = round(all_potential_dep_values[-1], 2) # Ensure last val is also rounded

    # Filter periods and values based on provision_as_of_date
    actual_labels_for_schedule = []
    actual_dep_values_for_schedule = []

    for i in range(num_total_potential_periods):
        period_start_date = all_potential_periods[i]
        if period_start_date <= provision_as_of_date:
            actual_labels_for_schedule.append(potential_labels[i])
            actual_dep_values_for_schedule.append(all_potential_dep_values[i])
        else:
            # Stop if period starts after provision date
            break 
    
    total_depreciation_up_to_provision = round(sum(actual_dep_values_for_schedule), 2)

    row_data = dict(zip(actual_labels_for_schedule, actual_dep_values_for_schedule))
    row_data["Asset"] = asset_name
    row_data["Total Depreciation"] = total_depreciation_up_to_provision
    
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
} # Expanded slightly

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
    # Default provision date far in the future to show full schedule by default
    default_provision_date = date.today() + relativedelta(years=50)
    provision_as_of_date = st.date_input("📅 Depreciation Provision As Of", value=default_provision_date, help="Calculate depreciation up to this date. Schedules will be truncated accordingly.")

num_assets = st.number_input("🔢 Number of Assets", min_value=1, max_value=20, value=1, step=1)
asset_inputs_list = []

for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1}"):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(f"Asset Name", value=f"Asset_{i+1}", key=f"name_{i}")
            cost = st.number_input("💰 Cost", min_value=0.0, value=10000.0, step=100.0, format="%.2f", key=f"cost_{i}")
            start_date = st.date_input("📍 In-Service Date", value=date.today(), key=f"date_{i}", help="The date the asset was placed in service.")
        with col2:
            gaap_standard = st.selectbox("📘 GAAP Standard", list(GAAP_USEFUL_LIVES.keys()), key=f"gaap_{i}")
            asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES, key=f"type_{i}")
            
            default_useful_life = GAAP_USEFUL_LIVES.get(gaap_standard, {}).get(asset_type, 5) 
            
            useful_life_years = st.number_input("📅 Useful Life (Years)", min_value=1, value=default_useful_life, step=1, key=f"life_{i}")
            salvage_value = st.number_input("♻️ Salvage Value", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=f"salvage_{i}")
            
            if salvage_value > cost:
                st.warning(f"For Asset #{i+1}: Salvage value (${salvage_value:,.2f}) is greater than cost (${cost:,.2f}). Depreciable base will be zero.")
            if start_date > provision_as_of_date:
                st.warning(f"For Asset #{i+1}: In-Service Date ({start_date}) is after Provision As Of Date ({provision_as_of_date}). No depreciation will be calculated for this asset.")

        asset_inputs_list.append({
            "id": i, # Unique ID for internal mapping if names are duplicated
            "name": asset_name,
            "cost": cost,
            "salvage": max(0, min(salvage_value, cost)), # Ensure salvage <= cost for calc, depreciable base non-negative
            "start_date": start_date,
            "useful_life": useful_life_years,
        })

# ------------------ Generate Schedule ------------------
if st.button("📊 Generate Depreciation Schedule", type="primary"):
    all_asset_rows_for_df = []
    summary_overview_data_list = [] # Renamed for clarity

    for asset_spec_data in asset_inputs_list:
        # Skip calculation if asset starts after provision date for efficiency and clarity
        if asset_spec_data["start_date"] > provision_as_of_date:
            row_data_for_df = {
                "Asset": asset_spec_data["name"], 
                "Total Depreciation": 0.0
            }
            final_period_label = "N/A (Starts after Provision Date)"
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
        all_asset_rows_for_df.append(row_data_for_df)

        summary_overview_data_list.append({
            "Asset": asset_spec_data["name"],
            "Useful Life (Years)": asset_spec_data["useful_life"],
            "Total Depreciation (as of Provision Date)": row_data_for_df["Total Depreciation"],
            "Final Included Period": final_period_label
        })

    if not all_asset_rows_for_df:
        st.warning("No asset data to generate schedule or all assets start after the provision date.")
    else:
        depreciation_df = pd.DataFrame(all_asset_rows_for_df)
        
        if "Asset" in depreciation_df.columns:
            cols = ["Asset"] + [col for col in depreciation_df.columns if col not in ["Asset", "Total Depreciation"]] + ["Total Depreciation"]
            depreciation_df = depreciation_df.reindex(columns=cols) # Ensure order
            depreciation_df = depreciation_df.set_index("Asset")
        
        period_cols = [col for col in depreciation_df.columns if col != "Total Depreciation"]
        
        if period_cols: # Only sort if there are period columns
            sort_fmt = "%b %Y" if mode == "Monthly" else "%Y"
            try:
                # Handle cases where a column might not be a valid date string (e.g. if empty schedule for an asset)
                valid_period_cols = [p for p in period_cols if isinstance(p, str)]
                sorted_period_cols = sorted(valid_period_cols, key=lambda d: pd.to_datetime(d, format=sort_fmt, errors='coerce'))
                # Filter out any NaT that might result from coerce
                sorted_period_cols = [p for p in sorted_period_cols if pd.notna(p)] 
            except Exception as e: # Broad exception for safety in sorting
                st.error(f"Error sorting period columns: {e}. Columns may appear unsorted.")
                sorted_period_cols = period_cols 
        else:
            sorted_period_cols = []


        final_columns_order = sorted_period_cols + (["Total Depreciation"] if "Total Depreciation" in depreciation_df.columns else [])
        if final_columns_order: # Check if there are any columns to display
            depreciation_df = depreciation_df[final_columns_order]

        st.markdown(f"<h3 style='text-align: center;'>📋 Full Depreciation Schedule (up to {provision_as_of_date.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
        st.dataframe(depreciation_df, use_container_width=True)

        st.markdown("<h3 style='text-align: center;'>📈 Asset Summary Overview</h3>", unsafe_allow_html=True)
        summary_overview_df = pd.DataFrame(summary_overview_data_list)
        if not summary_overview_df.empty:
            summary_overview_df = summary_overview_df[["Asset", "Useful Life (Years)", "Total Depreciation (as of Provision Date)", "Final Included Period"]]
            st.dataframe(summary_overview_df, use_container_width=True, hide_index=True)

        st.markdown("<h3 style='text-align: center;'>🧮 Grand Totals (up to Provision Date)</h3>", unsafe_allow_html=True)
        total_num_assets_in_schedule = len(depreciation_df)
        grand_total_depreciation_value = depreciation_df['Total Depreciation'].sum() if 'Total Depreciation' in depreciation_df.columns else 0.0
        
        col_total1, col_total2 = st.columns(2)
        with col_total1:
            st.metric(label="Total Assets in Schedule", value=total_num_assets_in_schedule)
        with col_total2:
            st.metric(label="Grand Total Accumulated Depreciation", value=f"${grand_total_depreciation_value:,.2f}")

        # ------------------ New Net Value Summary Section ------------------
        st.markdown(f"<h3 style='text-align: center;'>💼 Net Value Summary (as of {provision_as_of_date.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
        net_value_summary_data = []
        for i, asset_input_spec in enumerate(asset_inputs_list):
            asset_name = asset_input_spec["name"]
            original_cost = asset_input_spec["cost"]
            
            # Find the accumulated depreciation for this asset from the generated rows
            # Using the original index 'i' from asset_inputs_list to map to all_asset_rows_for_df
            # This assumes all_asset_rows_for_df maintains the same order as asset_inputs_list
            accumulated_depr_for_asset = all_asset_rows_for_df[i]["Total Depreciation"]
            
            nbv = original_cost - accumulated_depr_for_asset
            
            net_value_summary_data.append({
                "Asset": asset_name,
                "Cost": original_cost,
                "Accumulated Depreciation": accumulated_depr_for_asset,
                "Net Book Value": nbv
            })
        
        if net_value_summary_data:
            net_value_df = pd.DataFrame(net_value_summary_data)
            
            # Add Grand Total row
            if not net_value_df.empty:
                total_row_data = {
                    "Asset": "Grand Total",
                    "Cost": net_value_df["Cost"].sum(),
                    "Accumulated Depreciation": net_value_df["Accumulated Depreciation"].sum(),
                    "Net Book Value": net_value_df["Net Book Value"].sum()
                }
                # Convert to DataFrame to ensure dtypes match for concat, then append
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
        if not depreciation_df.empty:
            csv_export_data = depreciation_df.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Full Schedule as CSV",
                data=csv_export_data,
                file_name=f"{mode.lower()}_depreciation_schedule_as_of_{provision_as_of_date.strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
else:
    st.info("Configure your assets above and click 'Generate Depreciation Schedule'.")
