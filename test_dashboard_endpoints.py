"""Test Streamlit dashboard endpoints and functionality."""

import requests
import time
from google.auth import default
from google.auth.transport.requests import Request

SERVICE_URL = "https://trending-resolver-66813571646.us-central1.run.app"

def get_auth_headers():
    """Get authentication headers."""
    credentials, project = default()
    credentials.refresh(Request())
    return {"Authorization": f"Bearer {credentials.token}"}

def test_dashboard_load():
    """Test if dashboard loads properly."""
    print("Testing dashboard load...")
    
    try:
        response = requests.get(SERVICE_URL, headers=get_auth_headers(), timeout=30)
        
        if response.status_code == 200:
            print("✅ Dashboard loaded successfully")
            
            # Check for Streamlit indicators
            if "streamlit" in response.text.lower():
                print("✅ Streamlit framework detected")
            
            # Check for dashboard content
            if "trending" in response.text.lower():
                print("✅ Dashboard content detected")
                
            return True
        else:
            print(f"❌ Dashboard failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")
        return False

def test_streamlit_health():
    """Test Streamlit health endpoint."""
    print("Testing Streamlit health...")
    
    health_url = f"{SERVICE_URL}/_stcore/health"
    
    try:
        response = requests.get(health_url, headers=get_auth_headers(), timeout=10)
        
        if response.status_code == 200:
            print("✅ Streamlit health check passed")
            return True
        else:
            print(f"❌ Streamlit health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Streamlit health: {e}")
        return False

def test_performance():
    """Test response time performance."""
    print("Testing performance...")
    
    start_time = time.time()
    
    try:
        response = requests.get(SERVICE_URL, headers=get_auth_headers(), timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Response time: {response_time:.2f} seconds")
        
        if response_time < 10:
            print("✅ Good response time")
        elif response_time < 30:
            print("⚠️ Acceptable response time")
        else:
            print("❌ Slow response time")
            
        return response_time
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Streamlit Dashboard...")
    print(f"Service URL: {SERVICE_URL}")
    print("-" * 50)
    
    # Run tests
    test_dashboard_load()
    print()
    test_streamlit_health()
    print()
    test_performance()