"""Test script to verify system components."""

import asyncio
from google.cloud import bigquery, datastore

async def test_bigquery():
    """Test BigQuery connection and data."""
    print("Testing BigQuery...")
    try:
        client = bigquery.Client()
        query = f"""
        SELECT COUNT(*) as count 
        FROM `{client.project}.customer_interactions.issues`
        LIMIT 1
        """
        result = list(client.query(query).result())
        count = result[0].count
        print(f"✓ BigQuery connected - {count} issue records found")
        return True
    except Exception as e:
        print(f"❌ BigQuery error: {e}")
        return False

async def test_datastore():
    """Test Datastore connection and data."""
    print("Testing Datastore...")
    try:
        client = datastore.Client()
        
        # Test knowledge base
        kb_query = client.query(kind="knowledge_base")
        kb_count = len(list(kb_query.fetch(limit=100)))
        
        # Test response history
        resp_query = client.query(kind="response_history")
        resp_count = len(list(resp_query.fetch(limit=100)))
        
        print(f"✓ Datastore connected - {kb_count} KB articles, {resp_count} responses")
        return True
    except Exception as e:
        print(f"❌ Datastore error: {e}")
        return False

async def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from trending_issue_resolver import TrendingIssueResolverAgent
        from trending_issue_resolver.tools.bigquery_tool import BigQueryTool
        from trending_issue_resolver.tools.datastore_tool import DatastoreTool
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 System Component Tests")
    print("=" * 30)
    
    tests = [
        test_imports(),
        test_bigquery(),
        test_datastore(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    total_tests = len(results)
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("✅ All tests passed! System is ready to run.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())