import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime, timedelta

# Generate realistic Argo float data
@st.cache_data
def generate_argo_data():
    """Generate realistic Argo float dataset"""
    np.random.seed(42)  # For reproducible data
    
    # Create 15 different floats across different ocean regions
    floats = []
    base_date = datetime(2023, 1, 1)
    
    regions = [
        {"name": "North Pacific", "lat_range": (35, 50), "lon_range": (-180, -120), "temp_base": 12},
        {"name": "South Pacific", "lat_range": (-45, -20), "lon_range": (-180, -120), "temp_base": 18},
        {"name": "North Atlantic", "lat_range": (40, 60), "lon_range": (-60, -10), "temp_base": 10},
        {"name": "South Atlantic", "lat_range": (-40, -10), "lon_range": (-50, 10), "temp_base": 20},
        {"name": "Indian Ocean", "lat_range": (-30, 10), "lon_range": (40, 100), "temp_base": 22},
    ]
    
    float_id = 1
    for region in regions:
        for i in range(3):  # 3 floats per region
            # Generate float trajectory over 2 years
            n_profiles = random.randint(80, 120)
            
            # Starting position
            start_lat = np.random.uniform(*region["lat_range"])
            start_lon = np.random.uniform(*region["lon_range"])
            
            for profile_num in range(1, n_profiles + 1):
                # Drift simulation
                days_elapsed = profile_num * 10  # Profile every 10 days
                drift_lat = start_lat + np.random.normal(0, 0.1) * profile_num * 0.01
                drift_lon = start_lon + np.random.normal(0, 0.1) * profile_num * 0.01
                
                # Keep within reasonable bounds
                drift_lat = np.clip(drift_lat, region["lat_range"][0], region["lat_range"][1])
                drift_lon = np.clip(drift_lon, region["lon_range"][0], region["lon_range"][1])
                
                # Generate depth profile (0-2000m)
                depths = np.array([0, 10, 20, 30, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 600, 750, 1000, 1250, 1500, 2000])
                
                for depth in depths:
                    # Temperature decreases with depth
                    temp_surface = region["temp_base"] + np.random.normal(0, 2)
                    temp = temp_surface * np.exp(-depth / 1000) + np.random.normal(0, 0.5)
                    temp = max(temp, 2)  # Minimum deep water temp
                    
                    # Salinity varies by region and depth
                    sal_base = 34.5 + np.random.normal(0, 0.3)
                    salinity = sal_base + (depth / 2000) * 0.5 + np.random.normal(0, 0.1)
                    salinity = np.clip(salinity, 33, 37)
                    
                    floats.append({
                        'float_id': f'ARGO_{float_id:04d}',
                        'n_prof': profile_num,
                        'latitude': round(drift_lat, 4),
                        'longitude': round(drift_lon, 4),
                        'pressure': depth,
                        'temperature': round(temp, 2),
                        'salinity': round(salinity, 3),
                        'date': base_date + timedelta(days=days_elapsed),
                        'region': region["name"]
                    })
            
            float_id += 1
    
    return pd.DataFrame(floats)

