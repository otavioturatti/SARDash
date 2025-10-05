import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.data_processor import SARDataProcessor

def create_sidebar():
    """Create and manage the sidebar interface"""
    
    st.sidebar.markdown("## 🛰️ SAR Analysis Control")
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    view_options = {
        'dashboard': '📊 Main Dashboard',
        'colab_integration': '🛰️ Google Earth Engine Data',
        'insights': '🧠 AI Insights',
        'multi_biome': '🌎 Multi-Biome Analysis',
        'time_series': '📈 Time Series Analysis', 
        'comparison': '⚖️ Temporal Comparison'
    }
    
    selected_view = st.sidebar.selectbox(
        "Select View",
        options=list(view_options.keys()),
        format_func=lambda x: view_options[x],
        key='view_selector'
    )
    
    if selected_view != st.session_state.current_view:
        st.session_state.current_view = selected_view
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Region Selection
    st.sidebar.markdown("### 🌍 Region Selection")
    regions = ['Pantanal', 'Amazon', 'Cerrado', 'Atlantic Forest', 'Caatinga', 'Pampa']
    selected_region = st.sidebar.selectbox(
        "Select Biome Region",
        options=regions,
        index=regions.index(st.session_state.selected_region) if st.session_state.selected_region in regions else 0,
        key='region_selector'
    )
    
    if selected_region != st.session_state.selected_region:
        st.session_state.selected_region = selected_region
        st.session_state.data_loaded = False
        st.rerun()
    
    # Date Range Selection
    st.sidebar.markdown("### 📅 Analysis Period")
    
    # Predefined date ranges
    date_presets = {
        "Last 30 Days": (datetime.now() - timedelta(days=30), datetime.now()),
        "Last 3 Months": (datetime.now() - timedelta(days=90), datetime.now()),
        "Last 6 Months": (datetime.now() - timedelta(days=180), datetime.now()),
        "Last Year": (datetime.now() - timedelta(days=365), datetime.now()),
        "Custom": None
    }
    
    preset_choice = st.sidebar.selectbox(
        "Quick Select",
        options=list(date_presets.keys()),
        index=list(date_presets.keys()).index(st.session_state.date_preset_selection) if st.session_state.date_preset_selection in date_presets else 0,
        key='date_preset'
    )
    
    if preset_choice != "Custom" and date_presets[preset_choice]:
        start_date, end_date = date_presets[preset_choice]
        # Check if dates actually changed
        if st.session_state.date_range != [start_date, end_date] or st.session_state.date_preset_selection != preset_choice:
            st.session_state.date_range = [start_date, end_date]
            st.session_state.date_preset_selection = preset_choice
            st.session_state.data_loaded = False
    else:
        # Custom date range
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=st.session_state.date_range[0].date(),
                max_value=datetime.now().date(),
                key='start_date'
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=st.session_state.date_range[1].date(),
                max_value=datetime.now().date(),
                key='end_date'
            )
        
        # Update session state and invalidate cache if dates changed
        new_start = datetime.combine(start_date, datetime.min.time())
        new_end = datetime.combine(end_date, datetime.min.time())
        
        if st.session_state.date_range != [new_start, new_end]:
            st.session_state.date_range = [new_start, new_end]
            st.session_state.data_loaded = False
    
    st.sidebar.markdown("---")
    
    # Data Source Configuration
    st.sidebar.markdown("### 📡 Data Sources")
    
    data_sources = {
        'sentinel1': 'Sentinel-1 SAR',
        'landsat': 'Landsat 8/9',
        'modis': 'MODIS Terra/Aqua',
        'srtm': 'SRTM DEM'
    }
    
    selected_sources = {}
    for key, name in data_sources.items():
        selected_sources[key] = st.sidebar.checkbox(
            name,
            value=True,
            key=f'source_{key}'
        )
    
    st.session_state.selected_sources = selected_sources
    
    # Analysis Parameters
    st.sidebar.markdown("### ⚙️ Analysis Parameters")
    
    # SAR Processing Parameters
    with st.sidebar.expander("SAR Processing"):
        polarization = st.selectbox(
            "Polarization",
            options=['VV+VH', 'VV', 'VH'],
            index=0,
            key='polarization'
        )
        
        temporal_window = st.slider(
            "Temporal Averaging (days)",
            min_value=1,
            max_value=30,
            value=7,
            key='temporal_window'
        )
        
        speckle_filter = st.checkbox(
            "Apply Speckle Filter",
            value=True,
            key='speckle_filter'
        )
    
    # Vegetation Index Parameters
    with st.sidebar.expander("Vegetation Analysis"):
        vegetation_index = st.selectbox(
            "Vegetation Index",
            options=['NDVI', 'EVI', 'NDMI', 'NBR'],
            index=0,
            key='vegetation_index'
        )
        
        change_threshold = st.slider(
            "Change Detection Threshold",
            min_value=0.01,
            max_value=0.5,
            value=0.1,
            step=0.01,
            key='change_threshold'
        )
    
    # Water Detection Parameters
    with st.sidebar.expander("Water Analysis"):
        water_index = st.selectbox(
            "Water Index",
            options=['MNDWI', 'NDWI', 'AWEInsh', 'AWEIsh'],
            index=0,
            key='water_index'
        )
        
        water_threshold = st.slider(
            "Water Classification Threshold",
            min_value=-1.0,
            max_value=1.0,
            value=0.0,
            step=0.01,
            key='water_threshold'
        )
    
    st.sidebar.markdown("---")
    
    # Export Options
    st.sidebar.markdown("### 📤 Export Options")
    
    if st.sidebar.button("🔄 Refresh Data", type="secondary"):
        st.session_state.data_loaded = False
        st.rerun()
    
    export_format = st.sidebar.selectbox(
        "Export Format",
        options=['CSV', 'GeoJSON', 'Shapefile', 'PDF Report'],
        key='export_format'
    )
    
    if st.sidebar.button("📥 Export Analysis", type="primary"):
        st.sidebar.success("Export functionality will be available when connected to data sources")
    
    # Data Status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Status")
    
    # Initialize data processor to check status
    processor = SARDataProcessor()
    
    status_items = {
        '🛰️ SAR Data': 'Available' if selected_sources.get('sentinel1', False) else 'Disabled',
        '🌿 Vegetation': 'Available' if selected_sources.get('landsat', False) else 'Disabled',
        '💧 Water Bodies': 'Available' if selected_sources.get('modis', False) else 'Disabled',
        '📏 Elevation': 'Available' if selected_sources.get('srtm', False) else 'Disabled'
    }
    
    for item, status in status_items.items():
        color = "🟢" if status == 'Available' else "🔴"
        st.sidebar.text(f"{color} {item}: {status}")
    
    # Display current analysis window
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Current Analysis")
    st.sidebar.info(
        f"**Region:** {st.session_state.selected_region}\n\n"
        f"**Period:** {st.session_state.date_range[0].strftime('%Y-%m-%d')} to {st.session_state.date_range[1].strftime('%Y-%m-%d')}\n\n"
        f"**Duration:** {(st.session_state.date_range[1] - st.session_state.date_range[0]).days} days"
    )
