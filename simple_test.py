"""Simple test without ADK dependencies."""

import os
import asyncio
from datetime import datetime

# Set project ID
os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

async def test_basic_functionality():
    """Test basic GCP connections and data operations."""
    
    try:
        from google.cloud import bigquery, datastore
        
        print("🔍 Testing BigQuery...")
        bq_client = bigquery.Client()
        print(f"✓ Connected to project: {bq_client.project}")
        
        print("\n🔍 Testing Datastore...")
        ds_client = datastore.Client()
        print(f"✓ Connected to project: {ds_client.project}")
        
        print("\n🔍 Testing DatastoreTool...")
        from trending_issue_resolver.tools.datastore_tool import DatastoreTool
        ds_tool = DatastoreTool(ds_client)
        print(f"✓ DatastoreTool created: {ds_tool.name}")
        
        print("\n🔍 Testing BigQueryTool...")
        from trending_issue_resolver.tools.bigquery_tool import BigQueryTool
        bq_tool = BigQueryTool(bq_client)
        print(f"✓ BigQueryTool created: {bq_tool.name}")
        
        print("\n✅ All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())