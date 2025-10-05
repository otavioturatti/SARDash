# SAR Biome Monitoring Dashboard

## Overview

This is a Streamlit-based web application for monitoring and analyzing Brazilian biomes using Synthetic Aperture Radar (SAR) and satellite data. The dashboard provides environmental conservation insights through time series analysis, multi-biome comparisons, and AI-powered analytics. It focuses on six major Brazilian biomes: Pantanal, Amazon, Cerrado, Atlantic Forest, Caatinga, and Pampa.

The application visualizes satellite data from multiple sources (Sentinel-1 SAR, Landsat 8/9, MODIS Terra/Aqua, SRTM DEM) to track vegetation health, water extent, deforestation alerts, and environmental changes over time.

**Created for NASA Space Apps Challenge 2025** - Features advanced AI insights, predictive analytics, multi-biome risk assessment, and environmental impact quantification designed to impress judges with actionable conservation intelligence.

## Recent Changes (October 2025)

### Added Features
- **AI-Powered Insights Dashboard**: Anomaly detection, predictive forecasting, environmental impact assessment, and action recommendations
- **Multi-Biome Comparison Analysis**: Comprehensive cross-biome health rankings, comparative trend analysis, and risk assessment matrix
- **Enhanced Data Simulation**: Biome-specific characteristics with realistic environmental trends (Amazon deforestation, Cerrado water stress, Pantanal variability)
- **Date Range Synchronization**: Preset selections now persist correctly across all views
- **Modern Visual Design**: NASA-inspired dark theme with glassmorphism UI, gradient text, and responsive layouts
- **Google Earth Engine Integration**: Real-time data integration from Google Colab via REST API, allowing display of actual satellite analysis results

