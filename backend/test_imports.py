#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False

    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False

    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False

    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Testing imports...")
    if test_imports():
        print("\n🎉 All imports successful! Ready to run the app.")
    else:
        print("\n⚠️  Some imports failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")