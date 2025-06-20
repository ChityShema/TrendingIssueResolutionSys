FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and setuptools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e . || echo "Package install failed, continuing..."

# Expose port for Streamlit dashboard
EXPOSE 8501

# Set environment variables
ENV GOOGLE_CLOUD_PROJECT=hacker2025-team-98-dev
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["streamlit", "run", "trending_issue_resolver/dashboard/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]