import streamlit as st
import requests
import threading
import time
import uvicorn
import os
import sys
import pandas as pd
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import FastAPI app
from app.main import app as fastapi_app

# Configuration
API_PORT = 9000
API_BASE = f"http://localhost:{API_PORT}"

# Global variable to track if FastAPI is already started
_fastapi_started = False

# Check if port is available
def is_port_available(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False

# Start FastAPI server in background thread for local development
def start_fastapi():
    global _fastapi_started
    if _fastapi_started:
        return
    
    if not is_port_available(API_PORT):
        print(f"Port {API_PORT} already in use, assuming FastAPI is already running")
        _fastapi_started = True
        return
        
    try:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=API_PORT, log_level="error")
    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"Port {API_PORT} already in use, assuming FastAPI is already running")
            _fastapi_started = True
        else:
            raise

# Check if we're running locally (not on Streamlit Cloud)
if not os.getenv("STREAMLIT_SHARING_MODE") and not _fastapi_started:
    # Start FastAPI in background thread
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()
    _fastapi_started = True
    time.sleep(2)  # Give FastAPI time to start

st.set_page_config(page_title="FloatChat Dashboard", layout="wide")
st.title("FloatChat Dashboard")

# Check API health first
api_healthy = False
try:
    health_response = requests.get(f"{API_BASE}/health", timeout=5)
    if health_response.status_code == 200:
        api_healthy = True
        st.success("API is running")
    else:
        st.error("API is not responding properly")
except Exception as e:
    st.error(f"Cannot connect to API: {str(e)}")
    st.info("If running locally, make sure the FastAPI server is starting up...")