### Visual Design Updates
- **Dark Theme**: Deep space blue background (#0B1120) with cyan accents (#00D4FF)
- **Glassmorphism Cards**: Semi-transparent metric cards with backdrop blur effect, gradient borders, and hover animations
- **Gradient Typography**: Cyan-to-purple gradient on headers and metric values
- **Responsive Layout**: Full-width containers and adaptive map sizing for different screen sizes
- **Modern Typography**: Inter font family via Google Fonts
- **Enhanced UX**: Smooth transitions, hover effects with shadow elevation, and improved visual hierarchy

### Google Colab Integration
- **FastAPI Server**: Dedicated API server running on port 8080 for receiving data from Google Colab
- **REST Endpoints**: `/api/update-data` (POST), `/api/get-data` (GET), `/api/health` (GET), `/uploaded_data/{filename}` (GET)
- **Data Persistence**: JSON-based storage system for metrics, tables, and Base64-encoded images
- **New Dashboard View**: "Google Earth Engine Data" displays real-time analysis results from Colab
- **Automatic Updates**: Dashboard refreshes to show latest data received from Google Earth Engine analyses

### Bug Fixes
- Fixed biome differentiation: Each biome now has unique seed offsets and parameters (Amazon: veg_mean=0.85, Caatinga: veg_mean=0.40, etc.)
- Corrected date range cache invalidation: Date preset changes now properly invalidate cached data across all views
- Synchronized session state for date selections: Preset choice persists when navigating between views
- Applied !important flags to CSS for proper glassmorphism rendering across all metric cards

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework Choice**: Streamlit
- **Rationale**: Streamlit was chosen for rapid prototyping of data science applications with minimal frontend code. It provides built-in state management, reactive updates, and seamless integration with Python data science libraries.
- **Pros**: Fast development, Python-native, excellent for dashboards, built-in components
- **Cons**: Limited customization compared to traditional web frameworks, single-user session model

**Component-Based Structure**: The application uses a modular component architecture
- Each view (dashboard, insights, comparison, time series) is separated into its own component file
- **Rationale**: Improves code organization, maintainability, and allows for independent development of features
- Components located in `/components` directory include:
  - `sidebar.py` - Navigation and global controls
  - `main_dashboard.py` - Primary monitoring view
  - `insights_dashboard.py` - AI-powered analytics
  - `time_series.py` - Temporal analysis
  - `comparison_view.py` - Period-to-period comparisons
  - `multi_biome_comparison.py` - Cross-biome analysis

**Session State Management**: Leverages Streamlit's session state for data persistence
- Stores loaded data, selected regions, date ranges, and current view
- **Rationale**: Prevents unnecessary data reloading and maintains user selections across interactions
- Key state variables: `current_view`, `selected_region`, `date_range`, `data_loaded`

### Data Processing Architecture

**Processor Classes**: Object-oriented design with specialized processors in `/utils` directory

**SARDataProcessor**: Core data processing class
- Handles time series generation, metadata management, and metrics calculation
- Simulates SAR data patterns with biome-specific characteristics (currently uses synthetic data generation)
- **Design Decision**: Separated data processing logic from visualization to allow for future integration with real satellite data APIs
- **Biome Differentiation Strategy**: Each biome has unique parameters (vegetation mean, water extent, alert rates, seasonal patterns) and seed offsets for realistic comparative analysis
- Methods include: `generate_time_series_data()`, `load_sample_metadata()`, `calculate_change_metrics()`

**Biome-Specific Parameters** (for synthetic data):
- **Amazon**: High vegetation (0.85), high alerts (4.5/day), declining trend
- **Cerrado**: Medium vegetation (0.55), water stress trend
- **Pantanal**: Medium-high vegetation (0.65), high water variability (0.45 mean)
- **Atlantic Forest**: High vegetation (0.75), moderate alerts (2.8/day)
- **Caatinga**: Low vegetation (0.40), low water (0.15)
- **Pampa**: Medium vegetation (0.60), moderate parameters

**GeospatialProcessor**: Handles geographic data operations
- Integrates with GeoPandas for spatial analysis
- **Rationale**: Separates geospatial logic from general data processing

**Visualization Strategy**: Dedicated visualization class (SARVisualizer)
- Uses Plotly for interactive charts and graphs
- **Rationale**: Plotly provides rich interactivity, zoom capabilities, and professional-looking visualizations suitable for scientific data
- Standardized color schemes for different data types (vegetation, water, SAR, alerts)

### Mapping Architecture

**MapBuilder Class**: Folium-based interactive mapping
- **Technology Choice**: Folium (Python wrapper for Leaflet.js)
- **Rationale**: Provides interactive maps with layer controls, multiple tile sources, and geospatial overlays
- Features: Multiple base map options (OpenStreetMap, Satellite, Terrain), fullscreen mode, measurement tools
- Integration with Streamlit via `streamlit-folium` component

**Tile Layer Strategy**: Multiple tile providers for different visualization needs
- OpenStreetMap for general reference
- Esri satellite imagery for visual analysis
- Terrain maps for topographic context

### Data Storage

**Current Implementation**: Session-based in-memory storage
- Data generated on-demand and cached in Streamlit session state
- **Rationale**: Suitable for prototype/demo phase with synthetic data
- **Limitation**: No persistent storage between sessions

**Future Considerations**: The architecture is designed to accommodate:
- Database integration for caching processed satellite data
- Connection to real satellite data APIs (Sentinel Hub, Google Earth Engine)
- File-based storage for user preferences and analysis results

## External Dependencies

### Core Framework
- **Streamlit**: Web application framework for data science dashboards
- **Purpose**: Main application framework, UI components, and state management

### Data Processing Libraries
- **Pandas**: Tabular data manipulation and time series handling
- **NumPy**: Numerical computations and array operations
- **GeoPandas**: Geospatial data processing (extends Pandas with geographic capabilities)

### Visualization Libraries
- **Plotly**: Interactive plotting library
  - Used for time series charts, comparative analysis, and statistical visualizations
  - Provides `graph_objects` and `express` APIs for different complexity levels
- **Folium**: Interactive mapping library
  - Python wrapper for Leaflet.js
  - Enables multi-layer maps with satellite imagery and overlays
- **streamlit-folium**: Streamlit component for embedding Folium maps

### Satellite Data Sources (Referenced)
The application is designed to work with:
- **Sentinel-1 SAR**: Synthetic Aperture Radar data for all-weather monitoring
- **Landsat 8/9**: Optical satellite imagery
- **MODIS Terra/Aqua**: Moderate Resolution Imaging Spectroradiometer data
- **SRTM DEM**: Shuttle Radar Topography Mission Digital Elevation Model

**Note**: Current implementation uses synthetic data generation. Real satellite data integration would require:
- Google Earth Engine API or Sentinel Hub API
- Authentication credentials and API keys
- Additional processing libraries for raster data (rasterio, xarray)

### Python Standard Libraries
- **datetime**: Date and time manipulation for time series operations
- **json**: Configuration and metadata handling
- **os/sys**: File path management and module imports