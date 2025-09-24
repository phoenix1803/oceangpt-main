@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting FloatChat Dashboard...
python run_streamlit.py

pause