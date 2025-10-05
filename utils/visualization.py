import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

class SARVisualizer:
    """Class for creating SAR data visualizations"""
    
    def __init__(self):
        self.color_schemes = {
            'vegetation': px.colors.sequential.Greens,
            'water': px.colors.sequential.Blues,
            'sar': px.colors.sequential.Viridis,
            'alerts': px.colors.sequential.Reds
        }
    
    def create_time_series_plot(self, data, metrics=None):
        """Create comprehensive time series plot"""
        if data.empty:
            return self._create_empty_plot("No time series data available")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Vegetation Index', 'Water Extent',
                'SAR Backscatter (VV)', 'SAR Backscatter (VH)',
                'Deforestation Alerts', 'Combined Analysis'
            ),
            vertical_spacing=0.08,
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": True}]]
        )
        
        # Vegetation Index
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['vegetation_index'],
                mode='lines',
                name='Vegetation Index',
                line=dict(color='green', width=2)
            ),
            row=1, col=1
        )
        
        # Water Extent
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['water_extent'],
                mode='lines',
                name='Water Extent',
                line=dict(color='blue', width=2)
            ),
            row=1, col=2
        )
        
        # SAR Backscatter VV
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['sar_backscatter_vv'],
                mode='lines',
                name='SAR VV (dB)',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # SAR Backscatter VH
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['sar_backscatter_vh'],
                mode='lines',
                name='SAR VH (dB)',
                line=dict(color='orange', width=2)
            ),
            row=2, col=2
        )
        
        # Deforestation Alerts (Bar chart)
        fig.add_trace(
            go.Bar(
                x=data['date'], 
                y=data['deforestation_alerts'],
                name='Deforestation Alerts',
                marker_color='red',
                opacity=0.7
            ),
            row=3, col=1
        )
        
        # Combined analysis (Vegetation vs Water)
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['vegetation_index'],
                mode='lines',
                name='Vegetation',
                line=dict(color='green', width=2),
                yaxis='y'
            ),
            row=3, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['water_extent'],
                mode='lines',
                name='Water',
                line=dict(color='blue', width=2),
                yaxis='y2'
            ),
            row=3, col=2,
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="SAR Time Series Analysis",
            showlegend=True,
            title_x=0.5,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=2)
        fig.update_yaxes(title_text="Index Value", row=1, col=1)
        fig.update_yaxes(title_text="Extent", row=1, col=2)
        fig.update_yaxes(title_text="Backscatter (dB)", row=2, col=1)
        fig.update_yaxes(title_text="Backscatter (dB)", row=2, col=2)
        fig.update_yaxes(title_text="Alert Count", row=3, col=1)
        fig.update_yaxes(title_text="Vegetation Index", row=3, col=2)
        fig.update_yaxes(title_text="Water Extent", row=3, col=2, secondary_y=True)
        
        return fig
    
    def create_correlation_matrix(self, data):
        """Create correlation matrix heatmap"""
        if data.empty:
            return self._create_empty_plot("No correlation data available")
        
        # Calculate correlation matrix
        numeric_cols = ['vegetation_index', 'water_extent', 'deforestation_alerts', 
                       'sar_backscatter_vv', 'sar_backscatter_vh']
        corr_matrix = data[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Parameter Correlation Matrix',
            title_x=0.5,
            width=600,
            height=500
        )
        
        return fig
    
    def create_change_detection_plot(self, data, window_size=30):
        """Create change detection analysis plot"""
        if data.empty or len(data) < window_size * 2:
            return self._create_empty_plot("Insufficient data for change detection")
        
        # Calculate rolling statistics
        data_copy = data.copy()
        data_copy['veg_rolling_mean'] = data_copy['vegetation_index'].rolling(window=window_size).mean()
        data_copy['veg_rolling_std'] = data_copy['vegetation_index'].rolling(window=window_size).std()
        data_copy['water_rolling_mean'] = data_copy['water_extent'].rolling(window=window_size).mean()
        
        # Detect significant changes
        data_copy['veg_change'] = abs(data_copy['vegetation_index'] - data_copy['veg_rolling_mean'])
        data_copy['significant_change'] = data_copy['veg_change'] > (2 * data_copy['veg_rolling_std'])
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Vegetation Index with Change Detection', 'Change Magnitude'),
            vertical_spacing=0.1
        )
        
        # Original vegetation data
        fig.add_trace(
            go.Scatter(
                x=data_copy['date'],
                y=data_copy['vegetation_index'],
                mode='lines',
                name='Vegetation Index',
                line=dict(color='green', width=1)
            ),
            row=1, col=1
        )
        
        # Rolling mean
        fig.add_trace(
            go.Scatter(
                x=data_copy['date'],
                y=data_copy['veg_rolling_mean'],
                mode='lines',
                name='Rolling Mean',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Significant changes
        change_data = data_copy[data_copy['significant_change']]
        if not change_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=change_data['date'],
                    y=change_data['vegetation_index'],
                    mode='markers',
                    name='Significant Changes',
                    marker=dict(color='red', size=8, symbol='diamond')
                ),
                row=1, col=1
            )
        
        # Change magnitude
        fig.add_trace(
            go.Scatter(
                x=data_copy['date'],
                y=data_copy['veg_change'],
                mode='lines',
                name='Change Magnitude',
                line=dict(color='orange', width=1),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        # Threshold line
        if not data_copy['veg_rolling_std'].isna().all():
            threshold = 2 * data_copy['veg_rolling_std'].mean()
            fig.add_hline(
                y=threshold,
                row=2, col=1,
                line_dash="dash",
                line_color="red",
                annotation_text="Change Threshold"
            )
        
        fig.update_layout(
            height=600,
            title_text="Change Detection Analysis",
            title_x=0.5,
            showlegend=True
        )
        
        return fig
    
    def create_sar_polarization_plot(self, data):
        """Create SAR polarization comparison plot"""
        if data.empty:
            return self._create_empty_plot("No SAR data available")
        
        fig = go.Figure()
        
        # VV Polarization
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data['sar_backscatter_vv'],
                mode='lines+markers',
                name='VV Polarization',
                line=dict(color='purple', width=2),
                marker=dict(size=4)
            )
        )
        
        # VH Polarization
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data['sar_backscatter_vh'],
                mode='lines+markers',
                name='VH Polarization',
                line=dict(color='orange', width=2),
                marker=dict(size=4)
            )
        )
        
        # Add ratio
        if 'sar_backscatter_vv' in data.columns and 'sar_backscatter_vh' in data.columns:
            data_copy = data.copy()
            data_copy['vh_vv_ratio'] = data_copy['sar_backscatter_vh'] / data_copy['sar_backscatter_vv']
            
            fig.add_trace(
                go.Scatter(
                    x=data_copy['date'],
                    y=data_copy['vh_vv_ratio'],
                    mode='lines',
                    name='VH/VV Ratio',
                    line=dict(color='red', width=2, dash='dash'),
                    yaxis='y2'
                )
            )
        
        fig.update_layout(
            title='SAR Polarization Analysis',
            title_x=0.5,
            xaxis_title='Date',
            yaxis_title='Backscatter (dB)',
            yaxis2=dict(
                title='VH/VV Ratio',
                overlaying='y',
                side='right'
            ),
            height=500
        )
        
        return fig
    
    def create_summary_statistics_plot(self, metrics):
        """Create summary statistics visualization"""
        if not metrics:
            return self._create_empty_plot("No summary statistics available")
        
        # Prepare data for plotting
        metric_names = []
        metric_values = []
        metric_colors = []
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                metric_names.append(key.replace('_', ' ').title())
                metric_values.append(value)
                
                # Color based on metric type
                if 'vegetation' in key:
                    metric_colors.append('green')
                elif 'water' in key:
                    metric_colors.append('blue')
                elif 'deforestation' in key:
                    metric_colors.append('red')
                else:
                    metric_colors.append('gray')
        
        if not metric_values:
            return self._create_empty_plot("No numeric metrics available")
        
        fig = go.Figure(data=[
            go.Bar(
                x=metric_names,
                y=metric_values,
                marker_color=metric_colors,
                text=[f'{v:.3f}' if abs(v) < 1 else f'{v:.1f}' for v in metric_values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Summary Statistics',
            title_x=0.5,
            xaxis_title='Metrics',
            yaxis_title='Values',
            height=400
        )
        
        return fig
    
    def _create_empty_plot(self, message):
        """Create empty plot with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
