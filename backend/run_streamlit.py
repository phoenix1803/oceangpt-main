#!/usr/bin/env python3
"""
Simple script to run the Streamlit app locally
"""
import subprocess
import sys
import os
from pathlib import Path

def clear_port():
    """Clear port 9000 if it's in use"""
    try:
        from kill_port import kill_port_9000
        kill_port_9000()
    except Exception as e:
        print(f"Note: Could not clear port 9000: {e}")

def main():
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Clear port first
    print("Clearing port 9000...")
    clear_port()
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501"]
    
    print("Starting Streamlit app...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()