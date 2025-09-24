#!/usr/bin/env python3
"""
Kill any process running on port 9000
"""
import subprocess
import sys
import os

def kill_port_9000():
    try:
        if os.name == 'nt':  # Windows
            # Find process using port 9000
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if ':9000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"Killing process {pid} on port 9000")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        
        else:  # Unix/Linux/Mac
            result = subprocess.run(['lsof', '-ti:9000'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    print(f"Killing process {pid} on port 9000")
                    subprocess.run(['kill', '-9', pid])
                    
        print("Port 9000 cleared!")
        
    except Exception as e:
        print(f"Error clearing port: {e}")

if __name__ == "__main__":
    kill_port_9000()