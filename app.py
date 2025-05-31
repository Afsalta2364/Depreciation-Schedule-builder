import streamlit as st
import pandas as pd
from datetime import date
import datetime # Required for MINYEAR, MAXYEAR
from dateutil.relativedelta import relativedelta

# ------------------ Custom CSS Styling (Theme-Aware) ------------------
def apply_custom_styling():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    body, .main {
        font-family: 'Inter', sans-serif;
        background-color: var(--background-color); /* Streamlit theme variable */
        color: var(--text-color); /* Streamlit theme variable */
    }
    
    /* Custom Header Styling (Branding Element - kept specific colors) */
    .app-main-header { /* Renamed for clarity */
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; /* Ensure text is white on this background */
        padding: 2rem 1rem;
        border-radius: 12px; /* Consistent border-radius */
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
    }
    
    .app-main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .app-main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 300;
    }
    
    /* Section Headers (Theme-Aware) */
    .app-section-header h2 {
        color: var(--text-color);
        font-size: 1.6rem;
        font-weight: 600;
        margin: 2.5rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        border-bottom: 2px solid var(--secondary-background-color); 
        padding-bottom: 0.75rem;
    }
    
    /* Expander Styling (Leverage Streamlit's theme as much as possible) */
    .stExpander {
        border-radius: 10px !important;
        border: 1px solid var(--secondary-background-color) !important; /* Theme-aware border */
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); /* Softer shadow */
        margin-bottom: 1.5rem;
        overflow: hidden;
    }
    .stExpander header {
        background-color: var(--secondary-background-color) !important; /* Lighter header */
        border-bottom: 1px solid var(--border-color, rgba(0,0,0,0.05)) !important; /* Subtle separator */
    }
    .stExpander header button {
        font-weight: 600 !important;
        font-size: 1.05rem !important; /* Slightly smaller for better fit */
        color: var(--text-color) !important;
        padding: 0.75rem 1rem !important;
    }
    .stExpander > div > div[data-testid="stVerticalBlock"] > div { /* Content padding */
        padding: 1.25rem;
    }

    /* Buttons (Primary Button - Branding) */
    .stButton > button[kind="primary"] { /* Target only primary buttons */
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 8px; /* Consistent border-radius */
        padding: 0.65rem 1.75rem;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Download Button (Secondary Style - Theme-Aware Green) */
    .stDownloadButton > button { 
        background: #38a169 !important; /* Solid, adaptable green */
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.25rem !important; 
        font-weight: 500 !important; /* Slightly less bold */
        box-shadow: 0 3px 10px rgba(56, 161, 105, 0.25) !important;
        transition: all 0.2s ease-in-out;
    }
    .stDownloadButton > button:hover {
         transform: translateY(-1px);
         box-shadow: 0 5px 15px rgba(56, 161, 105, 0.35) !important;
    }
    
    /* Metric Styling (Using Streamlit's test IDs for better targeting) */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color, rgba(0,0,0,0.05));
        border-radius: 10px;
        padding: 1rem; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        height: 100%;
    }
    div[data-testid="stMetric"] > label[data-testid="stMetricLabel"] {
        font-weight: 500;
        color: var(--text-color);
        opacity: 0.8; /* Slightly subdued label */
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.7rem; 
        font-weight: 600; /* Bolder value */
        color: var(--primary-color); /* Use primary color for metric value */
    }
    
    /* Alerts (Theme-Aware) */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        border-width: 0px !important; 
        border-left-width: 4px !important; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        padding: 0.9rem 1.1rem !important;
        font-size: 0.95rem;
    }
    /* Specific alert type colors using theme variables as much as possible */
    div[data-testid="stAlert"][role="alert"] { /* Warning (yellowish) */
        background-color: var(--warning-background-color, #fffbeb) !important; /* Fallback color */
        border-left-color: var(--warning-color, #fec829) !important;
        color: var(--warning-text-color, #784d06) !important;
    }
    div[data-testid="stAlert"][role="status"] { /* Info (blueish) */
         background-color: var(--info-background-color, #e0f2fe) !important;
         border-left-color: var(--info-color, #3b82f6) !important;
         color: var(--info-text-color, #0c4a6e) !important;
    }
     div[data-testid="stAlert"][data-testid="stNotificationErrorMessage"] { /* Error (reddish) */
         background-color: var(--error-background-color, #fee2e2) !important;
         border-left-color: var(--error-color, #ef4444) !important;
         color: var(--error-text-color, #7f1d1d) !important;
    }
    
    /* Tabs (Theme-Aware) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px; 
        background-color: transparent; /* Let page background show */
        padding: 0.5rem 0; /* Reduced padding, only bottom border */
        border-radius: 0; /* Remove tab list radius */
        border-bottom: 2px solid var(--secondary-background-color);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0; /* Top radius for tabs */
        padding: 0.6rem 1.2rem; 
        font-weight: 500; 
        color: var(--text-color);
        opacity: 0.7;
        border: none !important; /* Remove default borders */
        transition: background-color 0.2s ease, color 0.2s ease, opacity 0.2s ease;
        background-color: var(--secondary-background-color); /* Default tab background */
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--primary-color) !important; /* Use primary color on hover */
        color: white !important;
        opacity: 0.8;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important; /* Ensure contrast */
        opacity: 1;
        border-bottom: 2px solid var(--primary-color) !important; /* Highlight selected */
    }
    
    /* Input fields (Theme-Aware) */
    .stTextInput input, 
    .stNumberInput input, 
    .stDateInput input, 
    .stSelectbox > div[data-baseweb="select"] > div {
        border-radius: 6px !important;
        border: 1px solid var(--border-color, rgba(0,0,0,0.15)) !important;
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    .stTextInput input:focus, 
    .stNumberInput input:focus, 
    .stDateInput input:focus, 
    .stSelectbox > div[data-baseweb="select"] > div:focus-within { /* Selectbox focus is tricky */
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px var(--primary-color-light, rgba(102, 126, 234, 0.25)) !important; /* Light primary for focus ring */
        background-color: var(--background-color) !important; /* Change background on focus */
    }
        
    /* Divider styling (Theme-Aware) */
    hr {
        border: none;
        height: 1px;
        background-color: var(--border-color, rgba(0,0,0,0.1)); /* Simpler, theme-aware divider */
        margin: 2.5rem 0; 
    }
    
    /* Dataframe height adjustments */
    .stDataFrame {
        border: 1px solid var(--secondary-background-color);
        border-radius: 8px;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .app-main-header h1 { font-size: 2rem; }
        .app-main-header p { font-size: 1rem; }
        .app-section-header h2 { font-size: 1.3rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 4px; padding: 0.5rem 0; }
        .stTabs [data-baseweb="tab"] { padding: 0.5rem 0.8rem; font-size: 0.9rem; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 1.5rem; }
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
    if depreciable_base < 0: depreciable_base = 0.0
    all_potential_periods = generate_all_potential_periods(start_date, useful_life_years, mode)
    num_total_potential_periods = len(all_potential_periods)
    if num_total_potential_periods == 0:
        return {"Asset": asset_name, "Total Depreciation": 0.00, "Original Cost": cost, "Original Salvage": salvage}, "N/A (No periods)"
    if mode == "Monthly":
        dep_per_period_unrounded = depreciable_base / (useful_life_years * 12) if (useful_life_years * 12) > 0 else 0
        potential_labels = [p.strftime("%b %Y") for p in all_potential_periods]
    else:
        dep_per_period_unrounded = depreciable_base / useful_life_years if useful_life_years > 0 else 0
        potential_labels = [p.strftime("%Y") for p in all_potential_periods]
    all_potential_dep_values = [round(dep_per_period_unrounded, 2)] * num_total_potential_periods
    if num_total_potential_periods > 0 and depreciable_base > 0:
        current_sum_full_life = sum(all_potential_dep_values)
        diff_full_life = round(depreciable_base - current_sum_full_life, 2)
        all_potential_dep_values[-1] = round(all_potential_dep_values[-1] + diff_full_life, 2)
    actual_labels_for_schedule, actual_dep_values_for_schedule = [], []
    for i in range(num_total_potential_periods):
        period_date = all_potential_periods[i]
        if period_date <= provision_as_of_date:
            actual_labels_for_schedule.append(potential_labels[i])
            actual_dep_values_for_schedule.append(all_potential_dep_values[i])
        else: break
    total_depreciation_up_to_provision = round(sum(actual_dep_values_for_schedule), 2)
    row_data_for_schedule_df = dict(zip(actual_labels_for_schedule, actual_dep_values_for_schedule))
    row_data_for_schedule_df.update({"Asset": asset_name, "Total Depreciation": total_depreciation_up_to_provision, "Original Cost": cost, "Original Salvage": salvage})
    final_included_period_label = actual_labels_for_schedule[-1] if actual_labels_for_schedule else "N/A"
    return row_data_for_schedule_df, final_included_period_label

# ------------------ Constants ------------------
ASSET_TYPES = ["Building", "Vehicle", "Machinery", "Furniture", "Computer Equipment", "Office Equipment", "Leasehold Improvements", "Land Improvements", "Software", "Intangible Asset (e.g., Patent)"]
GAAP_USEFUL_LIVES = {
    "US GAAP": {"Building": 40, "Vehicle": 5, "Machinery": 10, "Furniture": 7, "Computer Equipment": 5, "Office Equipment": 7, "Leasehold Improvements": 15, "Land Improvements": 15, "Software": 3, "Intangible Asset (e.g., Patent)": 10},
    "IFRS": {"Building": 30, "Vehicle": 7, "Machinery": 8, "Furniture": 5, "Computer Equipment": 4, "Office Equipment": 5, "Leasehold Improvements": 10, "Land Improvements": 10, "Software": 3, "Intangible Asset (e.g., Patent)": 10},
    "Indian GAAP": {"Building": 60, "Vehicle": 8, "Machinery": 15, "Furniture": 10, "Computer Equipment": 3, "Office Equipment": 5, "Leasehold Improvements": 10, "Land Improvements": 10, "Software": 6, "Intangible Asset (e.g., Patent)": 10} 
}
MIN_CALENDAR_DATE = datetime.date(datetime.MINYEAR, 1, 1)
MAX_CALENDAR_DATE = datetime.date(datetime.MAXYEAR, 12, 31)
CURRENCIES = {"USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "JPY (¥)": "¥", "INR (₹)": "₹"}

# ------------------ UI ------------------
st.set_page_config(page_title="📊 Depreciation Pro", layout="wide", initial_sidebar_state="collapsed")
apply_custom_styling()

st.markdown("""<div class="app-main-header"><h1>📊 Depreciation Pro</h1><p>Advanced Straight-Line Depreciation Schedules with GAAP Compliance</p></div>""", unsafe_allow_html=True)

st.markdown("""<div class="app-section-header"><h2>⚙️ Global Configuration</h2></div>""", unsafe_allow_html=True)
with st.container(border=True): 
    gc_col1, gc_col2, gc_col3 = st.columns(3)
    with gc_col1:
        st.markdown("<h6>📆 Schedule Mode</h6>", unsafe_allow_html=True) 
        mode = st.radio("Schedule Mode", ["Monthly", "Yearly"], horizontal=True, index=0, label_visibility="collapsed")
    with gc_col2:
        st.markdown("<h6>📅 Depreciation Provision As Of</h6>", unsafe_allow_html=True)
        provision_as_of_date_input = st.date_input("Provision Date", value=date.today(), min_value=MIN_CALENDAR_DATE, max_value=MAX_CALENDAR_DATE, help="Calculate depreciation up to this date.", label_visibility="collapsed")
    with gc_col3:
        st.markdown("<h6>🪙 Currency</h6>", unsafe_allow_html=True)
        selected_currency_label = st.selectbox("Currency", list(CURRENCIES.keys()), index=0, label_visibility="collapsed")
        currency_symbol = CURRENCIES[selected_currency_label]

st.markdown("""<div class="app-section-header"><h2>➕ Asset Configuration</h2></div>""", unsafe_allow_html=True)
num_assets = st.number_input("Number of Assets to Configure", min_value=1, max_value=25, value=1, step=1, help="Specify how many assets you want to add to the schedule.")

asset_input_data_list = []
for i in range(num_assets):
    with st.expander(f"📁 Asset #{i + 1}: Configuration Details", expanded=True if num_assets == 1 or i == 0 else False):
        asset_name = st.text_input(f"Asset Name", value=f"Asset_{i+1}", key=f"name_{i}", placeholder="e.g., Main Office Building, Company Vehicle X1")
        grid = st.columns([2,2,1]) 
        with grid[0]:
            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
            st.markdown("<h6>💰 Financials</h6>", unsafe_allow_html=True)
            cost = st.number_input(f"Cost ({currency_symbol})", min_value=0.0, value=10000.0, step=100.0, format="%.2f", key=f"cost_{i}", help="Original purchase price of the asset")
            salvage_value_input = st.number_input(f"Salvage Value ({currency_symbol})", min_value=0.0, value=1000.0, step=100.0, format="%.2f", key=f"salvage_{i}", help="Expected residual value at the end of its useful life")
        with grid[1]:
            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
            st.markdown("<h6>📘 Parameters</h6>", unsafe_allow_html=True)
            start_date_input = st.date_input(f"In-Service Date", value=date.today(), min_value=MIN_CALENDAR_DATE, max_value=MAX_CALENDAR_DATE, key=f"date_{i}", help="The date the asset was placed in service")
            gaap_standard = st.selectbox("GAAP Standard", list(GAAP_USEFUL_LIVES.keys()), key=f"gaap_{i}", help="Select accounting standard for default useful life")
            asset_type = st.selectbox("Asset Type", ASSET_TYPES, key=f"type_{i}", help="Category of the asset")
            default_useful_life = GAAP_USEFUL_LIVES.get(gaap_standard, {}).get(asset_type, 5)
            useful_life_years_input = st.number_input("Useful Life (Years)", min_value=1, value=default_useful_life, step=1, key=f"life_{i}", help=f"Suggested: {default_useful_life} years for {asset_type} under {gaap_standard}")
        with grid[2]:
            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
            st.markdown("<h6>💡 Calculated</h6>", unsafe_allow_html=True)
            depreciable_base_display = max(0, cost - min(salvage_value_input, cost))
            st.metric(label="Depreciable Base", value=f"{currency_symbol}{depreciable_base_display:,.2f}")

        if salvage_value_input > cost:
            st.error(f"⚠️ Salvage value ({currency_symbol}{salvage_value_input:,.2f}) exceeds cost ({currency_symbol}{cost:,.2f}). Depreciable base is adjusted to {currency_symbol}0.00 for calculations.")
        if start_date_input > provision_as_of_date_input:
            st.warning(f"⚠️ In-Service Date ({start_date_input.strftime('%b %d, %Y')}) is after Provision Date ({provision_as_of_date_input.strftime('%b %d, %Y')}). No depreciation will be calculated for this asset in the current schedule.")
        
        asset_input_data_list.append({"name": asset_name, "cost": cost, "salvage": max(0.0, min(salvage_value_input, cost)), "start_date": start_date_input, "useful_life": useful_life_years_input})

st.markdown("<hr>", unsafe_allow_html=True)
if st.button("🚀 Generate Depreciation Schedule", type="primary", use_container_width=True):
    with st.spinner('⏳ Calculating depreciation schedules... Please wait.'):
        processed_asset_data_rows, asset_summary_overview_list, net_value_summary_list = [], [], []
        for asset_spec in asset_input_data_list:
            accumulated_depr_for_nbv, final_period_label_for_summary = 0.0, "N/A"
            if asset_spec["start_date"] > provision_as_of_date_input:
                row_data_from_calc = {"Asset": asset_spec["name"], "Total Depreciation": 0.0, "Original Cost": asset_spec["cost"], "Original Salvage": asset_spec["salvage"]}
                final_period_label_for_summary = "N/A (Starts after Provision Date)"
            else:
                row_data_from_calc, final_period_label_for_summary = depreciation_row(asset_name=asset_spec["name"], cost=asset_spec["cost"], salvage=asset_spec["salvage"], start_date=asset_spec["start_date"], useful_life_years=asset_spec["useful_life"], mode=mode, provision_as_of_date=provision_as_of_date_input)
                accumulated_depr_for_nbv = row_data_from_calc["Total Depreciation"]
            processed_asset_data_rows.append(row_data_from_calc)
            asset_summary_overview_list.append({"Asset": asset_spec["name"], "Useful Life (Years)": asset_spec["useful_life"], "Accumulated Depreciation": accumulated_depr_for_nbv, "Final Included Period": final_period_label_for_summary})
            net_value_summary_list.append({"Asset": asset_spec["name"], "Cost": asset_spec["cost"], "Accumulated Depreciation": accumulated_depr_for_nbv, "Net Book Value": asset_spec["cost"] - accumulated_depr_for_nbv})

        if not processed_asset_data_rows: st.error("⚠️ No asset data processed. Configure assets or check dates.")
        else:
            st.markdown("""<div class="app-section-header"><h2>📊 Calculation Results</h2></div>""", unsafe_allow_html=True)
            tab_titles = ["📋 Full Schedule", "📈 Asset Summaries", "💼 Net Value & Insights"] 
            tab1, tab2, tab3 = st.tabs(tab_titles)
            
            def get_dynamic_df_height(df, base_height=35, row_height=35, max_height=400, min_height=100):
                calculated_height = base_height + len(df) * row_height
                return min(max_height, max(min_height, calculated_height))
            
            # --- Pre-formatting Function ---
            def preformat_currency_column(df, column_name, symbol):
                if column_name in df.columns:
                    # Ensure numeric and handle NaN/inf first
                    df[column_name] = pd.to_numeric(df[column_name], errors='coerce').replace([float('inf'), float('-inf')], float('nan')).fillna(0.0).astype(float)
                    # Apply f-string formatting to convert to string
                    df[column_name] = df[column_name].apply(lambda x: f"{symbol}{x:,.2f}")
                return df

            with tab1:
                st.markdown(f"""<div style="text-align: center; margin-bottom: 1.5rem;"><h4>Full Depreciation Schedule</h4><p style="color: var(--text-color-muted, #666); font-size:0.9rem;">Up to {provision_as_of_date_input.strftime('%B %d, %Y')}</p></div>""", unsafe_allow_html=True)
                df_full = pd.DataFrame(processed_asset_data_rows)
                df_display_cols = ["Asset"] + [c for c in df_full.columns if c not in ["Asset", "Total Depreciation", "Original Cost", "Original Salvage"]] + ["Total Depreciation"]
                df_display = df_full.reindex(columns=df_display_cols).copy()

                if df_display.empty or "Asset" not in df_display.columns: st.info("📝 No data for schedule.")
                else:
                    df_display = df_display.set_index("Asset")
                    period_cols = [c for c in df_display.columns if c != "Total Depreciation"]
                    sorted_p_cols = []
                    if period_cols:
                        fmt = "%b %Y" if mode == "Monthly" else "%Y"
                        try:
                            dt_objs = [pd.to_datetime(d, format=fmt, errors='coerce') for d in period_cols if isinstance(d, str)]
                            s_pairs = sorted([(s, dt) for s, dt in zip([p for p in period_cols if isinstance(p,str)], dt_objs) if pd.notna(dt)], key=lambda pair: pair[1])
                            sorted_p_cols = [p[0] for p in s_pairs if p[0] in df_display.columns]
                        except Exception: sorted_p_cols = period_cols # Fallback
                    final_cols_order = sorted_p_cols + (["Total Depreciation"] if "Total Depreciation" in df_display.columns else [])
                    
                    if final_cols_order and not df_display.empty:
                        df_display = df_display[final_cols_order]
                        cols_to_preformat = [c for c in df_display.columns if c == "Total Depreciation" or c in sorted_p_cols]
                        
                        for col_name in cols_to_preformat:
                            df_display = preformat_currency_column(df_display, col_name, currency_symbol)
                        
                        if not df_display.empty:
                            # Styler.format is no longer needed for pre-formatted columns
                            st.dataframe(df_display, use_container_width=True, height=get_dynamic_df_height(df_display, max_height=500))
                        else: st.info("Schedule empty after ordering.")
                        
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown("<h5 style='text-align:center; margin-bottom:1rem;'>Schedule Totals</h5>", unsafe_allow_html=True)
                        
                        # For sum, use the original numeric data before it was pre-formatted to string
                        total_depr_numeric = 0.0
                        if 'Total Depreciation' in df_full.columns: # Use df_full for numeric sum
                             numeric_total_dep = pd.to_numeric(df_full['Total Depreciation'], errors='coerce').fillna(0)
                             total_depr_numeric = numeric_total_dep.sum()
                        
                        total_assets = len(df_display)
                        scols = st.columns(2)
                        scols[0].metric("Assets in Schedule", total_assets)
                        scols[1].metric("Total Depreciation", f"{currency_symbol}{total_depr_numeric:,.2f}") # Use numeric sum here
                        
                        if not df_display.empty: 
                            st.download_button("⬇️ Download Schedule CSV", 
                                               df_display.reset_index().to_csv(index=False).encode('utf-8'), # Export the string-formatted df
                                               f"{mode.lower()}_dep_sched_{provision_as_of_date_input.strftime('%Y%m%d')}.csv", 
                                               "text/csv", use_container_width=True)
                    elif df_display.empty and not processed_asset_data_rows: st.info("📝 No asset data configured.")
                    else: st.info("📅 No depreciation periods for configured assets based on dates.")

            with tab2:
                st.markdown("<h4 style='text-align:center; margin-bottom:1.5rem;'>Asset Summary Overview</h4>", unsafe_allow_html=True)
                df_summary = pd.DataFrame(asset_summary_overview_list)
                if not df_summary.empty:
                    df_summary = df_summary[["Asset", "Useful Life (Years)", "Accumulated Depreciation", "Final Included Period"]]
                    
                    # Pre-format the "Accumulated Depreciation" column
                    df_summary = preformat_currency_column(df_summary, "Accumulated Depreciation", currency_symbol)
                    
                    # Styler.format is not needed for this pre-formatted column
                    st.dataframe(df_summary, use_container_width=True, hide_index=True, height=get_dynamic_df_height(df_summary))
                else: st.info("📊 No data for Asset Summary Overview.")

            with tab3:
                st.markdown(f"<h4 style='text-align:center; margin-bottom:0.5rem;'>Net Book Value Summary</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center; color:var(--text-color-muted, #666); font-size:0.9rem; margin-bottom:1.5rem;'><em>As of {provision_as_of_date_input.strftime('%B %d, %Y')}</em></p>", unsafe_allow_html=True)
                if net_value_summary_list:
                    df_nbv = pd.DataFrame(net_value_summary_list)
                    if not df_nbv.empty:
                        # Store numeric sums before pre-formatting for GRAND TOTAL row
                        numeric_cost_sum = pd.to_numeric(df_nbv["Cost"], errors='coerce').fillna(0.0).sum()
                        numeric_ad_sum = pd.to_numeric(df_nbv["Accumulated Depreciation"], errors='coerce').fillna(0.0).sum()
                        numeric_nbv_sum = pd.to_numeric(df_nbv["Net Book Value"], errors='coerce').fillna(0.0).sum()

                        # Pre-format columns for display
                        for col_name_nbv in ["Cost", "Accumulated Depreciation", "Net Book Value"]:
                            df_nbv = preformat_currency_column(df_nbv, col_name_nbv, currency_symbol)
                        
                        # GRAND TOTAL row with pre-formatted strings
                        nbv_total_row = {
                            "Asset": "**GRAND TOTAL**", 
                            "Cost": f"{currency_symbol}{numeric_cost_sum:,.2f}", 
                            "Accumulated Depreciation": f"{currency_symbol}{numeric_ad_sum:,.2f}", 
                            "Net Book Value": f"{currency_symbol}{numeric_nbv_sum:,.2f}"
                        }
                        df_nbv_total = pd.concat([df_nbv, pd.DataFrame([nbv_total_row])], ignore_index=True)
                        
                        # Styler.format is not needed
                        st.dataframe(df_nbv_total, use_container_width=True, hide_index=True, height=get_dynamic_df_height(df_nbv_total))
                        
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown("<h5 style='text-align:center; margin-bottom:1rem;'>Financial Insights (Overall)</h5>", unsafe_allow_html=True)
                        # Use the numeric sums for calculations
                        depr_ratio = (numeric_ad_sum / numeric_cost_sum * 100) if numeric_cost_sum > 0 else 0
                        insights_cols = st.columns(2)
                        insights_cols[0].metric("Depreciation Ratio", f"{depr_ratio:.1f}%", help="% of total original cost depreciated.")
                        insights_cols[1].metric("Remaining Value Ratio", f"{100-depr_ratio:.1f}%", help="% of total original cost remaining as book value.")
                else: st.info("💼 No data for Net Value Summary.")
else:
    st.markdown("""
        <div style="text-align: center; padding: 2.5rem 1rem; background-color: var(--secondary-background-color); border: 1px solid var(--border-color, rgba(0,0,0,0.05)); border-radius: 12px; margin: 2rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
            <h3 style="color: var(--text-color); margin-bottom: 1rem;">🎯 Ready to Calculate Depreciation?</h3>
            <p style="color: var(--text-color); opacity:0.8; font-size: 1.05rem; margin-bottom: 1.5rem;">Configure assets and click <strong>'Generate Depreciation Schedule'</strong> to see:</p>
            <div style="display: flex; justify-content: space-around; gap: 1.5rem; flex-wrap: wrap; margin-top: 1rem;">
                <div style="text-align: center; padding: 1.25rem; background-color: var(--background-color); border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-width: 180px; flex:1;">
                    <div style="font-size: 2.25rem; margin-bottom: 0.5rem; color: var(--primary-color);">📋</div>
                    <div style="font-weight: 600; color: var(--text-color);">Detailed Schedules</div><div style="color: var(--text-color); opacity:0.7; font-size: 0.9rem;">Period-by-period</div></div>
                <div style="text-align: center; padding: 1.25rem; background-color: var(--background-color); border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-width: 180px; flex:1;">
                    <div style="font-size: 2.25rem; margin-bottom: 0.5rem; color: var(--primary-color);">📊</div>
                    <div style="font-weight: 600; color: var(--text-color);">Asset Summaries</div><div style="color: var(--text-color); opacity:0.7; font-size: 0.9rem;">Key metrics & insights</div></div>
                <div style="text-align: center; padding: 1.25rem; background-color: var(--background-color); border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-width: 180px; flex:1;">
                    <div style="font-size: 2.25rem; margin-bottom: 0.5rem; color: var(--primary-color);">💼</div>
                    <div style="font-weight: 600; color: var(--text-color);">Net Book Values</div><div style="color: var(--text-color); opacity:0.7; font-size: 0.9rem;">Current valuations</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""<div style="text-align: center; color: var(--text-color); opacity:0.7; font-size: 0.9rem; padding: 1rem 0 2rem 0;"><p><strong>Depreciation Pro</strong> | Straight-line depreciation calculator</p><p style="margin-top: 0.5rem;">Built with Streamlit | Supports US GAAP, IFRS, Indian GAAP</p></div>""", unsafe_allow_html=True)
