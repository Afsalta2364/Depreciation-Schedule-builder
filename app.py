import streamlit as st
import pandas as pd
from datetime import date
import datetime # Required for MINYEAR, MAXYEAR
from dateutil.relativedelta import relativedelta

# ------------------ Custom CSS Styling ------------------
def apply_custom_styling():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Header Styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 300;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(90deg, #f8f9ff 0%, #e8ecff 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .section-header h2 {
        color: #2d3748;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Configuration Container */
    .config-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    
    /* Asset Cards */
    .asset-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .asset-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metrics */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Warning/Info boxes */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f7fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Input fields */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Download button special styling */
    .download-btn {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .main-header p {
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------ Depreciation Logic (unchanged) ------------------
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
st.set_page_config(
    page_title="📊 Depreciation Calculator", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styling
apply_custom_styling()

# Enhanced Header
st.markdown("""
    <div class="main-header">
        <h1>📊 Depreciation Schedule Builder</h1>
        <p>Design and download <b>monthly or yearly straight-line depreciation schedules</b> for multiple assets with GAAP-suggested useful lives</p>
    </div>
""", unsafe_allow_html=True)

# --- Global Configuration ---
st.markdown("""
    <div class="section-header">
        <h2>⚙️ Global Configuration</h2>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="config-container">', unsafe_allow_html=True)
    gc_col1, gc_col2, gc_col3 = st.columns(3)
    
    with gc_col1:
        st.markdown("**📆 Schedule Mode**")
        mode = st.radio("Schedule Mode", ["Monthly", "Yearly"], horizontal=True, index=0, label_visibility="collapsed")
    
    with gc_col2:
        st.markdown("**📅 Depreciation Provision As Of**")
        provision_as_of_date_input = st.date_input(
            "Provision Date",
            value=date.today(),
            min_value=MIN_CALENDAR_DATE,
            max_value=MAX_CALENDAR_DATE,
            help="Calculate depreciation up to this date. Schedules will be truncated accordingly.",
            label_visibility="collapsed"
        )
    
    with gc_col3:
        st.markdown("**🪙 Currency**")
        selected_currency_label = st.selectbox("Currency", list(CURRENCIES.keys()), index=0, label_visibility="collapsed")
        currency_symbol = CURRENCIES[selected_currency_label]
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Asset Inputs ---
st.markdown("""
    <div class="section-header">
        <h2>➕ Asset Configuration</h2>
    </div>
""", unsafe_allow_html=True)

# Number of assets selector with better styling
col_assets, col_spacer = st.columns([1, 3])
with col_assets:
    num_assets = st.number_input("🔢 Number of Assets", min_value=1, max_value=25, value=1, step=1)

asset_input_data_list = []
for i in range(num_assets):
    with st.expander(f"📁 **Asset #{i + 1}** Configuration", expanded=True if i == 0 else False):
        st.markdown('<div class="asset-card">', unsafe_allow_html=True)
        
        # Asset name prominently displayed
        asset_name = st.text_input(
            f"**Asset Name**", 
            value=f"Asset_{i+1}", 
            key=f"name_{i}",
            placeholder="Enter a descriptive asset name"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**💰 Financial Details**")
            cost = st.number_input(
                f"Cost ({currency_symbol})", 
                min_value=0.0, 
                value=10000.0, 
                step=100.0, 
                format="%.2f", 
                key=f"cost_{i}",
                help="The original purchase price of the asset"
            )
            salvage_value_input = st.number_input(
                f"Salvage Value ({currency_symbol})", 
                min_value=0.0, 
                value=1000.0, 
                step=100.0, 
                format="%.2f", 
                key=f"salvage_{i}",
                help="Expected residual value at end of useful life"
            )
            start_date_input = st.date_input(
                f"📍 In-Service Date", 
                value=date.today(), 
                min_value=MIN_CALENDAR_DATE,
                max_value=MAX_CALENDAR_DATE, 
                key=f"date_{i}",
                help="The date the asset was placed in service"
            )
        
        with col2:
            st.markdown("**📘 Depreciation Parameters**")
            gaap_standard = st.selectbox(
                "GAAP Standard", 
                list(GAAP_USEFUL_LIVES.keys()), 
                key=f"gaap_{i}",
                help="Select the accounting standard for default useful life suggestions"
            )
            asset_type = st.selectbox(
                "🏗️ Asset Type", 
                ASSET_TYPES, 
                key=f"type_{i}",
                help="Asset category determines default useful life"
            )
            default_useful_life = GAAP_USEFUL_LIVES.get(gaap_standard, {}).get(asset_type, 5)
            useful_life_years_input = st.number_input(
                "📅 Useful Life (Years)", 
                min_value=1, 
                value=default_useful_life, 
                step=1, 
                key=f"life_{i}",
                help=f"Suggested: {default_useful_life} years for {asset_type} under {gaap_standard}"
            )
        
        # Validation warnings with better styling
        if salvage_value_input > cost:
            st.error(f"⚠️ **Salvage value** ({currency_symbol}{salvage_value_input:,.2f}) **exceeds cost** ({currency_symbol}{cost:,.2f}). Depreciable base will be {currency_symbol}0.00.")
        
        if start_date_input > provision_as_of_date_input:
            st.warning(f"⚠️ **In-Service Date** ({start_date_input}) is **after Provision Date** ({provision_as_of_date_input}). No depreciation will be calculated.")
        
        # Calculated depreciable base display
        depreciable_base = max(0, cost - min(salvage_value_input, cost))
        st.info(f"💡 **Depreciable Base**: {currency_symbol}{depreciable_base:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)

        asset_input_data_list.append({
            "name": asset_name, "cost": cost, "salvage": max(0.0, min(salvage_value_input, cost)),
            "start_date": start_date_input, "useful_life": useful_life_years_input,
        })

# --- Generate Schedule Button & Logic ---
st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
generate_clicked = st.button("🚀 Generate Depreciation Schedule", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if generate_clicked:
    with st.spinner('Calculating depreciation schedules...'):
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
            st.error("⚠️ No asset data processed. Please configure assets or check dates.")
        else:
            st.markdown("""
                <div class="section-header">
                    <h2>📊 Calculation Results</h2>
                </div>
            """, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs([
                "📋 **Full Depreciation Schedule**", 
                "📈 **Asset Summaries**", 
                "💼 **Net Value & Totals**"
            ])

            currency_format_string = f"{currency_symbol}{{:, .2f}}"
            
            with tab1:
                st.markdown(f"""
                    <div style="text-align: center; margin: 1rem 0;">
                        <h3>📋 Full Depreciation Schedule</h3>
                        <p style="color: #666;">Calculated up to {provision_as_of_date_input.strftime('%B %d, %Y')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                main_schedule_df_full = pd.DataFrame(processed_asset_data_rows)
                
                schedule_display_cols = ["Asset"] + \
                                        [col for col in main_schedule_df_full.columns if col not in ["Asset", "Total Depreciation", "Original Cost", "Original Salvage"]] + \
                                        ["Total Depreciation"]
                main_schedule_df_display = main_schedule_df_full.reindex(columns=schedule_display_cols).copy()

                if main_schedule_df_display.empty or "Asset" not in main_schedule_df_display.columns:
                    st.info("📝 No data available to construct the depreciation schedule.")
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
                                    use_container_width=True,
                                    height=400
                                )
                            except Exception as e:
                                st.error(f"⚠️ Error applying styles to the schedule DataFrame: {e}. Displaying unstyled data.")
                                st.dataframe(main_schedule_df_display, use_container_width=True)
                        else:
                            st.info("The schedule is empty after attempting to order columns.")

                        # Enhanced totals section
                        st.markdown("---")
                        st.markdown("### 📊 Schedule Summary")
                        
                        total_assets_in_schedule_display = len(main_schedule_df_display)
                        grand_total_accum_depr_schedule = main_schedule_df_display['Total Depreciation'].sum() if 'Total Depreciation' in main_schedule_df_display.columns and not main_schedule_df_display.empty else 0.0
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                label="📋 Assets in Schedule", 
                                value=total_assets_in_schedule_display,
                                help="Number of assets included in the schedule"
                            )
                        with col2:
                            st.metric(
                                label="💰 Total Depreciation", 
                                value=f"{currency_symbol}{grand_total_accum_depr_schedule:,.2f}",
                                help="Sum of all accumulated depreciation"
                            )
                        with col3:
                            avg_depreciation = grand_total_accum_depr_schedule / total_assets_in_schedule_display if total_assets_in_schedule_display > 0 else 0
                            st.metric(
                                label="📊 Average per Asset", 
                                value=f"{currency_symbol}{avg_depreciation:,.2f}",
                                help="Average depreciation per asset"
                            )
                        with col4:
                            st.metric(
                                label="📅 Schedule Mode", 
                                value=mode,
                                help="Current calculation frequency"
                            )
                        
                        if not main_schedule_df_display.empty:
                            csv_export_data = main_schedule_df_display.reset_index().to_csv(index=False, float_format='%.2f').encode('utf-8')
                            st.download_button(
                                label="⬇️ Download Schedule as CSV", 
                                data=csv_export_data,
                                file_name=f"{mode.lower()}_depreciation_schedule_{provision_as_of_date_input.strftime('%Y%m%d')}.csv",
                                mime="text/csv", 
                                use_container_width=True,
                                type="secondary"
                            )
                    elif main_schedule_df_display.empty and not processed_asset_data_rows:
                        st.info("📝 No asset data was configured to display in the schedule.")
                    else: 
                        st.info("📅 No depreciation periods to display based on the provision date and asset start dates for the configured assets.")

            with tab2: # Asset Summaries
                st.markdown("### 📈 Asset Summary Overview")
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
                            hide_index=True,
                            height=300
                        )
                    except Exception as e:
                        st.error(f"⚠️ Error applying styles to the Asset Summary DataFrame: {e}. Displaying unstyled data.")
                        st.dataframe(summary_overview_df, use_container_width=True, hide_index=True)
                else:
                    st.info("📊 No data for Asset Summary Overview.")

            with tab3: # Net Value & Grand Totals
                st.markdown(f"### 💼 Net Book Value Summary")
                st.markdown(f"*As of {provision_as_of_date_input.strftime('%B %d, %Y')}*")
                
                if net_value_summary_list:
                    net_value_df = pd.DataFrame(net_value_summary_list)
                    if not net_value_df.empty:
                        # Ensure numeric types for sum and styling
                        for col_name in ["Cost", "Accumulated Depreciation", "Net Book Value"]:
                            if col_name in net_value_df.columns:
                                 net_value_df[col_name] = pd.to_numeric(net_value_df[col_name], errors='coerce').fillna(0.0)
                        
                        nbv_total_row_data = {
                            "Asset": "**GRAND TOTAL**", "Cost": net_value_df["Cost"].sum(),
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
                            }), use_container_width=True, hide_index=True, height=300)
                        except Exception as e:
                            st.error(f"⚠️ Error applying styles to the Net Value Summary DataFrame: {e}. Displaying unstyled data.")
                            st.dataframe(net_value_df_with_total, use_container_width=True, hide_index=True)
                        
                        # Additional insights
                        st.markdown("---")
                        st.markdown("#### 💡 Financial Insights")
                        
                        total_cost = net_value_df["Cost"].sum()
                        total_accumulated = net_value_df["Accumulated Depreciation"].sum()
                        total_nbv = net_value_df["Net Book Value"].sum()
                        depreciation_percentage = (total_accumulated / total_cost * 100) if total_cost > 0 else 0
                        
                        insights_col1, insights_col2 = st.columns(2)
                        with insights_col1:
                            st.metric(
                                label="📊 Depreciation Ratio", 
                                value=f"{depreciation_percentage:.1f}%",
                                help="Percentage of original cost that has been depreciated"
                            )
                        with insights_col2:
                            st.metric(
                                label="📈 Remaining Value Ratio", 
                                value=f"{100-depreciation_percentage:.1f}%",
                                help="Percentage of original cost remaining as book value"
                            )
                else:
                    st.info("💼 No data for Net Value Summary.")
else:
    # Enhanced welcome message when no calculation has been run
    st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%); border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: #4a5568; margin-bottom: 1rem;">🎯 Ready to Calculate Depreciation?</h3>
            <p style="color: #718096; font-size: 1.1rem; margin-bottom: 1.5rem;">
                Configure your assets above and click <strong>'Generate Depreciation Schedule'</strong> to see:
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                    <div style="font-weight: 600; color: #4a5568;">Detailed Schedules</div>
                    <div style="color: #718096; font-size: 0.9rem;">Period-by-period breakdown</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-weight: 600; color: #4a5568;">Asset Summaries</div>
                    <div style="color: #718096; font-size: 0.9rem;">Key metrics & insights</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💼</div>
                    <div style="font-weight: 600; color: #4a5568;">Net Book Values</div>
                    <div style="color: #718096; font-size: 0.9rem;">Current asset valuations</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem; padding: 1rem;">
        <p>📊 <strong>Depreciation Schedule Builder</strong> | Straight-line depreciation calculator with GAAP compliance</p>
        <p style="margin-top: 0.5rem;">Built with ❤️ using Streamlit | Supports US GAAP, IFRS, and Indian GAAP standards</p>
    </div>
""", unsafe_allow_html=True)
