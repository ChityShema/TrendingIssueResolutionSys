"""Demo Scenario 2: E-commerce Peak Traffic - Payment & Performance Issues"""

import os
from datetime import datetime, timedelta
import random
from google.cloud import bigquery, datastore

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

def clear_existing_data():
    """Clear existing demo data."""
    print("🧹 Clearing existing data...")
    
    # Clear BigQuery
    bq_client = bigquery.Client()
    bq_client.query(f"DELETE FROM `{bq_client.project}.customer_interactions.issues` WHERE TRUE").result()
    
    # Clear Datastore
    ds_client = datastore.Client()
    
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
    
    print("✅ Data cleared")

def setup_scenario_2():
    """Scenario 2: E-commerce Peak Traffic - Black Friday style load issues"""
    print("🛒 Setting up Scenario 2: E-commerce Peak Traffic")
    
    bq_client = bigquery.Client()
    ds_client = datastore.Client()
    
    # BigQuery Issues - E-commerce Peak Load
    issues = []
    now = datetime.utcnow()
    
    # Payment processing overload (trending)
    for i in range(35):
        issues.append({
            "issue_id": f"PAY_OVERLOAD_{1000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 25))).isoformat(),
            "content": "Payment gateway timeout during checkout. High traffic causing payment processor delays. Customers unable to complete purchases.",
            "category": "payment",
            "priority": 3,  # High
            "status": "open"
        })
    
    # Database performance issues
    for i in range(28):
        issues.append({
            "issue_id": f"DB_SLOW_{2000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(2, 30))).isoformat(),
            "content": "Database queries timing out. Product catalog loading slowly. Inventory checks failing due to DB performance.",
            "category": "database",
            "priority": 3,  # High
            "status": "open"
        })
    
    # API rate limiting
    for i in range(22):
        issues.append({
            "issue_id": f"API_LIMIT_{3000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(5, 35))).isoformat(),
            "content": "API rate limits exceeded. Mobile app requests being throttled. Third-party integrations failing.",
            "category": "api",
            "priority": 2,  # Medium
            "status": "open"
        })
    
    # Notification service overload
    for i in range(15):
        issues.append({
            "issue_id": f"NOTIF_QUEUE_{4000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(3, 40))).isoformat(),
            "content": "Email notification queue backing up. Order confirmations delayed. SMS delivery failing.",
            "category": "notification",
            "priority": 2,  # Medium
            "status": "open"
        })
    
    # Insert BigQuery data
    table_id = f"{bq_client.project}.customer_interactions.issues"
    errors = bq_client.insert_rows_json(table_id, issues)
    if not errors:
        print(f"✅ Inserted {len(issues)} peak traffic issues into BigQuery")
    
    # Datastore Knowledge Base - E-commerce focused
    kb_articles = [
        {
            "title": "Payment Gateway Scaling During Peak Traffic",
            "issue_type": "payment",
            "product_area": "billing",
            "content": "Peak traffic payment issues: 1. Enable backup payment processors 2. Increase gateway timeout limits 3. Scale payment service instances 4. Queue failed payments for retry",
            "status": "active",
            "success_rate": 94,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Database Performance Optimization",
            "issue_type": "database", 
            "product_area": "infrastructure",
            "content": "DB performance during high load: 1. Enable read replicas 2. Implement query caching 3. Scale database instances 4. Optimize slow queries 5. Enable connection pooling",
            "status": "active",
            "success_rate": 91,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "API Rate Limiting and Scaling",
            "issue_type": "api",
            "product_area": "platform",
            "content": "API overload management: 1. Increase rate limits temporarily 2. Scale API gateway instances 3. Implement request queuing 4. Enable API caching",
            "status": "active",
            "success_rate": 87,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Notification Service Load Management",
            "issue_type": "notification",
            "product_area": "communication",
            "content": "Notification overload: 1. Scale email service workers 2. Implement message queuing 3. Prioritize critical notifications 4. Use backup email providers",
            "status": "active",
            "success_rate": 89,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "E-commerce Peak Traffic Playbook",
            "issue_type": "payment",
            "product_area": "billing",
            "content": "Complete peak traffic response: 1. Monitor all payment channels 2. Scale infrastructure proactively 3. Enable all backup systems 4. Communicate with customers",
            "status": "active",
            "success_rate": 96,
            "last_updated": datetime.utcnow().timestamp()
        }
    ]
    
    for article in kb_articles:
        key = ds_client.key("knowledge_base")
        entity = datastore.Entity(key=key)
        entity.update(article)
        ds_client.put(entity)
    
    print(f"✅ Created {len(kb_articles)} knowledge base articles")
    
    # Sample resolution history - Previous peak traffic events
    resolutions = [
        {
            "timestamp": (datetime.utcnow() - timedelta(hours=6)).timestamp(),
            "issue_type": "payment",
            "product_area": "billing",
            "issue_summary": {
                "issue_type": "payment",
                "product_area": "billing",
                "count": 42,
                "description": "Payment gateway overload during flash sale"
            },
            "resolution": {
                "resolution_text": "Scaled payment infrastructure and enabled backup processors",
                "estimated_resolution_time": "20 minutes"
            },
            "channels": ["email", "dashboard", "slack"],
            "metrics": {
                "affected_customers": 42,
                "resolution_time": 18,
                "success_rate": 97
            }
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(hours=12)).timestamp(),
            "issue_type": "database",
            "product_area": "infrastructure",
            "issue_summary": {
                "issue_type": "database",
                "product_area": "infrastructure",
                "count": 31,
                "description": "Database performance degradation during peak hours"
            },
            "resolution": {
                "resolution_text": "Enabled read replicas and optimized query performance",
                "estimated_resolution_time": "35 minutes"
            },
            "channels": ["email", "dashboard"],
            "metrics": {
                "affected_customers": 31,
                "resolution_time": 32,
                "success_rate": 94
            }
        }
    ]
    
    for resolution in resolutions:
        key = ds_client.key("response_history")
        entity = datastore.Entity(key=key)
        entity.update(resolution)
        ds_client.put(entity)
    
    print("✅ Scenario 2 setup complete!")
    print("📊 Data Summary:")
    print(f"   - Payment issues: 35 (HIGH)")
    print(f"   - Database issues: 28 (HIGH)")
    print(f"   - API issues: 22 (MEDIUM)")
    print(f"   - Notification issues: 15 (MEDIUM)")
    print(f"   - Total affected: ~100 users")
    print(f"   - Knowledge base: 5 articles")

if __name__ == "__main__":
    clear_existing_data()
    setup_scenario_2()
    print("\n🚀 Ready for demo! Run: streamlit run trending_issue_resolver/dashboard/dashboard.py")