"""Deploy Trending Issue Resolver to Google Cloud using Vertex AI Agent Engines."""

import vertexai
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Cloud configuration
cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT", "hacker2025-team-98-dev")
cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "trending-resolver-bucket")

print(f"cloud_project={cloud_project}")
print(f"cloud_location={cloud_location}")
print(f"storage_bucket={storage_bucket}")

# Initialize Vertex AI
vertexai.init(
    project=cloud_project,
    location=cloud_location,
    staging_bucket=f"gs://{storage_bucket}",
)

print("-" * 50)
print("Deploying Trending Issue Resolver...")

try:
    # Import the main agent
    from trending_issue_resolver.agent import TrendingIssueResolverAgent
    
    # Create the root agent
    root_agent = TrendingIssueResolverAgent()
    
    # Create ADK App
    app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    
    # Package file (will be created by setup.py)
    AGENT_WHL_FILE = "./trending_issue_resolver-0.1.0-py3-none-any.whl"
    
    print("Deploying agent to Vertex AI Agent Engine...")
    remote_app = agent_engines.create(
        app,
        requirements=[
            "google-cloud-bigquery>=3.11.0",
            "google-cloud-datastore>=2.18.0", 
            "google-cloud-aiplatform>=1.38.0",
            "requests>=2.31.0",
            AGENT_WHL_FILE,
        ],
        extra_packages=[
            AGENT_WHL_FILE,
        ],
    )
    print("✅ Agent deployed to Vertex AI Agent Engine successfully!")
    print("-" * 50)
    
    # Test deployment
    print("🧪 Testing deployment...")
    session = remote_app.create_session(user_id="test_user")
    
    test_message = "Detect trending issues and generate resolution"
    print(f"Sending test message: {test_message}")
    
    for event in remote_app.stream_query(
        user_id="test_user",
        session_id=session["id"],
        message=test_message,
    ):
        print(f"Response: {event}")
    
    print("✅ Deployment test completed!")
    print("-" * 50)
    
    print("🚀 Trending Issue Resolver deployed successfully!")
    print(f"Agent Engine ID: {remote_app.id}")
    print(f"Project: {cloud_project}")
    print(f"Location: {cloud_location}")
    
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    import traceback
    traceback.print_exc()