import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import subprocess
import atexit

# API é gerenciada pelo start_services.sh

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))

from components.sidebar import create_sidebar
from components.main_dashboard import render_main_dashboard
from components.time_series import render_time_series_analysis
from components.comparison_view import render_comparison_view
from components.insights_dashboard import render_insights_dashboard
from components.multi_biome_comparison import render_multi_biome_comparison
from components.colab_integration import render_colab_integration

# Configure page
st.set_page_config(
    page_title="SAR Biome Monitoring Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'colab_integration'
    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = 'Pantanal'
    if 'date_range' not in st.session_state:
        st.session_state.date_range = [
            datetime.now() - timedelta(days=30),
            datetime.now()
        ]
    if 'date_preset_selection' not in st.session_state:
        st.session_state.date_preset_selection = 'Last 30 Days'
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Modern Custom CSS with NASA-inspired design
    st.markdown("""
    <style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    
    /* Main Header with Gradient */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00D4FF 0%, #7B2FFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        font-family: 'Inter', sans-serif;
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Modern Metric Cards with Glassmorphism */
    .metric-card {
        background: rgba(26, 35, 50, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) !important;
        border-color: rgba(0, 212, 255, 0.5) !important;
        box-shadow: 0 12px 48px 0 rgba(0, 212, 255, 0.3) !important;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00D4FF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #B0B8C4;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        background: linear-gradient(135deg, #00D4FF 0%, #7B2FFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        font-family: 'Inter', sans-serif;
    }
    
    /* Alert Boxes */
    .alert-critical {
        background: linear-gradient(135deg, rgba(255, 59, 92, 0.2), rgba(255, 59, 92, 0.1));
        border-left: 4px solid #FF3B5C;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #FFB4C2;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 195, 0, 0.2), rgba(255, 195, 0, 0.1));
        border-left: 4px solid #FFC300;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #FFE5A0;
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 255, 136, 0.1));
        border-left: 4px solid #00FF88;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #B0FFD9;
    }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 47, 255, 0.1));
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Responsive Tables */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.9rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(0, 212, 255, 0.1);
        margin-top: 3rem;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(26, 35, 50, 0.4);
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        color: #B0B8C4;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 47, 255, 0.3));
        color: #00D4FF;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .section-header {
            font-size: 1.3rem;
        }
    }
    
    /* Sidebar Enhancements */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1120 0%, #1a2332 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00D4FF, #7B2FFF);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header with animation
    st.markdown('<div class="main-header">🛰️ SAR Biome Monitoring Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Create sidebar
    create_sidebar()
    
    # Main content area
    if st.session_state.current_view == 'dashboard':
        render_main_dashboard()
    elif st.session_state.current_view == 'colab_integration':
        render_colab_integration()
    elif st.session_state.current_view == 'insights':
        render_insights_dashboard()
    elif st.session_state.current_view == 'multi_biome':
        render_multi_biome_comparison()
    elif st.session_state.current_view == 'time_series':
        render_time_series_analysis()
    elif st.session_state.current_view == 'comparison':
        render_comparison_view()
    
    # Modern Footer
    st.markdown("""
    <div class='custom-footer'>
    🛰️ SAR Biome Monitoring Dashboard | NASA Space Apps Challenge 2025<br>
    <small>Data sources: Sentinel-1 SAR • Landsat 8/9 • MODIS Terra/Aqua • SRTM DEM</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
