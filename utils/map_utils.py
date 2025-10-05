import folium
from folium import plugins
import streamlit as st
import json
import numpy as np
from datetime import datetime

class MapBuilder:
    """Class for building interactive maps with Folium"""
    
    def __init__(self):
        self.default_tiles = {
            'OpenStreetMap': folium.TileLayer('OpenStreetMap'),
            'Satellite': folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Satellite'
            ),
            'Terrain': folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Terrain'
            )
        }
    
    def create_base_map(self, center, zoom=9):
        """Create base map with standard configuration"""
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=None,
            prefer_canvas=True
        )
        
        # Add tile layers
        for name, tile_layer in self.default_tiles.items():
            tile_layer.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen plugin
        plugins.Fullscreen(
            position='topleft',
            title='Enter fullscreen',
            title_cancel='Exit fullscreen',
            force_separate_button=True
        ).add_to(m)
        
        # Add measure plugin
        plugins.MeasureControl(
            position='bottomleft',
            primary_length_unit='kilometers',
            secondary_length_unit='miles',
            primary_area_unit='sqkilometers',
            secondary_area_unit='acres'
        ).add_to(m)
        
        return m
    
    def add_sar_layer(self, m, sar_data, layer_name="SAR Data", bounds=None):
        """Add SAR data layer to map"""
        # In a real implementation, this would process actual SAR raster data
        # For now, we'll create a representative overlay
        
        # Create a sample heat map to represent SAR intensity
        heat_data = []
        
        # If no bounds provided, use map center to estimate bounds
        if bounds is None:
            center = m.location
            # Create approximate bounds around center
            lat_offset = 0.5
            lon_offset = 0.5
            bounds = [
                [center[0] - lat_offset, center[1] - lon_offset],
                [center[0] + lat_offset, center[1] + lon_offset]
            ]
        
        # Generate sample SAR backscatter points
        np.random.seed(42)
        for _ in range(100):
            lat = np.random.uniform(bounds[0][0], bounds[1][0])
            lon = np.random.uniform(bounds[0][1], bounds[1][1])
            intensity = np.random.uniform(0.3, 1.0)
            heat_data.append([lat, lon, intensity])
        
        # Add heatmap
        plugins.HeatMap(
            heat_data,
            name=layer_name,
            min_opacity=0.3,
            max_zoom=18,
            radius=15,
            blur=10,
            gradient={
                0.2: 'blue',
                0.4: 'cyan',
                0.6: 'lime',
                0.8: 'yellow',
                1.0: 'red'
            }
        ).add_to(m)
        
        return m
    
    def add_vegetation_layer(self, m, vegetation_data, layer_name="Vegetation Index", bounds=None):
        """Add vegetation index layer"""
        # Create vegetation index overlay
        if bounds is None:
            center = m.location
            lat_offset = 0.5
            lon_offset = 0.5
            bounds = [
                [center[0] - lat_offset, center[1] - lon_offset],
                [center[0] + lat_offset, center[1] + lon_offset]
            ]
        
        # Generate grid of vegetation values
        lat_range = np.linspace(bounds[0][0], bounds[1][0], 20)
        lon_range = np.linspace(bounds[0][1], bounds[1][1], 20)
        
        vegetation_points = []
        np.random.seed(42)
        
        for lat in lat_range:
            for lon in lon_range:
                # Simulate NDVI-like values
                ndvi = np.random.beta(2, 2)  # Values between 0 and 1
                if ndvi > 0.3:  # Only show vegetated areas
                    vegetation_points.append([lat, lon, ndvi])
        
        # Add vegetation heatmap
        plugins.HeatMap(
            vegetation_points,
            name=layer_name,
            min_opacity=0.2,
            max_zoom=18,
            radius=20,
            blur=15,
            gradient={
                0.0: 'brown',
                0.2: 'red',
                0.4: 'orange',
                0.6: 'yellow',
                0.8: 'lightgreen',
                1.0: 'darkgreen'
            }
        ).add_to(m)
        
        return m
    
    def add_water_layer(self, m, water_data, layer_name="Water Bodies", bounds=None):
        """Add water bodies layer"""
        if bounds is None:
            center = m.location
            lat_offset = 0.5
            lon_offset = 0.5
            bounds = [
                [center[0] - lat_offset, center[1] - lon_offset],
                [center[0] + lat_offset, center[1] + lon_offset]
            ]
        
        # Create sample water polygons
        water_features = []
        np.random.seed(42)
        
        for i in range(5):  # Create 5 water bodies
            center_lat = np.random.uniform(bounds[0][0], bounds[1][0])
            center_lon = np.random.uniform(bounds[0][1], bounds[1][1])
            
            # Create irregular polygon for water body
            angles = np.linspace(0, 2*np.pi, 8)
            radius = np.random.uniform(0.01, 0.03)
            
            coordinates = []
            for angle in angles:
                lat = center_lat + radius * np.cos(angle) * np.random.uniform(0.5, 1.0)
                lon = center_lon + radius * np.sin(angle) * np.random.uniform(0.5, 1.0)
                coordinates.append([lon, lat])
            coordinates.append(coordinates[0])  # Close polygon
            
            water_feature = {
                'type': 'Feature',
                'properties': {
                    'name': f'Water Body {i+1}',
                    'area_ha': np.random.randint(50, 500)
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [coordinates]
                }
            }
            water_features.append(water_feature)
        
        # Add water bodies to map
        water_layer = folium.FeatureGroup(name=layer_name)
        
        for feature in water_features:
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'darkblue',
                    'weight': 2,
                    'fillOpacity': 0.6
                },
                popup=folium.Popup(
                    f"<b>{feature['properties']['name']}</b><br>"
                    f"Area: {feature['properties']['area_ha']} ha"
                ),
                tooltip=feature['properties']['name']
            ).add_to(water_layer)
        
        water_layer.add_to(m)
        return m
    
    def add_deforestation_alerts(self, m, alerts_data, layer_name="Deforestation Alerts", bounds=None):
        """Add deforestation alert markers"""
        if bounds is None:
            center = m.location
            lat_offset = 0.5
            lon_offset = 0.5
            bounds = [
                [center[0] - lat_offset, center[1] - lon_offset],
                [center[0] + lat_offset, center[1] + lon_offset]
            ]
        
        # Generate sample deforestation alerts
        alerts_layer = folium.FeatureGroup(name=layer_name)
        np.random.seed(42)
        
        for i in range(20):  # 20 alert points
            lat = np.random.uniform(bounds[0][0], bounds[1][0])
            lon = np.random.uniform(bounds[0][1], bounds[1][1])
            
            alert_date = datetime.now().strftime('%Y-%m-%d')
            confidence = np.random.choice(['High', 'Medium', 'Low'], p=[0.3, 0.5, 0.2])
            area = np.random.randint(5, 100)
            
            # Color based on confidence
            color = {'High': 'red', 'Medium': 'orange', 'Low': 'yellow'}[confidence]
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=folium.Popup(
                    f"<b>Deforestation Alert</b><br>"
                    f"Date: {alert_date}<br>"
                    f"Confidence: {confidence}<br>"
                    f"Area: ~{area} ha",
                    max_width=200
                ),
                tooltip=f"Alert {i+1} - {confidence} confidence",
                fillColor=color,
                color='darkred',
                weight=2,
                fillOpacity=0.7
            ).add_to(alerts_layer)
        
        alerts_layer.add_to(m)
        return m
    
    def add_analysis_regions(self, m, regions_geojson, layer_name="Analysis Regions"):
        """Add analysis regions from GeoJSON"""
        regions_layer = folium.FeatureGroup(name=layer_name)
        
        def style_function(feature):
            return {
                'fillColor': 'green',
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.3
            }
        
        def highlight_function(feature):
            return {
                'fillColor': 'yellow',
                'color': 'red',
                'weight': 3,
                'fillOpacity': 0.7
            }
        
        for feature in regions_geojson['features']:
            folium.GeoJson(
                feature,
                style_function=style_function,
                highlight_function=highlight_function,
                popup=folium.Popup(
                    f"<b>Region: {feature['properties']['id']}</b><br>"
                    f"Area: {feature['properties']['area_ha']} ha<br>"
                    f"Type: {feature['properties']['vegetation_type']}"
                ),
                tooltip=feature['properties']['id']
            ).add_to(regions_layer)
        
        regions_layer.add_to(m)
        return m
    
    def add_legend(self, m, legend_html):
        """Add custom legend to map"""
        legend = folium.Element(legend_html)
        m.get_root().html.add_child(legend)
        return m

def create_legend_html():
    """Create HTML for map legend"""
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Legend</h4>
    <div><i class="fa fa-circle" style="color:red"></i> High Confidence Alerts</div>
    <div><i class="fa fa-circle" style="color:orange"></i> Medium Confidence Alerts</div>
    <div><i class="fa fa-circle" style="color:yellow"></i> Low Confidence Alerts</div>
    <div><i class="fa fa-square" style="color:blue"></i> Water Bodies</div>
    <div><i class="fa fa-square" style="color:green"></i> Analysis Regions</div>
    </div>
    '''
    return legend_html