# Hardcoded chat responses
CHAT_RESPONSES = {
    "describe the dataset": """
🌊 **Argo Float Dataset Overview**

This dataset contains oceanographic measurements from 15 autonomous Argo floats deployed across major ocean basins:

📍 **Geographic Coverage:**
- North Pacific: 3 floats (35°N-50°N, 120°W-180°W)
- South Pacific: 3 floats (20°S-45°S, 120°W-180°W)  
- North Atlantic: 3 floats (40°N-60°N, 10°W-60°W)
- South Atlantic: 3 floats (10°S-40°S, 50°W-10°E)
- Indian Ocean: 3 floats (30°S-10°N, 40°E-100°E)

📊 **Data Characteristics:**
- **Total Profiles:** ~1,500 vertical profiles
- **Depth Range:** 0-2000 meters
- **Temporal Coverage:** 2+ years of continuous monitoring
- **Measurements:** Temperature, Salinity, Pressure
- **Sampling Frequency:** Every 10 days per float

🔬 **Scientific Value:**
This dataset captures seasonal and regional variations in ocean temperature and salinity, essential for understanding ocean circulation, climate patterns, and marine ecosystem dynamics.
    """,
    
    "describe the graphs": """
📈 **Visualization Guide**

**🗺️ Float Trajectory Map:**
- Shows the drift paths of all 15 Argo floats
- Color-coded by ocean region
- Interactive: hover for float details
- Reveals ocean current patterns and float dispersion

**🌡️ Temperature-Salinity Profiles:**
- Vertical profiles showing T-S relationships with depth
- Each line represents one float's average profile
- Reveals water mass characteristics and stratification
- Thermocline and halocline clearly visible

**📊 Regional Comparison Charts:**
- Box plots comparing temperature/salinity by region
- Shows regional oceanographic differences
- Identifies warm/cold and fresh/saline water masses

**⏱️ Time Series Analysis:**
- Temporal evolution of surface conditions
- Seasonal cycles and long-term trends
- Useful for climate change studies

**🎯 Interactive Filters:**
- Filter by region, depth range, or time period
- Zoom into specific areas of interest
- Compare different ocean basins
    """,
    
    "what is argo": """
🤖 **About Argo Floats**

Argo is a global network of autonomous profiling floats that measure temperature and salinity in the upper 2000m of the ocean.

**How They Work:**
1. **Drift Phase:** Float drifts at ~1000m depth for 9-10 days
2. **Profile Phase:** Descends to 2000m, then rises to surface measuring T/S
3. **Surface Phase:** Transmits data via satellite, gets GPS position
4. **Repeat:** Cycle repeats ~150 times over 4-5 years

**Global Impact:**
- 🌍 4000+ active floats worldwide
- 📡 Real-time data transmission
- 🌊 Critical for weather/climate prediction
- 🔬 Supports oceanographic research
- 📈 Provides data for climate models

**This Demo:**
Our dataset simulates realistic Argo measurements, showcasing the type of valuable oceanographic data these remarkable instruments collect!
    """,
    
    "temperature patterns": """
🌡️ **Temperature Patterns Analysis**

**Vertical Structure:**
- **Surface Layer (0-100m):** Warmest, varies by region (10-25°C)
- **Thermocline (100-1000m):** Rapid temperature decrease
- **Deep Water (>1000m):** Cold, stable (~2-4°C)

**Regional Variations:**
- **Tropical Regions:** Warmest surface temperatures
- **Polar Regions:** Coldest throughout water column
- **Seasonal Cycles:** Most pronounced in mid-latitudes

**Key Findings:**
- Indian Ocean shows highest surface temperatures
- North Atlantic exhibits strong seasonal variability
- Deep water temperatures remarkably consistent globally
    """,
    
    "salinity patterns": """🧂 **Salinity Patterns Analysis**

**Vertical Distribution:**
- **Surface:** Highly variable (33-37 PSU)
- **Subsurface:** Often shows salinity maximum
- **Deep Water:** More uniform (~34.5-35 PSU)

**Regional Characteristics:**
- **Subtropical Gyres:** High surface salinity (evaporation > precipitation)
- **Polar Regions:** Lower salinity (ice melt, precipitation)
- **Equatorial Regions:** Variable due to rainfall patterns

**Ocean Circulation Indicators:**
- Salinity helps identify different water masses
- Critical for understanding thermohaline circulation
- Reveals mixing processes and water mass origins
    """
}

def get_chat_response(question):
    """Get hardcoded chat response"""
    question_lower = question.lower().strip()
    
    # Find best matching response
    for key, response in CHAT_RESPONSES.items():
        if key in question_lower:
            return response
    
    # Default responses for common patterns
    if any(word in question_lower for word in ['temperature', 'temp', 'warm', 'cold']):
        return CHAT_RESPONSES["temperature patterns"]
    elif any(word in question_lower for word in ['salinity', 'salt', 'fresh']):
        return CHAT_RESPONSES["salinity patterns"]
    elif any(word in question_lower for word in ['graph', 'chart', 'plot', 'visualization']):
        return CHAT_RESPONSES["describe the graphs"]
    elif any(word in question_lower for word in ['data', 'dataset', 'information']):
        return CHAT_RESPONSES["describe the dataset"]
    elif any(word in question_lower for word in ['argo', 'float', 'buoy']):
        return CHAT_RESPONSES["what is argo"]
    else:
        return """
🤔 **I can help you with:**

• **"Describe the dataset"** - Overview of the Argo data
• **"Describe the graphs"** - Explanation of visualizations  
• **"What is Argo?"** - About Argo float technology
• **"Temperature patterns"** - Analysis of temperature data
• **"Salinity patterns"** - Analysis of salinity data

Try asking about any of these topics! 🌊
        """

