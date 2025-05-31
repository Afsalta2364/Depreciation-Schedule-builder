import streamlit as st
import pandas as pd
from datetime import date
import datetime # Required for MINYEAR, MAXYEAR
from dateutil.relativedelta import relativedelta

# ------------------ Depreciation Logic (largely unchanged) ------------------
def generate_all_potential_periods(start_date, useful_life_years, mode):
    if mode == "Monthly":
        num_total_periods = useful_life_years * 12
        return [start_date + relativedelta(months=i) for i in range(num_total_periods)]
    else: # Yearly
        num_total_periods = useful_life_years
        return [start_date + relativedelta(years=i) for i in range(num_total_periods)]

def depreciation_row(asset_name, cost, salvage, start_date, useful_life_years, mode, provision_as_of_date):
    depreciable_base = cost - salvage
    if depreciable_base < 0:
        depreciable_base = 0.0

    all_potential_periods = generate_all_potential_periods(start_date, useful_life_years, mode)
    num_total_potential_periods = len(all_potential_periods)

    if num_total_potential_periods == 0:
        return {
            "Asset": asset_name, "Total Depreciation": 0.00,
            "Original Cost": cost, "Original Salvage": salvage
        }, "N/A (No periods)"

    if mode == "Monthly":
        dep_per_period_unrounded = depreciable_base / (useful_life_years * 12) if (useful_life_years * 12) > 0 else 0
        potential_labels = [p.strftime("%b %Y") for p in all_potential_periods]
    else: # Yearly
        dep_per_period_unrounded = depreciable_base / useful_life_years if useful_life_years > 0 else 0
        potential_labels = [p.strftime("%Y") for p in all_potential_periods]

    all_potential_dep_values = [round(dep_per_period_unrounded, 2)] * num_total_potential_periods
    
    if num_total_potential_periods > 0 and depreciable_base > 0:
        current_sum_full_life = sum(all_potential_dep_values)
        diff_full_life = round(depreciable_base - current_sum_full_life, 2)
        all_potential_dep_values[-1] += diff_full_life
        all_potential_dep_values[-1] = round(all_potential_dep_values[-1], 2)

    actual_labels_for_schedule, actual_dep_values_for_schedule = [], []
    for i in range(num_total_potential_periods):
        period_date = all_potential_periods[i]
        if period_date <= provision_as_of_date:
            actual_labels_for_schedule.append(potential_labels[i])
            actual_dep_values_for_schedule.append(all_potential_dep_values[i])
        else:
            break 
    
    total_depreciation_up_to_provision = round(sum(actual_dep_values_for_schedule), 2)
    row_data_for_schedule_df = dict(zip(actual_labels_for_schedule, actual_dep_values_for_schedule))
    row_data_for_schedule_df.update({
        "Asset": asset_name, "Total Depreciation": total_depreciation_up_to_provision,
        "Original Cost": cost, "Original Salvage": salvage
    })
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
MIN_CALENDAR_DATE = datetime.date(datetime.MINYEAR, 1, 1)
MAX_CALENDAR_DATE = datetime.date(datetime.MAXYEAR, 12, 31)
CURRENCIES = {"USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "JPY (¥)": "¥", "INR (₹)": "₹"}

# ------------------ UI ------------------
st.set_page_config(page_title="📊 Depreciation Calculator", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Depreciation Schedule Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Design and download <b>monthly or yearly straight-line depreciation schedules</b> for multiple assets with GAAP-suggested useful lives, calculated up to a specified provision date.</p>", unsafe_allow_html=True)
st.divider()

# --- Global Configuration ---
st.markdown("## ⚙️ Global Configuration")
with st.container(border=True):
    gc_col1, gc_col2, gc_col3 = st.columns(3)
    with gc_col1:
        mode = st.radio("📆 Schedule Mode", ["Monthly", "Yearly"], horizontal=True, index=0)
    with gc_col2:
        provision_as_of_date_input = st.date_input(
            "📅 Depreciation Provision As Of",
            value=date.today(), # Default to current date
            min_value=MIN_CALENDAR_DATE,
            max_value=MAX_CALENDAR_DATE,
            help="Calculate depreciation up to this date. Schedules will be truncated accordingly."
        )
    with gc_col3:
        selected_currency_label = st.selectbox("🪙 Currency", list(CURRENCIES.keys()), index=0)
        currency_symbol = CURRENCIES[selected_currency_label]
st.divider()

# --- Asset Inputs ---
st.markdown("## ➕ Add Assets")
num_assets = st.number_input("🔢 Number of Assets", min_value=1, max_value=25, value=1, step=1, label_visibility="collapsed") # Label is in markdown above

asset_input_data_list = []
for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1} Details"):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(f"Asset Name", value=f"Asset_{i+1}", key=f"name_{i}")
            cost = st.number_input(f"💰 Cost ({currency_symbol})", min_value=0.0, value=10000.0, step=100.0, format="%.2f", key=f"cost_{i}")
            start_date_input = st.date_input(
                f"📍 In-Service Date", value=date.today(), min_value=MIN_CALENDAR_DATE,
                max_value=MAX_CALENDAR_DATE, key=f"date_{i}",
                help="The date the asset was placed in service."
            )
        with col2:
            gaap_standard = st.selectbox("📘 GAAP Standard", list(GAAP_USEFUL_LIVES.keys()), key=f"gaap_{i}")
            asset_type = st.selectbox("🏗️ Asset Type", ASSET_TYPES, key=f"type_{i}")
            default_useful_life = GAAP_USEFUL_LIVES.get(gaap_standard, {}).get(asset_type, 5)
            useful_life_years_input = st.number_input("📅 Useful Life (Years)", min_value=1, value=default_useful_life, step=1, key=f"life_{i}")
            salvage_value_input = st.number_input(f"♻️ Salvage Value ({currency_symbol})", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=f"salvage_{i}")
            
            if salvage_value_input > cost:
                st.warning(f"Salvage value ({currency_symbol}{salvage_value_input:,.2f}) exceeds cost ({currency_symbol}{cost:,.2f}). Depreciable base will be {currency_symbol}0.00.")
            if start_date_input > provision_as_of_date_input:
                st.warning(f"In-Service Date ({start_date_input}) is after Provision Date ({provision_as_of_date_input}). No depreciation will be calculated.")

        asset_input_data_list.append({
            "name": asset_name, "cost": cost, "salvage": max(0.0, min(salvage_value_input, cost)),
            "start_date": start_date_input, "useful_life": useful_life_years_input,
        })
st.divider()

# --- Generate Schedule Button & Logic ---
if st.button("📊 Generate Depreciation Schedule", type="primary", use_container_width=True):
    processed_asset_data_rows = []
    asset_summary_overview_list = []
    net_value_summary_list = []

    for asset_spec in asset_input_data_list:
        accumulated_depr_for_nbv = 0.0
        final_period_label_for_summary = "N/A"

        if asset_spec["start_date"] > provision_as_of_date_input:
            row_data_from_calc = {
                "Asset": asset_spec["name"], "Total Depreciation": 0.0,
                "Original Cost": asset_spec["cost"], "Original Salvage": asset_spec["salvage"]
            }
            final_period_label_for_summary = "N/A (Starts after Provision Date)"
        else:
            row_data_from_calc, final_period_label_for_summary = depreciation_row(
                asset_name=asset_spec["name"], cost=asset_spec["cost"], salvage=asset_spec["salvage"],
                start_date=asset_spec["start_date"], useful_life_years=asset_spec["useful_life"],
                mode=mode, provision_as_of_date=provision_as_of_date_input
            )
            accumulated_depr_for_nbv = row_data_from_calc["Total Depreciation"]
        
        processed_asset_data_rows.append(row_data_from_calc)
        asset_summary_overview_list.append({
            "Asset": asset_spec["name"], "Useful Life (Years)": asset_spec["useful_life"],
            "Accumulated Depreciation": accumulated_depr_for_nbv,
            "Final Included Period": final_period_label_for_summary
        })
        net_value_summary_list.append({
            "Asset": asset_spec["name"], "Cost": asset_spec["cost"],
            "Accumulated Depreciation": accumulated_depr_for_nbv,
            "Net Book Value": asset_spec["cost"] - accumulated_depr_for_nbv
        })

    # --- Display Results in Tabs ---
    if not processed_asset_data_rows:
        st.warning("⚠️ No asset data processed. Please configure assets or check dates.")
    else:
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>🔍 Calculation Results</h2>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs([
            "📋 Full Depreciation Schedule", 
            "📈 Asset Summaries", 
            "💼 Net Value & Grand Totals"
        ])

        currency_format_string = f"{currency_symbol}{{:, .2f}}"
        
        with tab1:
            st.markdown(f"<h3 style='text-align: center;'>Full Depreciation Schedule (up to {provision_as_of_date_input.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
            
            main_schedule_df_full = pd.DataFrame(processed_asset_data_rows)
            
            schedule_display_cols = ["Asset"] + \
                                    [col for col in main_schedule_df_full.columns if col not in ["Asset", "Total Depreciation", "Original Cost", "Original Salvage"]] + \
                                    ["Total Depreciation"]
            main_schedule_df_display = main_schedule_df_full.reindex(columns=schedule_display_cols).copy()

            if main_schedule_df_display.empty or "Asset" not in main_schedule_df_display.columns:
                st.info("No data available to construct the depreciation schedule.")
            else:
                main_schedule_df_display = main_schedule_df_display.set_index("Asset")

                period_cols_in_schedule = [col for col in main_schedule_df_display.columns if col != "Total Depreciation"]
                sorted_period_cols = []

                if period_cols_in_schedule:
                    sort_fmt = "%b %Y" if mode == "Monthly" else "%Y"
                    valid_date_strings = [p for p in period_cols_in_schedule if isinstance(p, str)]
                    try:
                        datetime_objects = [pd.to_datetime(d, format=sort_fmt, errors='coerce') for d in valid_date_strings]
                        sorted_pairs = sorted(
                            [(s, dt) for s, dt in zip(valid_date_strings, datetime_objects) if pd.notna(dt)],
                            key=lambda pair: pair[1]
                        )
                        sorted_period_cols = [pair[0] for pair in sorted_pairs]
                        sorted_period_cols = [col for col in sorted_period_cols if col in main_schedule_df_display.columns]
                    except Exception as e:
                        st.warning(f"Could not sort period columns due to: {e}. Displaying unsorted.")
                        sorted_period_cols = period_cols_in_schedule

                final_schedule_columns_order = sorted_period_cols + (["Total Depreciation"] if "Total Depreciation" in main_schedule_df_display.columns else [])
                
                if final_schedule_columns_order and not main_schedule_df_display.empty:
                    main_schedule_df_display = main_schedule_df_display[final_schedule_columns_order]

                    cols_to_format_currency = [col for col in main_schedule_df_display.columns if col == "Total Depreciation" or col in sorted_period_cols]
                    
                    for col in cols_to_format_currency:
                        if col in main_schedule_df_display.columns:
                            main_schedule_df_display[col] = pd.to_numeric(main_schedule_df_display[col], errors='coerce').fillna(0.0)
                    
                    style_dict_schedule = {
                        col: currency_format_string 
                        for col in cols_to_format_currency
                        if col in main_schedule_df_display.columns
                    }
                    
                    if not main_schedule_df_display.empty:
                        try:
                            st.dataframe(
                                main_schedule_df_display.style.format(style_dict_schedule),
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"⚠️ Error applying styles to the schedule DataFrame: {e}. Displaying unstyled data.")
                            st.dataframe(main_schedule_df_display, use_container_width=True)
                    else:
                        st.info("The schedule is empty after attempting to order columns.")

                    st.markdown("---")
                    st.markdown("<h4 style='text-align: center;'>Schedule Totals</h4>", unsafe_allow_html=True)
                    total_assets_in_schedule_display = len(main_schedule_df_display)
                    grand_total_accum_depr_schedule = main_schedule_df_display['Total Depreciation'].sum() if 'Total Depreciation' in main_schedule_df_display.columns and not main_schedule_df_display.empty else 0.0
                    
                    sched_total_col1, sched_total_col2 = st.columns(2)
                    with sched_total_col1:
                        st.metric(label="Assets in Schedule", value=total_assets_in_schedule_display)
                    with sched_total_col2:
                        st.metric(label="Total Depreciation (Schedule)", value=f"{currency_symbol}{grand_total_accum_depr_schedule:,.2f}")
                    
                    if not main_schedule_df_display.empty:
                        csv_export_data = main_schedule_df_display.reset_index().to_csv(index=False, float_format='%.2f').encode('utf-8')
                        st.download_button(
                            label="⬇️ Download Schedule as CSV", data=csv_export_data,
                            file_name=f"{mode.lower()}_dep_schedule_{provision_as_of_date_input.strftime('%Y%m%d')}.csv",
                            mime="text/csv", use_container_width=True
                        )
                elif main_schedule_df_display.empty and not processed_asset_data_rows:
                    st.info("No asset data was configured to display in the schedule.")
                else: 
                    st.info("No depreciation periods to display based on the provision date and asset start dates for the configured assets.")

        with tab2: # Asset Summaries
            st.markdown("<h3 style='text-align: center;'>Asset Summary Overview</h3>", unsafe_allow_html=True)
            summary_overview_df = pd.DataFrame(asset_summary_overview_list)
            if not summary_overview_df.empty:
                summary_overview_df = summary_overview_df[[
                    "Asset", "Useful Life (Years)", 
                    "Accumulated Depreciation", "Final Included Period"
                ]]
                
                # Ensure 'Accumulated Depreciation' is numeric before styling
                if "Accumulated Depreciation" in summary_overview_df.columns:
                    summary_overview_df["Accumulated Depreciation"] = pd.to_numeric(
                        summary_overview_df["Accumulated Depreciation"], errors='coerce'
                    ).fillna(0.0)

                try:
                    st.dataframe(
                        summary_overview_df.style.format({"Accumulated Depreciation": currency_format_string}), 
                        use_container_width=True, 
                        hide_index=True
                    )
                except Exception as e:
                    st.error(f"⚠️ Error applying styles to the Asset Summary DataFrame: {e}. Displaying unstyled data.")
                    st.dataframe(summary_overview_df, use_container_width=True, hide_index=True) # Fallback
            else:
                st.info("No data for Asset Summary Overview.")

        with tab3: # Net Value & Grand Totals
            st.markdown(f"<h3 style='text-align: center;'>Net Value Summary (as of {provision_as_of_date_input.strftime('%d %b %Y')})</h3>", unsafe_allow_html=True)
            if net_value_summary_list:
                net_value_df = pd.DataFrame(net_value_summary_list)
                if not net_value_df.empty:
                    # Ensure numeric types for sum and styling
                    for col_name in ["Cost", "Accumulated Depreciation", "Net Book Value"]:
                        if col_name in net_value_df.columns:
                             net_value_df[col_name] = pd.to_numeric(net_value_df[col_name], errors='coerce').fillna(0.0)
                    
                    nbv_total_row_data = {
                        "Asset": "Grand Total", "Cost": net_value_df["Cost"].sum(),
                        "Accumulated Depreciation": net_value_df["Accumulated Depreciation"].sum(),
                        "Net Book Value": net_value_df["Net Book Value"].sum()
                    }
                    nbv_total_row_df = pd.DataFrame([nbv_total_row_data])
                    net_value_df_with_total = pd.concat([net_value_df, nbv_total_row_df], ignore_index=True)

                    try:
                        st.dataframe(net_value_df_with_total.style.format({
                            "Cost": currency_format_string,
                            "Accumulated Depreciation": currency_format_string,
                            "Net Book Value": currency_format_string
                        }), use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.error(f"⚠️ Error applying styles to the Net Value Summary DataFrame: {e}. Displaying unstyled data.")
                        st.dataframe(net_value_df_with_total, use_container_width=True, hide_index=True) # Fallback
            else:
                st.info("No data for Net Value Summary.")
else:
    st.info("ℹ️ Configure your assets above and click 'Generate Depreciation Schedule'.")
