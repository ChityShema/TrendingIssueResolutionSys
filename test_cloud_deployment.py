"""Integration tests for deployed Cloud Run service."""

import requests
import json
import os
from google.auth import default
from google.auth.transport.requests import Request

# Your deployed service URL
SERVICE_URL = "https://trending-resolver-66813571646.us-central1.run.app"

def get_auth_token():
    """Get authentication token for Cloud Run."""
    credentials, project = default()
    credentials.refresh(Request())
    return credentials.token

def test_service_health():
    """Test if the service is accessible."""
    try:
        headers = {"Authorization": f"Bearer {get_auth_token()}"}
        response = requests.get(SERVICE_URL, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Service is running successfully!")
            return True
        else:
            print(f"❌ Service returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to service: {e}")
        return False

def test_streamlit_dashboard():
    """Test Streamlit dashboard endpoints."""
    endpoints = [
        "/",
        "/_stcore/health",
        "/_stcore/allowed-message-origins",
    ]
    
    headers = {"Authorization": f"Bearer {get_auth_token()}"}
    
    for endpoint in endpoints:
        try:
            url = f"{SERVICE_URL}{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"Error testing {endpoint}: {e}")

def test_service_logs():
    """Check service logs for errors."""
    import subprocess
    try:
        result = subprocess.run([
            "gcloud", "run", "services", "logs", "read", "trending-resolver",
            "--region=us-central1", "--limit=10"
        ], capture_output=True, text=True)
        
        print("Recent logs:")
        print(result.stdout)
        
        if "ERROR" in result.stdout:
            print("⚠️ Errors found in logs")
        else:
            print("✅ No errors in recent logs")
            
    except Exception as e:
        print(f"Error reading logs: {e}")

if __name__ == "__main__":
    print("🧪 Testing deployed Cloud Run service...")
    print(f"Service URL: {SERVICE_URL}")
    print("-" * 50)
    
    # Run tests
    test_service_health()
    print()
    test_streamlit_dashboard()
    print()
    test_service_logs()