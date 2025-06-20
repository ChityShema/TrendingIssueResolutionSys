@echo off
echo ========================================
echo  Trending Issue Resolver Dashboard
echo ========================================
echo.
echo Starting local dashboard...
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.
cd /d "%~dp0"
python -m streamlit run trending_issue_resolver/dashboard/dashboard.py --server.port=8501 --server.address=0.0.0.0