if api_healthy:
    # Control buttons at the top
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("Data Management")
    
    with col2:
        if st.button("🔄 Reset Database", type="secondary"):
            with st.spinner("Resetting database..."):
                try:
                    # Try the delete method first
                    r = requests.delete(f"{API_BASE}/profiles/reset", timeout=10)
                    if r.status_code == 200:
                        result = r.json()
                        st.success(f"✅ {result.get('message', 'Database reset successfully!')}")
                        time.sleep(1)  # Brief pause before refresh
                        st.rerun()
                    else:
                        # Try alternative reset method
                        st.warning("Trying alternative reset method...")
                        r2 = requests.post(f"{API_BASE}/profiles/reset-tables", timeout=10)
                        if r2.status_code == 200:
                            result = r2.json()
                            st.success(f"✅ {result.get('message', 'Database reset successfully!')}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Both reset methods failed. Error: {r2.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Connection error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error resetting database: {str(e)}")
    
    with col3:
        if st.button("🔍 Refresh Data"):
            st.rerun()

    # Ingestion section
    st.subheader("CSV Ingestion")
    
    # Show current working directory for debugging
    current_dir = os.getcwd()
    backend_dir = Path(__file__).parent
    data_dir = backend_dir / "data"
    
    with st.expander("🔧 Debug Info"):
        if st.button("🔍 Get Debug Info"):
            try:
                debug_info = requests.get(f"{API_BASE}/ingest/debug", timeout=10).json()
                st.json(debug_info)
            except Exception as e:
                st.error(f"Error getting debug info: {e}")
                # Fallback to local debug info
                st.write(f"**Current working directory:** `{current_dir}`")
                st.write(f"**Backend directory:** `{backend_dir}`")
                st.write(f"**Data directory:** `{data_dir}`")
                st.write(f"**Data directory exists:** {data_dir.exists()}")
                if data_dir.exists():
                    csv_files = list(data_dir.glob("*.csv"))
                    st.write(f"**CSV files found:** {[f.name for f in csv_files]}")
    
    col_ing1, col_ing2 = st.columns([3, 1])
    
    with col_ing1:
        # Provide multiple path options
        default_paths = [
            str(data_dir),  # Absolute path to data directory
            "./data",
            "./data/data/csv_cleaned",  # Relative path
            "data",         # Simple relative path
            str(backend_dir / "data")  # Full backend data path
        ]
        
        folder = st.selectbox(
            "CSV folder path", 
            options=default_paths,
            help="Select or enter path to folder containing CSV files"
        )
        
        # Allow custom path input
        custom_folder = st.text_input("Or enter custom path:", placeholder="Enter custom folder path")
        if custom_folder:
            folder = custom_folder
    
    with col_ing2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        ingest_button = st.button("📥 Ingest CSVs", type="primary")
    
    st.info("💡 Select the data directory path that works for your environment")
    
    # Alternative: File upload
    st.subheader("📤 Or Upload CSV Files")
    uploaded_files = st.file_uploader(
        "Choose CSV files", 
        accept_multiple_files=True, 
        type=['csv'],
        help="Upload one or more CSV files directly"
    )
    
    if uploaded_files:
        if st.button("📥 Process Uploaded Files", type="primary"):
            with st.spinner("Processing uploaded files..."):
                processed_count = 0
                errors = []
                
                for uploaded_file in uploaded_files:
                    try:
                        # Save uploaded file temporarily
                        temp_path = backend_dir / f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Process the file using the same logic as folder ingestion
                        # This is a simplified version - in production you'd want to use the API
                        df = pd.read_csv(temp_path)
                        
                        # Basic validation
                        required_cols = ["N_PROF", "LATITUDE", "LONGITUDE"]
                        if all(col in df.columns for col in required_cols):
                            processed_count += 1
                            st.success(f"✅ Processed {uploaded_file.name}")
                        else:
                            errors.append(f"{uploaded_file.name}: Missing required columns")
                        
                        # Clean up temp file
                        temp_path.unlink(missing_ok=True)
                        
                    except Exception as e:
                        errors.append(f"{uploaded_file.name}: {str(e)}")
                
                if processed_count > 0:
                    st.success(f"🎉 Successfully processed {processed_count} files!")
                
                if errors:
                    st.error("❌ Some files had errors:")
                    for error in errors:
                        st.write(f"• {error}")
    
    if ingest_button:
        with st.spinner("Processing CSV files..."):
            try:
                r = requests.post(f"{API_BASE}/ingest/csv", params={"folder": folder}, timeout=30)
                if r.status_code == 200:
                    result = r.json()
                    st.success(f"✅ Successfully processed {result.get('processed_files', 0)} CSV files!")
                    if result.get('message'):
                        st.info(result['message'])
                else:
                    st.error(f"❌ Ingestion failed: {r.text}")
            except Exception as e:
                st.error(f"❌ Error during ingestion: {str(e)}")

    # Data Overview Section
    st.subheader("📊 Data Overview")
    
    # Get profile data
    try:
        data = requests.get(f"{API_BASE}/profiles", params={"limit": 100}, timeout=10).json()
        total_profiles = data.get("total", 0)
        
        if total_profiles > 0:
            profiles = data.get("items", [])
            
            # Summary metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.metric("Total Profiles", total_profiles)
            
            with col_m2:
                unique_floats = len(set(p.get('float_id', '') for p in profiles))
                st.metric("Unique Floats", unique_floats)
            
            with col_m3:
                if profiles:
                    lat_range = f"{min(p.get('latitude', 0) for p in profiles):.2f} to {max(p.get('latitude', 0) for p in profiles):.2f}"
                    st.metric("Latitude Range", lat_range)
            
            with col_m4:
                if profiles:
                    lon_range = f"{min(p.get('longitude', 0) for p in profiles):.2f} to {max(p.get('longitude', 0) for p in profiles):.2f}"
                    st.metric("Longitude Range", lon_range)
            
            # Profile table
            st.subheader("🗂️ Profile Summary")
            if profiles:
                df = pd.DataFrame(profiles)
                st.dataframe(df, use_container_width=True)
            
            # Expandable JSON view
            with st.expander("🔍 View Raw Profile Data (JSON)"):
                st.json(data)
                
        else:
            st.info("📝 No profiles found. Try ingesting some CSV files first.")
            
    except Exception as e:
        st.error(f"❌ Error fetching profiles: {str(e)}")

    # Trajectories Section
    st.subheader("🗺️ Trajectory Data")
    try:
        geo = requests.get(f"{API_BASE}/profiles/trajectories", timeout=10).json()
        features = geo.get("features", [])
        
        if features:
            st.success(f"✅ Found {len(features)} trajectory points")
            
            # Show trajectory summary
            if features:
                lats = [f["geometry"]["coordinates"][1] for f in features if f.get("geometry", {}).get("coordinates")]
                lons = [f["geometry"]["coordinates"][0] for f in features if f.get("geometry", {}).get("coordinates")]
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.write(f"**Latitude range:** {min(lats):.3f}° to {max(lats):.3f}°")
                with col_t2:
                    st.write(f"**Longitude range:** {min(lons):.3f}° to {max(lons):.3f}°")
            
            # Expandable GeoJSON view
            with st.expander("🔍 View GeoJSON Data"):
                st.json(geo)
                
        else:
            st.info("📍 No trajectory data available.")
            
    except Exception as e:
        st.error(f"❌ Error fetching trajectories: {str(e)}")
else:
    st.warning("API is not available. Please check the server status.")
