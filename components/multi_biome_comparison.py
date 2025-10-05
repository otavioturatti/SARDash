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

def render_multi_biome_comparison():
    """Render multi-biome comparison dashboard"""
    
    st.markdown("## 🌎 Multi-Biome Comparison Analysis")
    st.markdown("**Comprehensive Biome Health Assessment for Brazil**")
    
    data_processor = SARDataProcessor()
    
    biomes = ['Pantanal', 'Amazon', 'Cerrado', 'Atlantic Forest', 'Caatinga', 'Pampa']
    
    with st.spinner('Loading multi-biome data...'):
        biome_data = {}
        biome_metrics = {}
        
        for biome in biomes:
            data = data_processor.generate_time_series_data(
                datetime.now() - timedelta(days=90),
                datetime.now(),
                biome
            )
            biome_data[biome] = data
            biome_metrics[biome] = data_processor.calculate_change_metrics(data)
    
    tab1, tab2, tab3 = st.tabs([
        "🏆 Biome Rankings", 
        "📊 Comparative Analysis",
        "🚨 Risk Assessment"
    ])
    
    with tab1:
        render_biome_rankings(biome_data, biome_metrics)
    
    with tab2:
        render_comparative_analysis(biome_data)
    
    with tab3:
        render_risk_assessment(biome_data, biome_metrics)

