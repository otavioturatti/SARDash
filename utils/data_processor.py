import pandas as pd
import numpy as np
import geopandas as gpd
from datetime import datetime, timedelta
import json
import os

class SARDataProcessor:
    """Class for processing SAR and satellite data"""
    
    def __init__(self):
        self.data_sources = {
            'sentinel1': 'Sentinel-1 SAR',
            'landsat': 'Landsat 8/9',
            'modis': 'MODIS Terra/Aqua',
            'srtm': 'SRTM DEM'
        }
        
    def load_sample_metadata(self):
        """Generate sample metadata structure based on notebook"""
        return {
            'region': 'Pantanal',
            'coordinates': {
                'center': [-19.210022196386085, -56.72378540039063],
                'bounds': {
                    'north': -18.43010770156968,
                    'south': -19.986255155382313,
                    'east': -54.31091308593751,
                    'west': -59.13665771484376
                }
            },
            'data_availability': {
                'sentinel1': True,
                'landsat': True,
                'modis': True,
                'srtm': True
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_time_series_data(self, start_date, end_date, region='Pantanal'):
        """Generate time series data structure for analysis with biome-specific characteristics"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Biome-specific parameters for realistic differentiation
        biome_params = {
            'Pantanal': {
                'veg_mean': 0.65, 'veg_std': 0.12, 'veg_seasonal': 0.15,
                'water_mean': 0.45, 'water_std': 0.08, 'water_seasonal': 0.2,
                'alert_rate': 1.5, 'sar_vv': -11, 'sar_vh': -17,
                'seed_offset': 0
            },
            'Amazon': {
                'veg_mean': 0.85, 'veg_std': 0.08, 'veg_seasonal': 0.1,
                'water_mean': 0.35, 'water_std': 0.06, 'water_seasonal': 0.15,
                'alert_rate': 4.5, 'sar_vv': -10, 'sar_vh': -16,
                'seed_offset': 100
            },
            'Cerrado': {
                'veg_mean': 0.55, 'veg_std': 0.15, 'veg_seasonal': 0.25,
                'water_mean': 0.20, 'water_std': 0.05, 'water_seasonal': 0.1,
                'alert_rate': 3.2, 'sar_vv': -13, 'sar_vh': -19,
                'seed_offset': 200
            },
            'Atlantic Forest': {
                'veg_mean': 0.75, 'veg_std': 0.10, 'veg_seasonal': 0.12,
                'water_mean': 0.28, 'water_std': 0.06, 'water_seasonal': 0.12,
                'alert_rate': 2.8, 'sar_vv': -11.5, 'sar_vh': -17.5,
                'seed_offset': 300
            },
            'Caatinga': {
                'veg_mean': 0.40, 'veg_std': 0.18, 'veg_seasonal': 0.3,
                'water_mean': 0.15, 'water_std': 0.04, 'water_seasonal': 0.08,
                'alert_rate': 1.8, 'sar_vv': -14, 'sar_vh': -20,
                'seed_offset': 400
            },
            'Pampa': {
                'veg_mean': 0.60, 'veg_std': 0.13, 'veg_seasonal': 0.18,
                'water_mean': 0.25, 'water_std': 0.05, 'water_seasonal': 0.13,
                'alert_rate': 2.0, 'sar_vv': -12.5, 'sar_vh': -18.5,
                'seed_offset': 500
            }
        }
        
        params = biome_params.get(region, biome_params['Pantanal'])
        
        # Use biome-specific seed for differentiation but maintain some reproducibility
        seed_value = params['seed_offset'] + hash(f"{start_date}{end_date}") % 1000
        np.random.seed(seed_value)
        
        data = {
            'date': date_range,
            'vegetation_index': np.random.normal(params['veg_mean'], params['veg_std'], len(date_range)),
            'water_extent': np.random.normal(params['water_mean'], params['water_std'], len(date_range)),
            'deforestation_alerts': np.random.poisson(params['alert_rate'], len(date_range)),
            'sar_backscatter_vv': np.random.normal(params['sar_vv'], 2, len(date_range)),
            'sar_backscatter_vh': np.random.normal(params['sar_vh'], 2, len(date_range))
        }
        
        df = pd.DataFrame(data)
        
        # Add biome-specific seasonal patterns
        day_of_year = (df['date'] - df['date'].min()).dt.days
        df['vegetation_index'] += params['veg_seasonal'] * np.sin(2 * np.pi * day_of_year / 365.25)
        df['water_extent'] += params['water_seasonal'] * np.sin(2 * np.pi * day_of_year / 365.25 + np.pi/2)
        
        # Add realistic trends based on current environmental concerns
        if region == 'Amazon':
            # Amazon showing concerning declining trend
            df['vegetation_index'] -= (day_of_year / len(date_range)) * 0.05
            df['deforestation_alerts'] = df['deforestation_alerts'] * (1 + day_of_year / (len(date_range) * 2))
        elif region == 'Cerrado':
            # Cerrado with water stress
            df['water_extent'] -= (day_of_year / len(date_range)) * 0.03
        elif region == 'Pantanal':
            # Pantanal with water variability
            df['water_extent'] *= (1 + 0.3 * np.sin(2 * np.pi * day_of_year / 90))
        
        # Ensure realistic bounds
        df['vegetation_index'] = np.clip(df['vegetation_index'], 0, 1)
        df['water_extent'] = np.clip(df['water_extent'], 0, 1)
        df['deforestation_alerts'] = np.maximum(df['deforestation_alerts'], 0)
        
        return df
    
    def calculate_change_metrics(self, data):
        """Calculate key change detection metrics"""
        if len(data) < 2:
            return {}
            
        recent_data = data.tail(30)  # Last 30 days
        historical_data = data.head(-30) if len(data) > 30 else data.head(len(data)//2)
        
        metrics = {
            'vegetation_change': (
                recent_data['vegetation_index'].mean() - 
                historical_data['vegetation_index'].mean()
            ),
            'water_change': (
                recent_data['water_extent'].mean() - 
                historical_data['water_extent'].mean()
            ),
            'total_deforestation_alerts': data['deforestation_alerts'].sum(),
            'avg_sar_backscatter_vv': data['sar_backscatter_vv'].mean(),
            'avg_sar_backscatter_vh': data['sar_backscatter_vh'].mean(),
            'data_quality': 'Good' if len(data) > 100 else 'Limited'
        }
        
        return metrics
    
    def get_region_boundaries(self, region):
        """Get region boundary coordinates"""
        regions = {
            'Pantanal': {
                'center': [-19.210022196386085, -56.72378540039063],
                'bounds': [
                    [-19.986255155382313, -59.13665771484376],  # SW
                    [-18.43010770156968, -54.31091308593751]    # NE
                ]
            },
            'Amazon': {
                'center': [-3.0, -60.0],
                'bounds': [
                    [-10.0, -70.0],  # SW
                    [5.0, -50.0]     # NE
                ]
            },
            'Cerrado': {
                'center': [-15.0, -50.0],
                'bounds': [
                    [-25.0, -60.0],  # SW
                    [-5.0, -40.0]    # NE
                ]
            }
        }
        
        return regions.get(region, regions['Pantanal'])
    
    def validate_data_source(self, source):
        """Validate if data source is available"""
        # In a real implementation, this would check API availability
        return source in self.data_sources

class GeospatialProcessor:
    """Class for processing geospatial data"""
    
    def __init__(self):
        self.supported_formats = ['geojson', 'shapefile', 'kml']
    
    def create_sample_polygons(self, region_bounds):
        """Create sample analysis polygons"""
        sw_lat, sw_lon = region_bounds['bounds'][0]
        ne_lat, ne_lon = region_bounds['bounds'][1]
        
        # Create a grid of sample polygons
        polygons = []
        lat_steps = np.linspace(sw_lat, ne_lat, 4)
        lon_steps = np.linspace(sw_lon, ne_lon, 4)
        
        for i in range(len(lat_steps)-1):
            for j in range(len(lon_steps)-1):
                polygon = {
                    'type': 'Feature',
                    'properties': {
                        'id': f'polygon_{i}_{j}',
                        'area_ha': np.random.randint(100, 1000),
                        'vegetation_type': np.random.choice(['Forest', 'Grassland', 'Wetland', 'Agriculture'])
                    },
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[
                            [lon_steps[j], lat_steps[i]],
                            [lon_steps[j+1], lat_steps[i]],
                            [lon_steps[j+1], lat_steps[i+1]],
                            [lon_steps[j], lat_steps[i+1]],
                            [lon_steps[j], lat_steps[i]]
                        ]]
                    }
                }
                polygons.append(polygon)
        
        return {
            'type': 'FeatureCollection',
            'features': polygons
        }
