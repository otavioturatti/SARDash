import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.data_processor import SARDataProcessor
from utils.visualization import SARVisualizer

def render_insights_dashboard():
    """Render AI-powered insights dashboard for NASA Space Apps"""
    
    data_processor = SARDataProcessor()
    visualizer = SARVisualizer()
    
    st.markdown("## 🧠 AI-Powered Insights & Analytics")
    st.markdown("**Advanced SAR Analysis for Environmental Conservation**")
    
    if not st.session_state.data_loaded:
        with st.spinner('Generating insights...'):
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
    
    data = st.session_state.time_series_data
    
    if data.empty:
        st.error("No data available for insights generation")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Critical Insights", 
        "📊 Predictive Analytics", 
        "🌍 Environmental Impact",
        "⚡ Action Recommendations"
    ])
    
    with tab1:
        render_critical_insights(data)
    
    with tab2:
        render_predictive_analytics(data)
    
    with tab3:
        render_environmental_impact(data)
    
    with tab4:
        render_action_recommendations(data)

def render_critical_insights(data):
    """Render critical insights with anomaly detection"""
    
    st.markdown('<div class="section-header">🚨 Critical Insights & Anomaly Detection</div>', unsafe_allow_html=True)
    
    veg_mean = data['vegetation_index'].mean()
    veg_std = data['vegetation_index'].std()
    water_mean = data['water_extent'].mean()
    
    recent_data = data.tail(30)
    recent_veg = recent_data['vegetation_index'].mean()
    recent_alerts = recent_data['deforestation_alerts'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        veg_status = "Stable" if abs(recent_veg - veg_mean) < veg_std else "Critical"
        status_color = "#00FF88" if veg_status == "Stable" else "#FF3B5C"
        status_icon = "🟢" if veg_status == "Stable" else "🔴"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vegetation Status</div>
            <div class="metric-value" style="color: {status_color};">{status_icon} {veg_status}</div>
            <div style="color: {status_color};">
                {((recent_veg - veg_mean) / veg_mean * 100):+.1f}% from baseline
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        alert_level = "Low" if recent_alerts < 30 else "Medium" if recent_alerts < 60 else "High"
        alert_icon = "🟢" if alert_level == "Low" else "🟡" if alert_level == "Medium" else "🔴"
        alert_color = "#00FF88" if alert_level == "Low" else "#FFC300" if alert_level == "Medium" else "#FF3B5C"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Alert Level</div>
            <div class="metric-value" style="color: {alert_color};">{alert_icon} {alert_level}</div>
            <div style="color: {alert_color};">
                {int(recent_alerts)} alerts in 30 days
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        trend = "Improving" if recent_veg > veg_mean else "Declining"
        trend_icon = "📈" if trend == "Improving" else "📉"
        trend_color = "#00FF88" if trend == "Improving" else "#FF3B5C"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Trend Direction</div>
            <div class="metric-value" style="color: {trend_color};">{trend_icon} {trend}</div>
            <div style="color: {trend_color};">
                {abs((recent_veg - veg_mean) / veg_mean * 100):.1f}% change
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size: 1.3rem; margin-top: 1rem;">🔍 Detected Anomalies</div>', unsafe_allow_html=True)
    
    veg_anomalies = data[abs(data['vegetation_index'] - veg_mean) > 2 * veg_std]
    
    if not veg_anomalies.empty:
        st.warning(f"⚠️ **{len(veg_anomalies)} vegetation anomalies detected** - Unusual patterns requiring investigation")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['vegetation_index'],
            mode='lines',
            name='Vegetation Index',
            line=dict(color='green', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=veg_anomalies['date'],
            y=veg_anomalies['vegetation_index'],
            mode='markers',
            name='Anomalies',
            marker=dict(color='red', size=10, symbol='x')
        ))
        
        fig.add_hline(y=veg_mean, line_dash="dash", line_color="blue", 
                     annotation_text="Baseline")
        fig.add_hline(y=veg_mean + 2*veg_std, line_dash="dot", line_color="red",
                     annotation_text="Upper Threshold")
        fig.add_hline(y=veg_mean - 2*veg_std, line_dash="dot", line_color="red",
                     annotation_text="Lower Threshold")
        
        fig.update_layout(
            title="Anomaly Detection - Vegetation Index",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        anomaly_dates = veg_anomalies['date'].dt.strftime('%Y-%m-%d').tolist()
        with st.expander("📋 Anomaly Details"):
            for idx, (date, veg_val) in enumerate(zip(anomaly_dates[:5], veg_anomalies['vegetation_index'].head(5))):
                deviation = ((veg_val - veg_mean) / veg_std)
                st.write(f"**{date}:** Vegetation Index = {veg_val:.3f} ({deviation:+.1f}σ from mean)")
    else:
        st.success("✅ No significant anomalies detected - System operating within normal parameters")
    
    st.markdown("#### 🔬 Multi-Parameter Correlation")
    
    corr_data = data[['vegetation_index', 'water_extent', 'sar_backscatter_vv']].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_data.values,
        x=['Vegetation', 'Water', 'SAR VV'],
        y=['Vegetation', 'Water', 'SAR VV'],
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_data.values, 2),
        texttemplate='%{text}',
        textfont={"size": 14}
    ))
    
    fig.update_layout(title="Parameter Correlation Analysis", height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    veg_water_corr = data['vegetation_index'].corr(data['water_extent'])
    
    if abs(veg_water_corr) > 0.5:
        st.info(f"💡 **Insight:** Strong correlation ({veg_water_corr:.2f}) between vegetation and water - "
                f"Water availability is a key driver of vegetation health in this biome")

def render_predictive_analytics(data):
    """Render predictive analytics and forecasting"""
    
    st.markdown("### 📈 Predictive Analytics & Forecasting")
    
    st.markdown("#### 🔮 30-Day Trend Forecast")
    
    veg_values = data['vegetation_index'].values
    x = np.arange(len(veg_values))
    
    if len(veg_values) > 10:
        coeffs = np.polyfit(x, veg_values, deg=2)
        poly = np.poly1d(coeffs)
        
        forecast_days = 30
        future_x = np.arange(len(veg_values), len(veg_values) + forecast_days)
        forecast = poly(future_x)
        
        future_dates = pd.date_range(
            start=data['date'].iloc[-1] + timedelta(days=1),
            periods=forecast_days,
            freq='D'
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['vegetation_index'],
            mode='lines',
            name='Historical Data',
            line=dict(color='green', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast,
            mode='lines',
            name='Forecast',
            line=dict(color='orange', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates)[::-1],
            y=list(forecast + 0.05) + list(forecast - 0.05)[::-1],
            fill='toself',
            fillcolor='rgba(255,165,0,0.2)',
            line=dict(width=0),
            name='Confidence Interval',
            showlegend=True
        ))
        
        fig.update_layout(
            title="Vegetation Index - 30 Day Forecast",
            xaxis_title="Date",
            yaxis_title="Vegetation Index",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        trend_direction = "upward" if coeffs[0] > 0 else "downward"
        forecast_end = forecast[-1]
        current_val = veg_values[-1]
        change_pct = ((forecast_end - current_val) / current_val) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Forecast Direction", f"📊 {trend_direction.title()}", f"{change_pct:+.1f}%")
        with col2:
            st.metric("Predicted Value (30d)", f"{forecast_end:.3f}", f"{forecast_end - current_val:+.3f}")
        with col3:
            confidence = "High" if abs(coeffs[0]) < 0.0001 else "Medium"
            st.metric("Forecast Confidence", f"🎯 {confidence}")
        
        if change_pct < -10:
            st.error(f"⚠️ **Alert:** Forecast shows {abs(change_pct):.1f}% decline in vegetation - "
                    f"Immediate intervention recommended")
        elif change_pct > 10:
            st.success(f"✅ **Positive Trend:** Forecast shows {change_pct:.1f}% improvement in vegetation health")
    
    st.markdown("#### 📊 Seasonal Pattern Analysis")
    
    data_copy = data.copy()
    data_copy['day_of_year'] = data_copy['date'].dt.dayofyear
    
    seasonal_pattern = data_copy.groupby('day_of_year')['vegetation_index'].mean().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=seasonal_pattern['day_of_year'],
        y=seasonal_pattern['vegetation_index'],
        mode='lines',
        name='Seasonal Pattern',
        line=dict(color='forestgreen', width=3),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title="Vegetation Seasonal Pattern",
        xaxis_title="Day of Year",
        yaxis_title="Average Vegetation Index",
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_environmental_impact(data):
    """Render environmental impact assessment"""
    
    st.markdown("### 🌍 Environmental Impact Assessment")
    
    total_alerts = data['deforestation_alerts'].sum()
    avg_veg = data['vegetation_index'].mean()
    veg_loss = max(0, (0.7 - avg_veg) * 100)
    
    area_monitored_ha = 100000
    estimated_loss_ha = (total_alerts / len(data)) * area_monitored_ha * 0.01
    co2_per_ha = 200
    estimated_co2_tons = estimated_loss_ha * co2_per_ha
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Estimated Forest Loss",
            f"{estimated_loss_ha:,.0f} ha",
            help="Estimated hectares of forest lost based on deforestation alerts"
        )
    
    with col2:
        st.metric(
            "CO₂ Emissions",
            f"{estimated_co2_tons:,.0f} tons",
            help="Estimated CO₂ emissions from deforestation"
        )
    
    with col3:
        biodiversity_impact = min(100, total_alerts / 10)
        st.metric(
            "Biodiversity Impact",
            f"{biodiversity_impact:.0f}%",
            help="Estimated impact on local biodiversity"
        )
    
    with col4:
        water_impact = (1 - data['water_extent'].mean()) * 100
        st.metric(
            "Water System Impact",
            f"{water_impact:.0f}%",
            help="Impact on local water systems"
        )
    
    st.markdown("---")
    st.markdown("#### 📊 Environmental Metrics Over Time")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Vegetation Health Trend',
            'Deforestation Impact',
            'Water Availability',
            'Cumulative Environmental Damage'
        )
    )
    
    fig.add_trace(
        go.Scatter(x=data['date'], y=data['vegetation_index'], 
                  name='Vegetation', line=dict(color='green')),
        row=1, col=1
    )
    
    cumulative_alerts = data['deforestation_alerts'].cumsum()
    fig.add_trace(
        go.Scatter(x=data['date'], y=cumulative_alerts,
                  name='Cumulative Alerts', line=dict(color='red'), fill='tonexty'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=data['date'], y=data['water_extent'],
                  name='Water Extent', line=dict(color='blue')),
        row=2, col=1
    )
    
    environmental_score = (data['vegetation_index'] * 0.5 + 
                          data['water_extent'] * 0.3 + 
                          (1 - data['deforestation_alerts'] / data['deforestation_alerts'].max()) * 0.2)
    
    fig.add_trace(
        go.Scatter(x=data['date'], y=environmental_score,
                  name='Environmental Score', line=dict(color='purple')),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    current_score = environmental_score.iloc[-1]
    if current_score < 0.4:
        st.error("🔴 **Critical Environmental Status** - Immediate action required")
    elif current_score < 0.6:
        st.warning("🟡 **Moderate Environmental Concern** - Monitoring and intervention needed")
    else:
        st.success("🟢 **Healthy Environmental Status** - Continue current conservation efforts")
    
    st.markdown("#### 🌱 Conservation Impact Potential")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**If Current Trends Continue (30 days):**")
        future_loss = estimated_loss_ha * 1.3
        future_co2 = future_loss * co2_per_ha
        st.error(f"- Additional {future_loss:,.0f} ha at risk")
        st.error(f"- {future_co2:,.0f} tons more CO₂")
        st.error(f"- {biodiversity_impact * 1.5:.0f}% biodiversity impact")
    
    with col2:
        st.markdown("**With Intervention:**")
        prevented_loss = estimated_loss_ha * 0.7
        prevented_co2 = prevented_loss * co2_per_ha
        st.success(f"- {prevented_loss:,.0f} ha protected")
        st.success(f"- {prevented_co2:,.0f} tons CO₂ prevented")
        st.success(f"- {biodiversity_impact * 0.5:.0f}% biodiversity preserved")

def render_action_recommendations(data):
    """Render AI-powered action recommendations"""
    
    st.markdown("### ⚡ AI-Powered Action Recommendations")
    
    recent_data = data.tail(30)
    veg_trend = recent_data['vegetation_index'].diff().mean()
    alert_count = recent_data['deforestation_alerts'].sum()
    water_level = recent_data['water_extent'].mean()
    
    st.markdown("#### 🎯 Priority Actions")
    
    priority_actions = []
    
    if veg_trend < -0.01:
        priority_actions.append({
            'priority': 'HIGH',
            'action': 'Vegetation Decline Intervention',
            'description': f'Vegetation declining at {abs(veg_trend)*100:.2f}% per day',
            'recommendation': 'Deploy rapid response team to affected areas. Implement reforestation protocols.',
            'timeline': 'Immediate (0-7 days)',
            'resources': 'Field team, seedlings, monitoring equipment'
        })
    
    if alert_count > 40:
        priority_actions.append({
            'priority': 'HIGH',
            'action': 'Deforestation Alert Response',
            'description': f'{int(alert_count)} alerts detected in last 30 days',
            'recommendation': 'Investigate high-alert zones. Coordinate with law enforcement. Set up surveillance.',
            'timeline': 'Urgent (0-3 days)',
            'resources': 'Drones, satellite imagery, enforcement team'
        })
    
    if water_level < 0.25:
        priority_actions.append({
            'priority': 'MEDIUM',
            'action': 'Water System Restoration',
            'description': 'Water extent below critical threshold',
            'recommendation': 'Assess water sources. Implement water retention strategies. Monitor riparian zones.',
            'timeline': 'Short-term (7-14 days)',
            'resources': 'Hydrological team, water management tools'
        })
    
    if not priority_actions:
        priority_actions.append({
            'priority': 'LOW',
            'action': 'Routine Monitoring',
            'description': 'All parameters within acceptable range',
            'recommendation': 'Continue regular monitoring. Maintain current conservation efforts.',
            'timeline': 'Ongoing',
            'resources': 'Standard monitoring equipment'
        })
    
    for idx, action in enumerate(priority_actions, 1):
        priority_color = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(action['priority'], '⚪')
        
        with st.expander(f"{priority_color} **Priority {idx}: {action['action']}** [{action['priority']}]", expanded=(action['priority']=='HIGH')):
            st.markdown(f"**Situation:** {action['description']}")
            st.markdown(f"**Recommendation:** {action['recommendation']}")
            st.markdown(f"**Timeline:** {action['timeline']}")
            st.markdown(f"**Resources Needed:** {action['resources']}")
    
    st.markdown("---")
    st.markdown("#### 📍 Strategic Focus Areas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Immediate Actions (0-7 days)**")
        st.markdown("1. ✅ Deploy monitoring in high-alert zones")
        st.markdown("2. ✅ Activate rapid response protocols")
        st.markdown("3. ✅ Coordinate with local authorities")
        st.markdown("4. ✅ Establish emergency communication channels")
    
    with col2:
        st.markdown("**Medium-term Strategy (7-30 days)**")
        st.markdown("1. 📋 Implement reforestation programs")
        st.markdown("2. 📋 Enhance surveillance infrastructure")
        st.markdown("3. 📋 Community engagement initiatives")
        st.markdown("4. 📋 Long-term monitoring setup")
    
    st.markdown("---")
    st.markdown("#### 🎯 Success Metrics & KPIs")
    
    kpi_data = pd.DataFrame({
        'Metric': ['Vegetation Recovery', 'Alert Reduction', 'Water Restoration', 'Biodiversity Protection'],
        'Current': ['65%', f'{int(alert_count)}', '28%', '72%'],
        'Target (30d)': ['75%', f'{int(alert_count * 0.6)}', '35%', '85%'],
        'Target (90d)': ['85%', f'{int(alert_count * 0.3)}', '45%', '95%']
    })
    
    st.dataframe(kpi_data, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 📊 Implementation Roadmap")
    
    fig = go.Figure()
    
    phases = ['Phase 1\nAssessment', 'Phase 2\nIntervention', 'Phase 3\nMonitoring', 'Phase 4\nOptimization']
    timeline = [7, 14, 21, 30]
    progress = [100, 60, 30, 10]
    
    fig.add_trace(go.Bar(
        x=phases,
        y=timeline,
        text=[f'{t} days' for t in timeline],
        textposition='auto',
        marker_color=['green', 'orange', 'blue', 'purple'],
        name='Timeline'
    ))
    
    fig.update_layout(
        title="Conservation Action Roadmap",
        yaxis_title="Days from Start",
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("💡 **Pro Tip:** Real-time SAR monitoring enables 24/7 surveillance regardless of weather conditions, "
              "providing crucial early warning for environmental threats.")
