"""Run the system without gcloud CLI using service account."""

import os
import asyncio
from datetime import datetime

# Set your project ID here
PROJECT_ID = "your-project-id-here"

# Set path to your service account key file
# Download from: Console > IAM & Admin > Service Accounts > Create Key
SERVICE_ACCOUNT_KEY = "path/to/your/service-account-key.json"

async def main():
    """Run without gcloud CLI."""
    
    # Set environment variables
    os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY
    
    print(f"🚀 Running with Project: {PROJECT_ID}")
    
    try:
        # Test connections first
        print("Testing connections...")
        
        from google.cloud import bigquery, datastore
        
        # Test BigQuery
        bq_client = bigquery.Client()
        print(f"✓ BigQuery connected to project: {bq_client.project}")
        
        # Test Datastore  
        ds_client = datastore.Client()
        print(f"✓ Datastore connected to project: {ds_client.project}")
        
        # Now run the agent
        from trending_issue_resolver import TrendingIssueResolverAgent
        from google.adk.managers import SessionManager
        from google.adk.agents import AgentContext
        
        agent = TrendingIssueResolverAgent()
        session_manager = SessionManager()
        session = session_manager.create_session()
        
        context = AgentContext(
            session=session,
            current_time=datetime.now()
        )
        
        print("\n🔍 Running trending issue detection...")
        result = await agent.process(context)
        
        print("\n✅ Agent completed successfully!")
        print(f"Summary: {result.get('summary', 'None')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())