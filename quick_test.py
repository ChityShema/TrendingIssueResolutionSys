"""Quick test of system components without full setup."""

import os

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")
    
    try:
        import google.cloud.bigquery
        print("✓ BigQuery SDK installed")
    except ImportError:
        print("❌ BigQuery SDK missing: pip install google-cloud-bigquery")
        return False
    
    try:
        import google.cloud.datastore
        print("✓ Datastore SDK installed")
    except ImportError:
        print("❌ Datastore SDK missing: pip install google-cloud-datastore")
        return False
    
    try:
        import google.cloud.aiplatform
        print("✓ AI Platform SDK installed")
    except ImportError:
        print("❌ AI Platform SDK missing: pip install google-cloud-aiplatform")
        return False
    
    return True

def test_project_setup():
    """Test project configuration."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project_id:
        print(f"✓ Project ID set: {project_id}")
        return True
    else:
        print("❌ Project ID not set")
        print("Set with: set GOOGLE_CLOUD_PROJECT=your-project-id")
        return False

def main():
    """Run quick tests."""
    print("🧪 Quick System Test")
    print("=" * 20)
    
    if not test_imports():
        print("\n❌ Install missing packages first")
        return
    
    if not test_project_setup():
        print("\n❌ Set your project ID first")
        return
    
    print("\n✅ Basic setup looks good!")
    print("\nNext steps:")
    print("1. Install Google Cloud SDK OR use service account key")
    print("2. Run: python populate_bigquery.py")
    print("3. Run: python populate_datastore.py") 
    print("4. Run: python run_agent.py")

if __name__ == "__main__":
    main()