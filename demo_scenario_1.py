"""Demo Scenario 1: Authentication Crisis - High Volume Login Issues"""

import os
from datetime import datetime, timedelta
import random
from google.cloud import bigquery, datastore

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

def clear_existing_data():
    """Clear existing demo data (skip BigQuery DELETE due to streaming buffer)."""
    print("🧹 Clearing existing data...")
    
    # Skip BigQuery DELETE due to streaming buffer limitation
    print("⚠️  Skipping BigQuery clear (streaming buffer limitation)")
    
    # Clear Datastore
    ds_client = datastore.Client()
    
    try:
        # Clear knowledge base
        kb_query = ds_client.query(kind="knowledge_base")
        kb_entities = list(kb_query.fetch())
        for entity in kb_entities:
            ds_client.delete(entity.key)
        
        # Clear response history
        resp_query = ds_client.query(kind="response_history")
        resp_entities = list(resp_query.fetch())
        for entity in resp_entities:
            ds_client.delete(entity.key)
        
        # Clear human interventions
        hi_query = ds_client.query(kind="human_interventions")
        hi_entities = list(hi_query.fetch())
        for entity in hi_entities:
            ds_client.delete(entity.key)
            
        print("✅ Datastore data cleared")
    except Exception as e:
        print(f"⚠️  Datastore clear warning: {e}")
    
    print("✅ Data clear completed")

def setup_scenario_1():
    """Scenario 1: Authentication Crisis - Major login outage affecting hundreds of users"""
    print("🚨 Setting up Scenario 1: Authentication Crisis")
    
    bq_client = bigquery.Client()
    ds_client = datastore.Client()
    
    # BigQuery Issues - Authentication Crisis
    issues = []
    now = datetime.utcnow()
    
    # Massive authentication failures (trending)
    for i in range(45):
        issues.append({
            "issue_id": f"AUTH_CRISIS_{1000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 30))).isoformat(),
            "content": "Critical: Users unable to authenticate. Login service returning 500 errors. OAuth tokens failing validation.",
            "category": "authentication",
            "priority": 4,  # Critical
            "status": "open"
        })
    
    # Payment processing affected by auth issues
    for i in range(25):
        issues.append({
            "issue_id": f"PAY_AUTH_{2000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(5, 35))).isoformat(),
            "content": "Payment checkout failing due to authentication service unavailable. Users cannot complete purchases.",
            "category": "payment",
            "priority": 3,  # High
            "status": "open"
        })
    
    # API gateway issues
    for i in range(18):
        issues.append({
            "issue_id": f"API_AUTH_{3000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(10, 40))).isoformat(),
            "content": "API requests failing authentication. Third-party integrations unable to connect.",
            "category": "api",
            "priority": 3,  # High
            "status": "open"
        })
    
    # Insert BigQuery data
    table_id = f"{bq_client.project}.customer_interactions.issues"
    errors = bq_client.insert_rows_json(table_id, issues)
    if not errors:
        print(f"✅ Inserted {len(issues)} critical issues into BigQuery")
    
    # Datastore Knowledge Base - Authentication focused
    kb_articles = [
        {
            "title": "Critical Authentication Service Recovery",
            "issue_type": "authentication",
            "product_area": "user_management",
            "content": "CRITICAL: 1. Restart auth service cluster 2. Clear Redis cache 3. Regenerate JWT keys 4. Update load balancer config 5. Monitor error rates",
            "status": "active",
            "success_rate": 95,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "OAuth Token Validation Failures",
            "issue_type": "authentication", 
            "product_area": "user_management",
            "content": "Token validation issues: 1. Check token expiry settings 2. Verify signing keys 3. Restart token service 4. Clear token cache",
            "status": "active",
            "success_rate": 88,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Payment Authentication Dependencies",
            "issue_type": "payment",
            "product_area": "billing",
            "content": "When auth fails, payments break: 1. Enable payment bypass mode 2. Queue failed transactions 3. Retry after auth recovery",
            "status": "active",
            "success_rate": 92,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "API Gateway Authentication Troubleshooting",
            "issue_type": "api",
            "product_area": "platform",
            "content": "API auth failures: 1. Check gateway health 2. Verify auth service connectivity 3. Update API keys 4. Restart gateway instances",
            "status": "active",
            "success_rate": 85,
            "last_updated": datetime.utcnow().timestamp()
        }
    ]
    
    for article in kb_articles:
        key = ds_client.key("knowledge_base")
        entity = datastore.Entity(key=key)
        entity.update(article)
        ds_client.put(entity)
    
    print(f"✅ Created {len(kb_articles)} knowledge base articles")
    
    # Sample resolution history
    resolution = {
        "timestamp": (datetime.utcnow() - timedelta(hours=2)).timestamp(),
        "issue_type": "authentication",
        "product_area": "user_management",
        "issue_summary": {
            "issue_type": "authentication",
            "product_area": "user_management",
            "count": 67,
            "description": "Previous authentication outage resolved"
        },
        "resolution": {
            "resolution_text": "Successfully resolved authentication service outage by restarting cluster and clearing cache",
            "estimated_resolution_time": "45 minutes"
        },
        "channels": ["email", "slack", "dashboard"],
        "metrics": {
            "affected_customers": 67,
            "resolution_time": 45,
            "success_rate": 98
        }
    }
    
    key = ds_client.key("response_history")
    entity = datastore.Entity(key=key)
    entity.update(resolution)
    ds_client.put(entity)
    
    print("✅ Scenario 1 setup complete!")
    print("📊 Data Summary:")
    print(f"   - Authentication issues: 45 (CRITICAL)")
    print(f"   - Payment issues: 25 (HIGH)")
    print(f"   - API issues: 18 (HIGH)")
    print(f"   - Total affected: ~88 users")
    print(f"   - Knowledge base: 4 articles")

if __name__ == "__main__":
    clear_existing_data()
    setup_scenario_1()
    print("\n🚀 Ready for demo! Run: streamlit run trending_issue_resolver/dashboard/dashboard.py")