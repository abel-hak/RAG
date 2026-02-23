@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%
streamlit run app.py