# Main App
st.set_page_config(
    page_title="🌊 Argo Float Explorer", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the hardcoded data
df = generate_argo_data()

# Sidebar for navigation and filters
with st.sidebar:
    st.title("🌊 Argo Explorer")
    st.markdown("---")
    
    # Navigation
    page = st.selectbox(
        "📍 Navigate to:",
        ["🏠 Dashboard", "🗺️ Float Trajectories", "📊 Data Analysis", "💬 Chat Assistant"]
    )
    
    st.markdown("---")
    
    # Filters
    st.subheader("🎛️ Filters")
    
    # Region filter
    regions = ["All Regions"] + sorted(df['region'].unique().tolist())
    selected_region = st.selectbox("🌍 Ocean Region:", regions)
    
    # Float filter
    if selected_region != "All Regions":
        available_floats = ["All Floats"] + sorted(df[df['region'] == selected_region]['float_id'].unique().tolist())
    else:
        available_floats = ["All Floats"] + sorted(df['float_id'].unique().tolist())
    selected_float = st.selectbox("🤖 Float ID:", available_floats)
    
    # Depth filter
    depth_range = st.slider(
        "🌊 Depth Range (m):",
        min_value=0,
        max_value=2000,
        value=(0, 500),
        step=50
    )
    
    # Date filter
    date_range = st.date_input(
        "📅 Date Range:",
        value=(df['date'].min().date(), df['date'].max().date()),
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_region != "All Regions":
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if selected_float != "All Floats":
        filtered_df = filtered_df[filtered_df['float_id'] == selected_float]
    
    filtered_df = filtered_df[
        (filtered_df['pressure'] >= depth_range[0]) & 
        (filtered_df['pressure'] <= depth_range[1])
    ]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) & 
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    
    st.markdown("---")
    st.info(f"📊 **{len(filtered_df):,}** measurements selected")

# Main content area
if page == "🏠 Dashboard":
    st.title("🌊 Argo Float Data Explorer")
    st.markdown("### Real-time Oceanographic Monitoring Dashboard")
    
    # Simulate "loading" effect
    if st.button("🔄 Refresh Data", type="primary"):
        with st.spinner("Fetching latest data from Argo network..."):
            time.sleep(1)
        st.success("✅ Data refreshed successfully!")
        st.rerun()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🤖 Active Floats", 
            len(filtered_df['float_id'].unique()),
            delta=f"+{random.randint(1,3)} this week"
        )
    
    with col2:
        st.metric(
            "📊 Total Profiles", 
            len(filtered_df['n_prof'].unique()),
            delta=f"+{random.randint(10,50)} today"
        )
    
    with col3:
        avg_temp = filtered_df['temperature'].mean()
        st.metric(
            "🌡️ Avg Temperature", 
            f"{avg_temp:.1f}°C",
            delta=f"{random.uniform(-0.5, 0.5):.1f}°C"
        )
    
    with col4:
        avg_sal = filtered_df['salinity'].mean()
        st.metric(
            "🧂 Avg Salinity", 
            f"{avg_sal:.2f} PSU",
            delta=f"{random.uniform(-0.1, 0.1):.2f} PSU"
        )
    
    # Recent activity simulation
    st.subheader("📡 Recent Float Activity")
    
    # Create fake recent activity
    recent_activity = []
    for i in range(5):
        float_id = random.choice(filtered_df['float_id'].unique())
        activity_time = datetime.now() - timedelta(hours=random.randint(1, 24))
        recent_activity.append({
            "Time": activity_time.strftime("%Y-%m-%d %H:%M"),
            "Float ID": float_id,
            "Status": random.choice(["✅ Profile Complete", "📡 Data Transmitted", "🌊 Surfacing", "⬇️ Descending"]),
            "Location": f"{random.uniform(-60, 60):.2f}°, {random.uniform(-180, 180):.2f}°"
        })
    
    activity_df = pd.DataFrame(recent_activity)
    st.dataframe(activity_df, use_container_width=True)
    
    # Quick stats
    st.subheader("📈 Quick Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature distribution
        fig_temp = px.histogram(
            filtered_df, 
            x='temperature', 
            nbins=30,
            title="🌡️ Temperature Distribution",
            color_discrete_sequence=['#FF6B6B']
        )
        fig_temp.update_layout(height=300)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Salinity distribution
        fig_sal = px.histogram(
            filtered_df, 
            x='salinity', 
            nbins=30,
            title="🧂 Salinity Distribution",
            color_discrete_sequence=['#4ECDC4']
        )
        fig_sal.update_layout(height=300)
        st.plotly_chart(fig_sal, use_container_width=True)

elif page == "🗺️ Float Trajectories":
    st.title("🗺️ Argo Float Trajectories")
    st.markdown("### Interactive map showing float positions and drift patterns")
    
    # Create trajectory map
    fig_map = px.scatter_mapbox(
        filtered_df.groupby(['float_id', 'latitude', 'longitude']).first().reset_index(),
        lat='latitude',
        lon='longitude',
        color='region',
        hover_data=['float_id', 'temperature', 'salinity'],
        mapbox_style='open-street-map',
        title="🌍 Global Argo Float Positions",
        height=600,
        zoom=1
    )
    
    fig_map.update_layout(
        mapbox=dict(
            center=dict(lat=0, lon=0),
            zoom=1
        )
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Float trajectory details
    st.subheader("🛤️ Individual Float Trajectories")
    
    if selected_float != "All Floats":
        float_data = filtered_df[filtered_df['float_id'] == selected_float]
        
        # Create trajectory line plot
        trajectory_data = float_data.groupby(['n_prof', 'latitude', 'longitude', 'date']).first().reset_index()
        trajectory_data = trajectory_data.sort_values('date')
        
        fig_traj = px.line_mapbox(
            trajectory_data,
            lat='latitude',
            lon='longitude',
            hover_data=['n_prof', 'date'],
            mapbox_style='open-street-map',
            title=f"🛤️ Trajectory for {selected_float}",
            height=500
        )
        
        st.plotly_chart(fig_traj, use_container_width=True)
        
        # Trajectory statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Total Positions", len(trajectory_data))
        with col2:
            distance = np.sqrt(
                (trajectory_data['latitude'].iloc[-1] - trajectory_data['latitude'].iloc[0])**2 +
                (trajectory_data['longitude'].iloc[-1] - trajectory_data['longitude'].iloc[0])**2
            ) * 111  # Rough km conversion
            st.metric("🏃 Distance Traveled", f"{distance:.0f} km")
        with col3:
            days = (trajectory_data['date'].iloc[-1] - trajectory_data['date'].iloc[0]).days
            st.metric("⏱️ Mission Duration", f"{days} days")

elif page == "📊 Data Analysis":
    st.title("📊 Oceanographic Data Analysis")
    st.markdown("### Detailed analysis of temperature and salinity profiles")
    
    # Temperature-Salinity profiles
    st.subheader("🌡️ Temperature vs Depth Profiles")
    
    # Create T-S diagram
    profile_data = filtered_df.groupby(['float_id', 'pressure']).agg({
        'temperature': 'mean',
        'salinity': 'mean',
        'region': 'first'
    }).reset_index()
    
    fig_temp_depth = px.line(
        profile_data,
        x='temperature',
        y='pressure',
        color='region',
        line_group='float_id',
        title="🌡️ Temperature Profiles by Region",
        labels={'pressure': 'Depth (m)', 'temperature': 'Temperature (°C)'}
    )
    fig_temp_depth.update_yaxis(autorange='reversed')
    fig_temp_depth.update_layout(height=500)
    st.plotly_chart(fig_temp_depth, use_container_width=True)
    
    # Salinity profiles
    st.subheader("🧂 Salinity vs Depth Profiles")
    
    fig_sal_depth = px.line(
        profile_data,
        x='salinity',
        y='pressure',
        color='region',
        line_group='float_id',
        title="🧂 Salinity Profiles by Region",
        labels={'pressure': 'Depth (m)', 'salinity': 'Salinity (PSU)'}
    )
    fig_sal_depth.update_yaxis(autorange='reversed')
    fig_sal_depth.update_layout(height=500)
    st.plotly_chart(fig_sal_depth, use_container_width=True)
    
    # Regional comparison
    st.subheader("🌍 Regional Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature by region
        fig_temp_region = px.box(
            filtered_df[filtered_df['pressure'] <= 100],  # Surface waters
            x='region',
            y='temperature',
            title="🌡️ Surface Temperature by Region (0-100m)",
            color='region'
        )
        fig_temp_region.update_xaxis(tickangle=45)
        st.plotly_chart(fig_temp_region, use_container_width=True)
    
    with col2:
        # Salinity by region
        fig_sal_region = px.box(
            filtered_df[filtered_df['pressure'] <= 100],
            x='region',
            y='salinity',
            title="🧂 Surface Salinity by Region (0-100m)",
            color='region'
        )
        fig_sal_region.update_xaxis(tickangle=45)
        st.plotly_chart(fig_sal_region, use_container_width=True)
    
    # Time series analysis
    if selected_float != "All Floats":
        st.subheader("⏱️ Time Series Analysis")
        
        float_data = filtered_df[filtered_df['float_id'] == selected_float]
        surface_data = float_data[float_data['pressure'] <= 50].groupby('date').agg({
            'temperature': 'mean',
            'salinity': 'mean'
        }).reset_index()
        
        fig_ts = make_subplots(
            rows=2, cols=1,
            subplot_titles=('🌡️ Surface Temperature Over Time', '🧂 Surface Salinity Over Time'),
            vertical_spacing=0.1
        )
        
        fig_ts.add_trace(
            go.Scatter(x=surface_data['date'], y=surface_data['temperature'], 
                      name='Temperature', line=dict(color='red')),
            row=1, col=1
        )
        
        fig_ts.add_trace(
            go.Scatter(x=surface_data['date'], y=surface_data['salinity'], 
                      name='Salinity', line=dict(color='blue')),
            row=2, col=1
        )
        
        fig_ts.update_layout(height=500, title_text=f"📈 {selected_float} Time Series")
        st.plotly_chart(fig_ts, use_container_width=True)

elif page == "💬 Chat Assistant":
    st.title("💬 Argo Data Assistant")
    st.markdown("### Ask me anything about the oceanographic data!")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Argo data assistant. Ask me about the dataset, graphs, or oceanographic patterns! 🌊"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about the data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                time.sleep(1)  # Simulate processing
                response = get_chat_response(prompt)
                st.markdown(response)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick question buttons
    st.markdown("---")
    st.markdown("**💡 Quick Questions:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Describe Dataset"):
            st.session_state.messages.append({"role": "user", "content": "Describe the dataset"})
            st.session_state.messages.append({"role": "assistant", "content": CHAT_RESPONSES["describe the dataset"]})
            st.rerun()
    
    with col2:
        if st.button("📈 Explain Graphs"):
            st.session_state.messages.append({"role": "user", "content": "Describe the graphs"})
            st.session_state.messages.append({"role": "assistant", "content": CHAT_RESPONSES["describe the graphs"]})
            st.rerun()
    
    with col3:
        if st.button("🤖 What is Argo?"):
            st.session_state.messages.append({"role": "user", "content": "What is Argo?"})
            st.session_state.messages.append({"role": "assistant", "content": CHAT_RESPONSES["what is argo"]})
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🌊 Argo Float Explorer | Real-time Oceanographic Data Analysis<br>
        Data simulated for demonstration purposes | Built with Streamlit & Plotly
    </div>
    """, 
    unsafe_allow_html=True
)