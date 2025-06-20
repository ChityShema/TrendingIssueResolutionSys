"""Simple load test for the deployed service."""

import requests
import time
import threading
from google.auth import default
from google.auth.transport.requests import Request

SERVICE_URL = "https://trending-resolver-66813571646.us-central1.run.app"

def get_auth_headers():
    """Get authentication headers."""
    credentials, project = default()
    credentials.refresh(Request())
    return {"Authorization": f"Bearer {credentials.token}"}

def make_request():
    """Make a single request to the service."""
    try:
        start_time = time.time()
        response = requests.get(SERVICE_URL, headers=get_auth_headers(), timeout=30)
        end_time = time.time()
        
        return {
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": 0,
            "response_time": 0,
            "success": False,
            "error": str(e)
        }

def load_test(num_requests=5, concurrent=2):
    """Run a simple load test."""
    print(f"Running load test: {num_requests} requests, {concurrent} concurrent")
    
    results = []
    threads = []
    
    def worker():
        result = make_request()
        results.append(result)
    
    # Start threads
    for i in range(min(num_requests, concurrent)):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Stagger requests slightly
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Analyze results
    successful = sum(1 for r in results if r["success"])
    avg_response_time = sum(r["response_time"] for r in results if r["success"]) / max(successful, 1)
    
    print(f"Results:")
    print(f"  Successful requests: {successful}/{len(results)}")
    print(f"  Average response time: {avg_response_time:.2f}s")
    print(f"  Success rate: {successful/len(results)*100:.1f}%")

if __name__ == "__main__":
    load_test()