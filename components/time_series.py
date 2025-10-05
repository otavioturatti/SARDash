import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add utils to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.data_processor import SARDataProcessor
from utils.visualization import SARVisualizer

def render_time_series_analysis():
    """Render the time series analysis view"""
    
    # Initialize processors
    data_processor = SARDataProcessor()
    visualizer = SARVisualizer()
    
    st.markdown("## 📈 Time Series Analysis")
    st.markdown(f"**Region:** {st.session_state.selected_region} | "
                f"**Period:** {st.session_state.date_range[0].strftime('%Y-%m-%d')} to {st.session_state.date_range[1].strftime('%Y-%m-%d')}")
    
    # Load data if not already loaded
    if not st.session_state.data_loaded:
        with st.spinner('Loading time series data...'):
            start_date = st.session_state.date_range[0]
            end_date = st.session_state.date_range[1]
            region = st.session_state.selected_region
            
            st.session_state.time_series_data = data_processor.generate_time_series_data(
                start_date, end_date, region
            )
            st.session_state.metrics = data_processor.calculate_change_metrics(
                st.session_state.time_series_data
            )
            st.session_state.data_loaded = True
    
    # Check if we have data
    if st.session_state.time_series_data.empty:
        st.error("No time series data available for the selected period and region.")
        st.stop()
    
    data = st.session_state.time_series_data
    
    # Analysis Controls
    st.markdown("### ⚙️ Analysis Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        smoothing_window = st.slider(
            "Smoothing Window (days)",
            min_value=1,
            max_value=30,
            value=7,
            help="Apply moving average smoothing to reduce noise"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=['Complete', 'Vegetation Focus', 'Water Focus', 'SAR Focus'],
            help="Select which parameters to emphasize in the analysis"
        )
    
    with col3:
        trend_analysis = st.checkbox(
            "Show Trend Lines",
            value=True,
            help="Display trend lines and seasonal decomposition"
        )
    
    with col4:
        anomaly_detection = st.checkbox(
            "Highlight Anomalies",
            value=True,
            help="Mark unusual values in the time series"
        )
    
    # Apply data processing based on controls
    processed_data = data.copy()
    
    # Define numeric columns
    numeric_cols = ['vegetation_index', 'water_extent', 'sar_backscatter_vv', 'sar_backscatter_vh']
    
    if smoothing_window > 1:
        # Apply smoothing
        for col in numeric_cols:
            processed_data[f'{col}_smooth'] = processed_data[col].rolling(
                window=smoothing_window, center=True
            ).mean()
    
    # Main Time Series Visualization
    st.markdown("### 📊 Comprehensive Time Series Analysis")
    
    if analysis_type == 'Complete':
        # Full multi-parameter analysis
        ts_fig = visualizer.create_time_series_plot(processed_data, st.session_state.metrics)
        st.plotly_chart(ts_fig, use_container_width=True)
    
    elif analysis_type == 'Vegetation Focus':
        # Focus on vegetation parameters
        st.markdown("#### 🌿 Vegetation Analysis")
        
        # Create focused vegetation plot
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Vegetation Index Over Time', 'Vegetation Change Rate'),
            vertical_spacing=0.1
        )
        
        # Vegetation index
        fig.add_trace(
            go.Scatter(
                x=processed_data['date'],
                y=processed_data['vegetation_index'],
                mode='lines',
                name='Original',
                line=dict(color='lightgreen', width=1)
            ),
            row=1, col=1
        )
        
        if smoothing_window > 1:
            fig.add_trace(
                go.Scatter(
                    x=processed_data['date'],
                    y=processed_data['vegetation_index_smooth'],
                    mode='lines',
                    name='Smoothed',
                    line=dict(color='darkgreen', width=2)
                ),
                row=1, col=1
            )
        
        # Change rate
        change_rate = processed_data['vegetation_index'].diff()
        fig.add_trace(
            go.Scatter(
                x=processed_data['date'],
                y=change_rate,
                mode='lines',
                name='Daily Change',
                line=dict(color='red', width=1)
            ),
            row=2, col=1
        )
        
        if anomaly_detection:
            # Detect anomalies (values beyond 2 standard deviations)
            threshold = 2 * change_rate.std()
            anomalies = processed_data[abs(change_rate) > threshold]
            
            if not anomalies.empty:
                fig.add_trace(
                    go.Scatter(
                        x=anomalies['date'],
                        y=anomalies['vegetation_index'],
                        mode='markers',
                        name='Anomalies',
                        marker=dict(color='red', size=8, symbol='diamond')
                    ),
                    row=1, col=1
                )
        
        fig.update_layout(height=600, title_text="Vegetation-Focused Analysis")
        st.plotly_chart(fig, use_container_width=True)
        
        # Vegetation statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Vegetation Index", f"{processed_data['vegetation_index'].mean():.3f}")
        with col2:
            st.metric("Vegetation Trend", f"{change_rate.mean():+.4f}/day")
        with col3:
            st.metric("Variability (Std)", f"{processed_data['vegetation_index'].std():.3f}")
    
    elif analysis_type == 'Water Focus':
        # Focus on water-related parameters
        st.markdown("#### 💧 Water Analysis")
        
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Water Extent Over Time', 'Water vs Vegetation Relationship'),
            vertical_spacing=0.1
        )
        
        # Water extent
        fig.add_trace(
            go.Scatter(
                x=processed_data['date'],
                y=processed_data['water_extent'],
                mode='lines',
                name='Water Extent',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Water vs Vegetation scatter
        fig.add_trace(
            go.Scatter(
                x=processed_data['vegetation_index'],
                y=processed_data['water_extent'],
                mode='markers',
                name='Water vs Vegetation',
                marker=dict(color=processed_data.index, colorscale='viridis', size=5)
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, title_text="Water-Focused Analysis")
        fig.update_xaxes(title_text="Vegetation Index", row=2, col=1)
        fig.update_yaxes(title_text="Water Extent", row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)
        
        # Water statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Water Extent", f"{processed_data['water_extent'].mean():.3f}")
        with col2:
            water_change = processed_data['water_extent'].diff().mean()
            st.metric("Water Trend", f"{water_change:+.4f}/day")
        with col3:
            correlation = processed_data['water_extent'].corr(processed_data['vegetation_index'])
            st.metric("Water-Vegetation Correlation", f"{correlation:.3f}")
    
    elif analysis_type == 'SAR Focus':
        # Focus on SAR backscatter analysis
        st.markdown("#### 🛰️ SAR Backscatter Analysis")
        
        sar_fig = visualizer.create_sar_polarization_plot(processed_data)
        st.plotly_chart(sar_fig, use_container_width=True)
        
        # SAR statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg VV Backscatter", f"{processed_data['sar_backscatter_vv'].mean():.1f} dB")
        with col2:
            st.metric("Avg VH Backscatter", f"{processed_data['sar_backscatter_vh'].mean():.1f} dB")
        with col3:
            ratio = (processed_data['sar_backscatter_vh'] / processed_data['sar_backscatter_vv']).mean()
            st.metric("Avg VH/VV Ratio", f"{ratio:.3f}")
        with col4:
            vv_trend = processed_data['sar_backscatter_vv'].diff().mean()
            st.metric("VV Trend", f"{vv_trend:+.3f} dB/day")
    
    # Change Detection Analysis
    st.markdown("### 🔍 Change Detection Analysis")
    
    change_fig = visualizer.create_change_detection_plot(processed_data, window_size=smoothing_window)
    st.plotly_chart(change_fig, use_container_width=True)
    
    # Trend Analysis
    if trend_analysis:
        st.markdown("### 📈 Trend Analysis")
        
        # Calculate trends for each parameter
        trends = {}
        numeric_cols = ['vegetation_index', 'water_extent', 'sar_backscatter_vv', 'sar_backscatter_vh']
        
        for col in numeric_cols:
            # Simple linear trend calculation
            x = np.arange(len(processed_data))
            y = processed_data[col].values
            
            # Remove NaN values
            valid_idx = ~np.isnan(y)
            if valid_idx.sum() > 1:
                slope, intercept = np.polyfit(x[valid_idx], y[valid_idx], 1)
                trends[col] = {
                    'slope': slope,
                    'direction': 'Increasing' if slope > 0 else 'Decreasing',
                    'magnitude': 'Strong' if abs(slope) > 0.001 else 'Weak'
                }
        
        # Display trends
        if trends:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Trend Summary")
                for param, trend_info in trends.items():
                    param_name = param.replace('_', ' ').title()
                    direction_emoji = "📈" if trend_info['direction'] == 'Increasing' else "📉"
                    st.write(f"{direction_emoji} **{param_name}:** {trend_info['direction']} ({trend_info['magnitude']})")
            
            with col2:
                st.markdown("#### Trend Coefficients")
                trend_df = pd.DataFrame([
                    {'Parameter': param.replace('_', ' ').title(), 'Slope': trend_info['slope']}
                    for param, trend_info in trends.items()
                ])
                st.dataframe(trend_df, hide_index=True)
    
    # Statistical Summary
    st.markdown("### 📊 Statistical Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Descriptive Statistics")
        stats_df = processed_data[numeric_cols].describe().round(4)
        st.dataframe(stats_df)
    
    with col2:
        st.markdown("#### Data Quality Metrics")
        quality_metrics = {}
        
        for col in numeric_cols:
            total_points = len(processed_data)
            valid_points = processed_data[col].notna().sum()
            completeness = (valid_points / total_points) * 100
            
            quality_metrics[col.replace('_', ' ').title()] = {
                'Completeness': f"{completeness:.1f}%",
                'Valid Points': f"{valid_points}/{total_points}",
                'Missing Points': total_points - valid_points
            }
        
        quality_df = pd.DataFrame(quality_metrics).T
        st.dataframe(quality_df)
    
    # Export Section
    st.markdown("### 📥 Export Time Series Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv_data = processed_data.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"time_series_{st.session_state.selected_region}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # JSON export for metadata
        import json
        metadata = {
            'region': st.session_state.selected_region,
            'date_range': [
                st.session_state.date_range[0].isoformat(),
                st.session_state.date_range[1].isoformat()
            ],
            'metrics': st.session_state.metrics,
            'analysis_parameters': {
                'smoothing_window': smoothing_window,
                'analysis_type': analysis_type
            }
        }
        
        json_data = json.dumps(metadata, indent=2, default=str)
        st.download_button(
            label="📋 Download Metadata",
            data=json_data,
            file_name=f"metadata_{st.session_state.selected_region}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    
    with col3:
        # Summary report
        if st.button("📊 Generate Report"):
            st.info("Advanced reporting functionality will be available in future updates")
