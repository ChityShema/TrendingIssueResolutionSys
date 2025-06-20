"""Setup and run script for the Trending Issue Resolver."""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def setup_gcp_auth():
    """Check GCP authentication."""
    print("\nChecking GCP authentication...")
    try:
        # Check if gcloud is authenticated
        result = subprocess.run(["gcloud", "auth", "list"], capture_output=True, text=True)
        if "ACTIVE" in result.stdout:
            print("✓ GCP authentication found")
            return True
        else:
            print("❌ No active GCP authentication found")
            print("Please run: gcloud auth application-default login")
            return False
    except FileNotFoundError:
        print("❌ gcloud CLI not found. Please install Google Cloud SDK")
        return False

def populate_data():
    """Populate BigQuery and Datastore with sample data."""
    print("\nPopulating sample data...")
    
    # Populate BigQuery
    try:
        subprocess.check_call([sys.executable, "populate_bigquery.py"])
        print("✓ BigQuery data populated")
    except subprocess.CalledProcessError:
        print("❌ Failed to populate BigQuery data")
        return False
    
    # Populate Datastore
    try:
        subprocess.check_call([sys.executable, "populate_datastore.py"])
        print("✓ Datastore data populated")
    except subprocess.CalledProcessError:
        print("❌ Failed to populate Datastore data")
        return False
    
    return True

def run_agent():
    """Run the trending issue resolver agent."""
    print("\nRunning Trending Issue Resolver...")
    try:
        subprocess.check_call([sys.executable, "run_agent.py"])
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run agent: {e}")
        return False
    return True

def main():
    """Main setup and run function."""
    print("🚀 Trending Issue Resolver Setup")
    print("=" * 40)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        return
    
    # Step 2: Check GCP auth
    if not setup_gcp_auth():
        print("\n⚠️  Please authenticate with GCP and run this script again")
        return
    
    # Step 3: Set project ID
    project_id = input("\nEnter your GCP Project ID: ").strip()
    if project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        print(f"✓ Project ID set to: {project_id}")
    
    # Step 4: Populate data
    populate_choice = input("\nPopulate sample data? (y/n): ").strip().lower()
    if populate_choice == 'y':
        if not populate_data():
            print("⚠️  Data population failed, but you can still run the agent")
    
    # Step 5: Run agent
    run_choice = input("\nRun the agent now? (y/n): ").strip().lower()
    if run_choice == 'y':
        run_agent()
    
    print("\n✅ Setup completed!")
    print("\nTo run the agent manually:")
    print("python run_agent.py")

if __name__ == "__main__":
    main()