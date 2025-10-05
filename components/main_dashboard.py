import streamlit as st
import pandas as pd
import sys
import os
from streamlit_folium import st_folium

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.data_processor import SARDataProcessor, GeospatialProcessor
from utils.map_utils import MapBuilder, create_legend_html
from utils.visualization import SARVisualizer

def render_main_dashboard():
    """Render the main dashboard view"""
    
    # Initialize processors
    data_processor = SARDataProcessor()
    geo_processor = GeospatialProcessor()
    map_builder = MapBuilder()
    visualizer = SARVisualizer()
    
    # Page header
    st.markdown("## 📊 SAR Biome Monitoring Dashboard")
    st.markdown(f"**Current Analysis Region:** {st.session_state.selected_region}")
    
    # Load or generate data
    if not st.session_state.data_loaded:
        with st.spinner('Loading SAR analysis data...'):
            # Generate sample data based on current selections
            start_date = st.session_state.date_range[0]
            end_date = st.session_state.date_range[1]
            region = st.session_state.selected_region
            
            # Store data in session state
            st.session_state.time_series_data = data_processor.generate_time_series_data(
                start_date, end_date, region
            )
            st.session_state.metadata = data_processor.load_sample_metadata()
            st.session_state.metrics = data_processor.calculate_change_metrics(
                st.session_state.time_series_data
            )
            st.session_state.data_loaded = True
    
    # Data availability check
    if not any(st.session_state.selected_sources.values()):
        st.warning("⚠️ No data sources selected. Please enable at least one data source in the sidebar.")
        st.stop()
    
    # Key Metrics Row with Modern Cards
    st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
    
    metrics = st.session_state.metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        vegetation_change = metrics.get('vegetation_change', 0)
        delta_icon = "↑" if vegetation_change > 0 else "↓" if vegetation_change < 0 else "→"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌿 Vegetation Change</div>
            <div class="metric-value">{vegetation_change:.3f}</div>
            <div style="color: {'#00FF88' if vegetation_change > 0 else '#FF3B5C' if vegetation_change < 0 else '#FFC300'};">
                {delta_icon} {vegetation_change:+.3f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        water_change = metrics.get('water_change', 0)
        delta_icon = "↑" if water_change > 0 else "↓" if water_change < 0 else "→"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💧 Water Extent Change</div>
            <div class="metric-value">{water_change:.3f}</div>
            <div style="color: {'#00D4FF' if water_change > 0 else '#FF3B5C' if water_change < 0 else '#FFC300'};">
                {delta_icon} {water_change:+.3f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_alerts = metrics.get('total_deforestation_alerts', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Total Alerts</div>
            <div class="metric-value">{int(total_alerts)}</div>
            <div style="color: {'#FF3B5C' if total_alerts > 50 else '#FFC300' if total_alerts > 20 else '#00FF88'};">
                {int(total_alerts)} alerts detected
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        data_quality = metrics.get('data_quality', 'Unknown')
        quality_emoji = "🟢" if data_quality == "Good" else "🟡" if data_quality == "Limited" else "🔴"
        quality_color = "#00FF88" if data_quality == "Good" else "#FFC300" if data_quality == "Limited" else "#FF3B5C"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Data Quality</div>
            <div class="metric-value" style="background: linear-gradient(135deg, {quality_color}, #00D4FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {quality_emoji}
            </div>
            <div style="color: {quality_color};">
                {data_quality}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Interactive Map Section
    st.markdown('<div class="section-header">🗺️ Interactive Analysis Map</div>', unsafe_allow_html=True)
    
    # Map controls
    col1, col2, col3 = st.columns(3)
    with col1:
        show_sar = st.checkbox("🛰️ SAR Intensity", value=True, key='show_sar_main')
    with col2:
        show_vegetation = st.checkbox("🌿 Vegetation Index", value=True, key='show_veg_main')
    with col3:
        show_alerts = st.checkbox("⚠️ Deforestation Alerts", value=True, key='show_alerts_main')
    
    # Create map
    region_bounds = data_processor.get_region_boundaries(st.session_state.selected_region)
    map_obj = map_builder.create_base_map(
        center=region_bounds['center'],
        zoom=9
    )
    
    # Prepare bounds for layers
    layer_bounds = region_bounds['bounds']
    
    # Add selected layers
    if show_sar and st.session_state.selected_sources.get('sentinel1', False):
        map_obj = map_builder.add_sar_layer(map_obj, None, "SAR Intensity", bounds=layer_bounds)
    
    if show_vegetation and st.session_state.selected_sources.get('landsat', False):
        map_obj = map_builder.add_vegetation_layer(map_obj, None, "Vegetation Index", bounds=layer_bounds)
    
    if st.session_state.selected_sources.get('modis', False):
        map_obj = map_builder.add_water_layer(map_obj, None, "Water Bodies", bounds=layer_bounds)
    
    if show_alerts:
        map_obj = map_builder.add_deforestation_alerts(map_obj, None, "Deforestation Alerts", bounds=layer_bounds)
    
    # Add analysis regions
    regions_geojson = geo_processor.create_sample_polygons(region_bounds)
    map_obj = map_builder.add_analysis_regions(map_obj, regions_geojson, "Analysis Regions")
    
    # Add legend
    legend_html = create_legend_html()
    map_obj = map_builder.add_legend(map_obj, legend_html)
    
    # Display map with responsive width
    map_data = st_folium(map_obj, width=None, height=500, returned_objects=["last_object_clicked"], use_container_width=True)
    
    # Display clicked feature info
    if map_data['last_object_clicked']:
        clicked_data = map_data['last_object_clicked']
        if clicked_data:
            st.info(f"📍 **Clicked Location:** {clicked_data.get('lat', 'N/A'):.4f}, {clicked_data.get('lng', 'N/A'):.4f}")
    
    # Analysis Charts Section
    st.markdown('<div class="section-header">📊 Quick Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SAR Polarization Analysis")
        if not st.session_state.time_series_data.empty:
            sar_fig = visualizer.create_sar_polarization_plot(st.session_state.time_series_data)
            st.plotly_chart(sar_fig, use_container_width=True)
        else:
            st.info("No SAR data available for the selected period")
    
    with col2:
        st.markdown("#### Parameter Correlations")
        if not st.session_state.time_series_data.empty:
            corr_fig = visualizer.create_correlation_matrix(st.session_state.time_series_data)
            st.plotly_chart(corr_fig, use_container_width=True)
        else:
            st.info("No correlation data available")
    
    # Summary Statistics
    st.markdown('<div class="section-header">📈 Summary Statistics</div>', unsafe_allow_html=True)
    
    if metrics:
        summary_fig = visualizer.create_summary_statistics_plot(metrics)
        st.plotly_chart(summary_fig, use_container_width=True)
    else:
        st.info("No summary statistics available")
    
    # Recent Changes Table
    st.markdown('<div class="section-header">📋 Recent Analysis Results</div>', unsafe_allow_html=True)
    
    if not st.session_state.time_series_data.empty:
        # Get recent data (last 10 records)
        recent_data = st.session_state.time_series_data.tail(10).copy()
        recent_data['date'] = recent_data['date'].dt.strftime('%Y-%m-%d')
        
        # Select and rename columns for display
        display_data = recent_data[['date', 'vegetation_index', 'water_extent', 
                                   'deforestation_alerts', 'sar_backscatter_vv']].copy()
        display_data.columns = ['Date', 'Vegetation Index', 'Water Extent', 
                               'Deforestation Alerts', 'SAR VV (dB)']
        
        # Format numeric columns
        for col in ['Vegetation Index', 'Water Extent', 'SAR VV (dB)']:
            display_data[col] = display_data[col].round(3)
        
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button for full dataset
        csv_data = st.session_state.time_series_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv_data,
            file_name=f"sar_analysis_{st.session_state.selected_region}_{st.session_state.date_range[0].strftime('%Y%m%d')}_{st.session_state.date_range[1].strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No recent analysis data available")
    
    # Data Source Information
    with st.expander("📡 Data Source Information"):
        st.markdown("""
        **Active Data Sources:**
        
        - **🛰️ Sentinel-1 SAR:** Synthetic Aperture Radar data for all-weather monitoring
        - **🌍 Landsat 8/9:** Optical imagery for vegetation and land use analysis  
        - **📡 MODIS:** Moderate resolution imagery for large-scale monitoring
        - **📏 SRTM DEM:** Digital elevation model for topographic analysis
        
        **Analysis Parameters:**
        - Temporal resolution: Daily composites
        - Spatial resolution: 10-30m depending on sensor
        - Processing level: Analysis Ready Data (ARD)
        
        **Change Detection Methodology:**
        - Statistical analysis of time series data
        - Threshold-based alert generation
        - Multi-temporal comparison algorithms
        """)
    
    # System Status
    with st.expander("⚙️ System Status"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Processing Status:**")
            st.success("✅ Data loading: Complete")
            st.success("✅ Analysis pipeline: Active") 
            st.success("✅ Visualization: Ready")
            
        with col2:
            st.markdown("**Data Coverage:**")
            date_range = st.session_state.date_range
            days_analyzed = (date_range[1] - date_range[0]).days
            st.info(f"📅 Analysis period: {days_analyzed} days")
            st.info(f"📊 Data points: {len(st.session_state.time_series_data) if not st.session_state.time_series_data.empty else 0}")
            st.info(f"🌍 Region: {st.session_state.selected_region}")
