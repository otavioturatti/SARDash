import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.data_processor import SARDataProcessor
from utils.visualization import SARVisualizer

def render_comparison_view():
    """Render the temporal comparison view"""
    
    # Initialize processors
    data_processor = SARDataProcessor()
    visualizer = SARVisualizer()
    
    st.markdown("## ⚖️ Temporal Comparison Analysis")
    st.markdown("Compare different time periods to identify changes and trends in the biome")
    
    # Comparison Configuration
    st.markdown("### ⚙️ Comparison Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Period A (Baseline)")
        
        # Period A date selection
        period_a_preset = st.selectbox(
            "Quick Select - Period A",
            options=["Last Year", "Same Period Last Year", "Custom"],
            key='period_a_preset'
        )
        
        if period_a_preset == "Last Year":
            period_a_end = datetime.now() - timedelta(days=365)
            period_a_start = period_a_end - timedelta(days=90)  # 3 months
        elif period_a_preset == "Same Period Last Year":
            current_range = st.session_state.date_range[1] - st.session_state.date_range[0]
            period_a_end = st.session_state.date_range[1] - timedelta(days=365)
            period_a_start = period_a_end - current_range
        else:  # Custom
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                period_a_start = st.date_input(
                    "Start Date A",
                    value=datetime.now().date() - timedelta(days=455),  # ~15 months ago
                    key='period_a_start'
                )
            with col_a2:
                period_a_end = st.date_input(
                    "End Date A", 
                    value=datetime.now().date() - timedelta(days=365),  # 1 year ago
                    key='period_a_end'
                )
            
            period_a_start = datetime.combine(period_a_start, datetime.min.time())
            period_a_end = datetime.combine(period_a_end, datetime.min.time())
        
        st.info(f"📍 Period A: {period_a_start.strftime('%Y-%m-%d')} to {period_a_end.strftime('%Y-%m-%d')}")
    
    with col2:
        st.markdown("#### 📅 Period B (Current)")
        
        # Use current session date range as Period B
        period_b_start = st.session_state.date_range[0]
        period_b_end = st.session_state.date_range[1]
        
        st.info(f"📍 Period B: {period_b_start.strftime('%Y-%m-%d')} to {period_b_end.strftime('%Y-%m-%d')}")
        
        # Option to use different region for Period B
        use_different_region = st.checkbox("Compare different region for Period B", key='diff_region')
        
        if use_different_region:
            regions = ['Pantanal', 'Amazon', 'Cerrado', 'Atlantic Forest', 'Caatinga', 'Pampa']
            period_b_region = st.selectbox(
                "Region for Period B",
                options=regions,
                index=regions.index('Amazon') if st.session_state.selected_region != 'Amazon' else 1,
                key='period_b_region'
            )
        else:
            period_b_region = st.session_state.selected_region
    
    # Parameters to compare
    st.markdown("### 📊 Comparison Parameters")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        compare_vegetation = st.checkbox("🌿 Vegetation Index", value=True)
        compare_water = st.checkbox("💧 Water Extent", value=True)
    with col2:
        compare_sar_vv = st.checkbox("📡 SAR VV Backscatter", value=True)
        compare_sar_vh = st.checkbox("📡 SAR VH Backscatter", value=False)
    with col3:
        compare_alerts = st.checkbox("⚠️ Deforestation Alerts", value=True)
        statistical_tests = st.checkbox("📈 Statistical Significance Tests", value=False)
    
    # Generate comparison button
    if st.button("🔍 Run Comparison Analysis", type="primary"):
        
        with st.spinner("Generating comparison data..."):
            # Generate data for both periods
            data_a = data_processor.generate_time_series_data(
                period_a_start, period_a_end, st.session_state.selected_region
            )
            data_b = data_processor.generate_time_series_data(
                period_b_start, period_b_end, period_b_region
            )
            
            # Calculate metrics for both periods
            metrics_a = data_processor.calculate_change_metrics(data_a)
            metrics_b = data_processor.calculate_change_metrics(data_b)
        
        # Store in session state
        st.session_state.comparison_data_a = data_a
        st.session_state.comparison_data_b = data_b
        st.session_state.comparison_metrics_a = metrics_a
        st.session_state.comparison_metrics_b = metrics_b
        st.session_state.comparison_ready = True
        
        st.success("✅ Comparison data generated successfully!")
    
    # Display comparison results if available
    if st.session_state.get('comparison_ready', False):
        
        data_a = st.session_state.comparison_data_a
        data_b = st.session_state.comparison_data_b
        metrics_a = st.session_state.comparison_metrics_a
        metrics_b = st.session_state.comparison_metrics_b
        
        # Comparison Summary
        st.markdown("### 📈 Comparison Summary")
        
        # Key metrics comparison
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            veg_a = metrics_a.get('vegetation_change', 0)
            veg_b = metrics_b.get('vegetation_change', 0)
            veg_diff = veg_b - veg_a
            
            st.metric(
                "Vegetation Change",
                value=f"{veg_b:.3f}",
                delta=f"{veg_diff:+.3f} vs Period A"
            )
        
        with col2:
            water_a = metrics_a.get('water_change', 0)
            water_b = metrics_b.get('water_change', 0)
            water_diff = water_b - water_a
            
            st.metric(
                "Water Change",
                value=f"{water_b:.3f}",
                delta=f"{water_diff:+.3f} vs Period A"
            )
        
        with col3:
            alerts_a = metrics_a.get('total_deforestation_alerts', 0)
            alerts_b = metrics_b.get('total_deforestation_alerts', 0)
            alerts_diff = alerts_b - alerts_a
            
            st.metric(
                "Total Alerts",
                value=int(alerts_b),
                delta=f"{alerts_diff:+.0f} vs Period A"
            )
        
        with col4:
            sar_a = metrics_a.get('avg_sar_backscatter_vv', 0)
            sar_b = metrics_b.get('avg_sar_backscatter_vv', 0)
            sar_diff = sar_b - sar_a
            
            st.metric(
                "Avg SAR VV (dB)",
                value=f"{sar_b:.1f}",
                delta=f"{sar_diff:+.1f} vs Period A"
            )
        
        # Side-by-side Time Series Comparison
        st.markdown("### 📊 Time Series Comparison")
        
        # Create comparison plots based on selected parameters
        if compare_vegetation:
            st.markdown("#### 🌿 Vegetation Index Comparison")
            
            fig = go.Figure()
            
            # Period A
            fig.add_trace(go.Scatter(
                x=data_a['date'],
                y=data_a['vegetation_index'],
                mode='lines',
                name=f'Period A ({st.session_state.selected_region})',
                line=dict(color='lightgreen', width=2)
            ))
            
            # Period B
            fig.add_trace(go.Scatter(
                x=data_b['date'],
                y=data_b['vegetation_index'],
                mode='lines',
                name=f'Period B ({period_b_region})',
                line=dict(color='darkgreen', width=2)
            ))
            
            # Add averages
            fig.add_hline(
                y=data_a['vegetation_index'].mean(),
                line_dash="dash",
                line_color="lightgreen",
                annotation_text=f"Period A Avg: {data_a['vegetation_index'].mean():.3f}"
            )
            
            fig.add_hline(
                y=data_b['vegetation_index'].mean(),
                line_dash="dash", 
                line_color="darkgreen",
                annotation_text=f"Period B Avg: {data_b['vegetation_index'].mean():.3f}"
            )
            
            fig.update_layout(
                title="Vegetation Index Comparison",
                xaxis_title="Date",
                yaxis_title="Vegetation Index",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        if compare_water:
            st.markdown("#### 💧 Water Extent Comparison")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=data_a['date'],
                y=data_a['water_extent'],
                mode='lines',
                name=f'Period A ({st.session_state.selected_region})',
                line=dict(color='lightblue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=data_b['date'],
                y=data_b['water_extent'],
                mode='lines',
                name=f'Period B ({period_b_region})',
                line=dict(color='darkblue', width=2)
            ))
            
            fig.update_layout(
                title="Water Extent Comparison",
                xaxis_title="Date",
                yaxis_title="Water Extent",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        if compare_sar_vv or compare_sar_vh:
            st.markdown("#### 📡 SAR Backscatter Comparison")
            
            fig = make_subplots(
                rows=2 if compare_sar_vv and compare_sar_vh else 1,
                cols=1,
                subplot_titles=(['VV Polarization', 'VH Polarization'] if compare_sar_vv and compare_sar_vh 
                              else ['VV Polarization'] if compare_sar_vv else ['VH Polarization'])
            )
            
            row = 1
            if compare_sar_vv:
                fig.add_trace(
                    go.Scatter(
                        x=data_a['date'],
                        y=data_a['sar_backscatter_vv'],
                        mode='lines',
                        name='Period A - VV',
                        line=dict(color='purple', width=2)
                    ),
                    row=row, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data_b['date'],
                        y=data_b['sar_backscatter_vv'],
                        mode='lines',
                        name='Period B - VV',
                        line=dict(color='darkred', width=2)
                    ),
                    row=row, col=1
                )
                row += 1
            
            if compare_sar_vh:
                fig.add_trace(
                    go.Scatter(
                        x=data_a['date'],
                        y=data_a['sar_backscatter_vh'],
                        mode='lines',
                        name='Period A - VH',
                        line=dict(color='orange', width=2)
                    ),
                    row=row, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data_b['date'],
                        y=data_b['sar_backscatter_vh'],
                        mode='lines',
                        name='Period B - VH',
                        line=dict(color='brown', width=2)
                    ),
                    row=row, col=1
                )
            
            fig.update_layout(
                height=600 if compare_sar_vv and compare_sar_vh else 400,
                title_text="SAR Backscatter Comparison"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        if compare_alerts:
            st.markdown("#### ⚠️ Deforestation Alerts Comparison")
            
            # Aggregate alerts by week for comparison
            data_a_weekly = data_a.copy()
            data_a_weekly['week'] = data_a_weekly['date'].dt.isocalendar().week
            alerts_a_weekly = data_a_weekly.groupby('week')['deforestation_alerts'].sum()
            
            data_b_weekly = data_b.copy()
            data_b_weekly['week'] = data_b_weekly['date'].dt.isocalendar().week
            alerts_b_weekly = data_b_weekly.groupby('week')['deforestation_alerts'].sum()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=alerts_a_weekly.index,
                y=alerts_a_weekly.values,
                name='Period A',
                marker_color='orange',
                opacity=0.7
            ))
            
            fig.add_trace(go.Bar(
                x=alerts_b_weekly.index,
                y=alerts_b_weekly.values,
                name='Period B',
                marker_color='red',
                opacity=0.7
            ))
            
            fig.update_layout(
                title="Weekly Deforestation Alerts Comparison",
                xaxis_title="Week of Year",
                yaxis_title="Alert Count",
                height=400,
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistical Analysis
        if statistical_tests:
            st.markdown("### 📊 Statistical Analysis")
            
            from scipy import stats
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### T-Test Results")
                
                # Perform t-tests for each parameter
                test_results = {}
                
                if compare_vegetation and len(data_a) > 1 and len(data_b) > 1:
                    t_stat, p_val = stats.ttest_ind(data_a['vegetation_index'], data_b['vegetation_index'])
                    test_results['Vegetation Index'] = {'t_stat': t_stat, 'p_value': p_val}
                
                if compare_water and len(data_a) > 1 and len(data_b) > 1:
                    t_stat, p_val = stats.ttest_ind(data_a['water_extent'], data_b['water_extent'])
                    test_results['Water Extent'] = {'t_stat': t_stat, 'p_value': p_val}
                
                if compare_sar_vv and len(data_a) > 1 and len(data_b) > 1:
                    t_stat, p_val = stats.ttest_ind(data_a['sar_backscatter_vv'], data_b['sar_backscatter_vv'])
                    test_results['SAR VV'] = {'t_stat': t_stat, 'p_value': p_val}
                
                # Display results
                for param, result in test_results.items():
                    significance = "Significant" if result['p_value'] < 0.05 else "Not Significant"
                    significance_color = "🟢" if result['p_value'] < 0.05 else "🔴"
                    
                    st.write(f"{significance_color} **{param}:**")
                    st.write(f"  - t-statistic: {result['t_stat']:.3f}")
                    st.write(f"  - p-value: {result['p_value']:.3f}")
                    st.write(f"  - Result: {significance}")
                    st.write("")
            
            with col2:
                st.markdown("#### Distribution Comparison")
                
                # Create box plots for comparison
                if compare_vegetation:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Box(
                        y=data_a['vegetation_index'],
                        name='Period A',
                        marker_color='lightgreen'
                    ))
                    
                    fig.add_trace(go.Box(
                        y=data_b['vegetation_index'],
                        name='Period B',
                        marker_color='darkgreen'
                    ))
                    
                    fig.update_layout(
                        title="Vegetation Index Distribution",
                        yaxis_title="Vegetation Index",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Change Summary Table
        st.markdown("### 📋 Change Summary Table")
        
        # Create comprehensive change summary
        summary_data = []
        
        parameters = {
            'Vegetation Index': ('vegetation_index', 'vegetation_change'),
            'Water Extent': ('water_extent', 'water_change'),
            'SAR VV Backscatter': ('sar_backscatter_vv', 'avg_sar_backscatter_vv'),
            'SAR VH Backscatter': ('sar_backscatter_vh', 'avg_sar_backscatter_vh'),
            'Deforestation Alerts': ('deforestation_alerts', 'total_deforestation_alerts')
        }
        
        for param_name, (data_col, metric_col) in parameters.items():
            if data_col in data_a.columns and data_col in data_b.columns:
                
                if param_name == 'Deforestation Alerts':
                    # Special handling for alerts (sum instead of mean)
                    period_a_val = data_a[data_col].sum()
                    period_b_val = data_b[data_col].sum()
                else:
                    period_a_val = data_a[data_col].mean()
                    period_b_val = data_b[data_col].mean()
                
                absolute_change = period_b_val - period_a_val
                percent_change = ((period_b_val - period_a_val) / abs(period_a_val)) * 100 if period_a_val != 0 else 0
                
                trend = "↗️ Increase" if absolute_change > 0 else "↘️ Decrease" if absolute_change < 0 else "➡️ No Change"
                
                summary_data.append({
                    'Parameter': param_name,
                    'Period A': f"{period_a_val:.3f}",
                    'Period B': f"{period_b_val:.3f}",
                    'Absolute Change': f"{absolute_change:+.3f}",
                    'Percent Change': f"{percent_change:+.1f}%",
                    'Trend': trend
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, hide_index=True, use_container_width=True)
        
        # Export Comparison Results
        st.markdown("### 📥 Export Comparison Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export comparison data
            comparison_export = {
                'period_a_data': data_a.to_dict(),
                'period_b_data': data_b.to_dict(),
                'period_a_metrics': metrics_a,
                'period_b_metrics': metrics_b,
                'summary': summary_data
            }
            
            import json
            export_json = json.dumps(comparison_export, indent=2, default=str)
            
            st.download_button(
                label="📊 Download Comparison Data (JSON)",
                data=export_json,
                file_name=f"comparison_analysis_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        with col2:
            if summary_data:
                summary_csv = pd.DataFrame(summary_data).to_csv(index=False)
                st.download_button(
                    label="📋 Download Summary (CSV)",
                    data=summary_csv,
                    file_name=f"comparison_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("👆 Configure the comparison parameters above and click 'Run Comparison Analysis' to begin the analysis.")
        
        # Show example of what the comparison will include
        with st.expander("🔍 What will be compared?"):
            st.markdown("""
            The temporal comparison analysis will provide:
            
            **📊 Quantitative Comparisons:**
            - Side-by-side time series plots
            - Statistical significance testing (t-tests)
            - Percentage and absolute change calculations
            - Distribution comparisons (box plots)
            
            **📈 Visual Comparisons:**
            - Overlaid time series for direct comparison
            - Before/after average lines
            - Weekly/monthly aggregation views
            - Correlation analysis between periods
            
            **📋 Summary Reports:**
            - Change summary table with trends
            - Key metrics comparison
            - Statistical test results
            - Exportable results in multiple formats
            
            **🔬 Advanced Analysis:**
            - Anomaly detection differences
            - Seasonal pattern comparison  
            - Change rate analysis
            - Confidence intervals for changes
            """)