def render_biome_rankings(biome_data, biome_metrics):
    """Render biome health rankings"""
    
    st.markdown('<div class="section-header">🏆 Biome Health Rankings</div>', unsafe_allow_html=True)
    
    rankings = []
    
    for biome, data in biome_data.items():
        veg_health = data['vegetation_index'].mean()
        water_health = data['water_extent'].mean()
        alert_score = max(0, 1 - (data['deforestation_alerts'].sum() / 100))
        
        overall_score = (veg_health * 0.4 + water_health * 0.3 + alert_score * 0.3) * 100
        
        rankings.append({
            'Biome': biome,
            'Health Score': overall_score,
            'Vegetation': veg_health,
            'Water': water_health,
            'Alert Score': alert_score
        })
    
    rankings_df = pd.DataFrame(rankings).sort_values('Health Score', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure()
        
        colors = ['#2ecc71' if score > 70 else '#f39c12' if score > 50 else '#e74c3c' 
                 for score in rankings_df['Health Score']]
        
        fig.add_trace(go.Bar(
            x=rankings_df['Biome'],
            y=rankings_df['Health Score'],
            marker_color=colors,
            text=[f"{score:.1f}" for score in rankings_df['Health Score']],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Overall Biome Health Scores",
            yaxis_title="Health Score (0-100)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🥇 Top Performers")
        
        for idx, row in rankings_df.head(3).iterrows():
            medal = ["🥇", "🥈", "🥉"][list(rankings_df.index).index(idx)]
            score_color = "green" if row['Health Score'] > 70 else "orange"
            
            st.markdown(f"{medal} **{row['Biome']}**")
            st.markdown(f"Score: :{score_color}[**{row['Health Score']:.1f}**]")
            st.markdown("---")
    
    st.markdown('<div class="section-header">📊 Detailed Metrics Comparison</div>', unsafe_allow_html=True)
    
    display_df = rankings_df.copy()
    display_df['Health Score'] = display_df['Health Score'].round(1)
    display_df['Vegetation'] = display_df['Vegetation'].round(3)
    display_df['Water'] = display_df['Water'].round(3)
    display_df['Alert Score'] = display_df['Alert Score'].round(3)
    display_df['Rank'] = range(1, len(display_df) + 1)
    
    st.dataframe(
        display_df[['Rank', 'Biome', 'Health Score', 'Vegetation', 'Water', 'Alert Score']],
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("### 🎯 Key Insights")
    
    best_biome = rankings_df.iloc[0]
    worst_biome = rankings_df.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"**Best Performer:** {best_biome['Biome']}")
        st.write(f"Health Score: {best_biome['Health Score']:.1f}")
        st.write(f"Key Strength: {'Vegetation' if best_biome['Vegetation'] > 0.7 else 'Water Management'}")
    
    with col2:
        st.error(f"**Needs Attention:** {worst_biome['Biome']}")
        st.write(f"Health Score: {worst_biome['Health Score']:.1f}")
        st.write(f"Primary Issue: {'Deforestation' if worst_biome['Alert Score'] < 0.5 else 'Water Stress'}")
    
    with col3:
        avg_score = rankings_df['Health Score'].mean()
        st.info(f"**National Average:** {avg_score:.1f}")
        st.write(f"Biomes above average: {len(rankings_df[rankings_df['Health Score'] > avg_score])}/6")
        st.write(f"Overall Trend: {'Stable' if 50 < avg_score < 75 else 'Concerning'}")

def render_comparative_analysis(biome_data):
    """Render side-by-side biome comparison"""
    
    st.markdown("### 📈 Vegetation Trends Across Biomes")
    
    fig = go.Figure()
    
    colors = ['green', 'blue', 'orange', 'purple', 'red', 'brown']
    
    for idx, (biome, data) in enumerate(biome_data.items()):
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['vegetation_index'],
            mode='lines',
            name=biome,
            line=dict(color=colors[idx], width=2)
        ))
    
    fig.update_layout(
        title="Vegetation Index Comparison - All Biomes",
        xaxis_title="Date",
        yaxis_title="Vegetation Index",
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 💧 Water Extent Comparison")
    
    fig2 = go.Figure()
    
    for idx, (biome, data) in enumerate(biome_data.items()):
        fig2.add_trace(go.Scatter(
            x=data['date'],
            y=data['water_extent'],
            mode='lines',
            name=biome,
            line=dict(color=colors[idx], width=2)
        ))
    
    fig2.update_layout(
        title="Water Extent Comparison - All Biomes",
        xaxis_title="Date",
        yaxis_title="Water Extent",
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("### ⚠️ Deforestation Alert Distribution")
    
    alert_data = []
    for biome, data in biome_data.items():
        alert_data.append({
            'Biome': biome,
            'Total Alerts': int(data['deforestation_alerts'].sum()),
            'Avg Daily': round(data['deforestation_alerts'].mean(), 1)
        })
    
    alert_df = pd.DataFrame(alert_data).sort_values('Total Alerts', ascending=False)
    
    fig3 = go.Figure(data=[
        go.Bar(
            x=alert_df['Biome'],
            y=alert_df['Total Alerts'],
            marker_color='crimson',
            text=alert_df['Total Alerts'],
            textposition='auto'
        )
    ])
    
    fig3.update_layout(
        title="Total Deforestation Alerts by Biome (90 days)",
        yaxis_title="Alert Count",
        height=400
    )
    
    st.plotly_chart(fig3, use_container_width=True)

def render_risk_assessment(biome_data, biome_metrics):
    """Render comprehensive risk assessment"""
    
    st.markdown("### 🚨 Comprehensive Risk Assessment")
    
    risk_levels = []
    
    for biome, data in biome_data.items():
        veg_decline = -biome_metrics[biome].get('vegetation_change', 0)
        alert_count = data['deforestation_alerts'].sum()
        water_stress = 1 - data['water_extent'].mean()
        
        risk_score = (veg_decline * 30 + alert_count * 0.5 + water_stress * 20)
        
        if risk_score > 30:
            risk_level = "CRITICAL"
            risk_color = "🔴"
        elif risk_score > 15:
            risk_level = "HIGH"
            risk_color = "🟠"
        elif risk_score > 8:
            risk_level = "MEDIUM"
            risk_color = "🟡"
        else:
            risk_level = "LOW"
            risk_color = "🟢"
        
        risk_levels.append({
            'Biome': biome,
            'Risk Level': risk_level,
            'Risk Score': risk_score,
            'Color': risk_color,
            'Veg Decline': veg_decline,
            'Alerts': alert_count,
            'Water Stress': water_stress
        })
    
    risk_df = pd.DataFrame(risk_levels).sort_values('Risk Score', ascending=False)
    
    st.markdown("#### 🎯 Risk Priority Matrix")
    
    for _, row in risk_df.iterrows():
        with st.expander(f"{row['Color']} **{row['Biome']}** - {row['Risk Level']} RISK", 
                        expanded=(row['Risk Level'] in ['CRITICAL', 'HIGH'])):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Risk Score", f"{row['Risk Score']:.1f}")
            with col2:
                st.metric("Vegetation Decline", f"{row['Veg Decline']:.3f}")
            with col3:
                st.metric("Alert Count", int(row['Alerts']))
            
            if row['Risk Level'] == 'CRITICAL':
                st.error("⚠️ **IMMEDIATE ACTION REQUIRED** - Deploy emergency response team")
            elif row['Risk Level'] == 'HIGH':
                st.warning("📋 **PRIORITY INTERVENTION** - Schedule assessment within 7 days")
            elif row['Risk Level'] == 'MEDIUM':
                st.info("👁️ **ENHANCED MONITORING** - Increase surveillance frequency")
            else:
                st.success("✅ **STABLE** - Continue routine monitoring")
    
    st.markdown("---")
    st.markdown("### 📊 Risk Distribution Overview")
    
    risk_counts = risk_df['Risk Level'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker_colors=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71'],
        hole=0.4
    )])
    
    fig.update_layout(
        title="Biome Risk Distribution",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🎯 Recommended Actions by Priority")
    
    critical_biomes = risk_df[risk_df['Risk Level'] == 'CRITICAL']['Biome'].tolist()
    high_biomes = risk_df[risk_df['Risk Level'] == 'HIGH']['Biome'].tolist()
    
    if critical_biomes:
        st.error(f"**CRITICAL Priority ({len(critical_biomes)} biomes):** {', '.join(critical_biomes)}")
        st.markdown("- 🚨 Deploy emergency response teams immediately")
        st.markdown("- 📡 Activate continuous satellite monitoring")
        st.markdown("- 👥 Coordinate with federal authorities")
    
    if high_biomes:
        st.warning(f"**HIGH Priority ({len(high_biomes)} biomes):** {', '.join(high_biomes)}")
        st.markdown("- 📋 Schedule on-site assessment within 7 days")
        st.markdown("- 🔍 Increase monitoring frequency to daily")
        st.markdown("- 🛡️ Implement preventive measures")
    
    st.success("**💡 Strategic Recommendation:** Focus 70% of resources on critical/high-risk biomes, "
              "30% on maintaining stability in low-risk areas")
