@echo off
echo Starting Trending Issue Resolver Dashboard locally...
echo.
echo This will start the Streamlit dashboard on http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
streamlit run trending_issue_resolver/dashboard/dashboard.py --server.port=8501 --server.address=localhost