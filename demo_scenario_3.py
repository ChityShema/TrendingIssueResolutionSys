"""Demo Scenario 3: Multi-Service Cascade Failure - Complex System Issues"""

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

def setup_scenario_3():
    """Scenario 3: Multi-Service Cascade Failure - Complex interconnected system issues"""
    print("⚡ Setting up Scenario 3: Multi-Service Cascade Failure")
    
    bq_client = bigquery.Client()
    ds_client = datastore.Client()
    
    # BigQuery Issues - Cascade failure across multiple services
    issues = []
    now = datetime.utcnow()
    
    # Database cluster failure (root cause)
    for i in range(32):
        issues.append({
            "issue_id": f"DB_CLUSTER_{1000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 20))).isoformat(),
            "content": "Primary database cluster unreachable. Connection pool exhausted. All dependent services affected.",
            "category": "database",
            "priority": 4,  # Critical
            "status": "open"
        })
    
    # Authentication service dependent on DB
    for i in range(28):
        issues.append({
            "issue_id": f"AUTH_CASCADE_{2000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(2, 25))).isoformat(),
            "content": "Authentication service failing due to database unavailability. User sessions cannot be validated.",
            "category": "authentication",
            "priority": 4,  # Critical
            "status": "open"
        })
    
    # Payment service cascade failure
    for i in range(24):
        issues.append({
            "issue_id": f"PAY_CASCADE_{3000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(3, 30))).isoformat(),
            "content": "Payment processing halted. Cannot verify user accounts or process transactions due to auth/DB failures.",
            "category": "payment",
            "priority": 4,  # Critical
            "status": "open"
        })
    
    # API gateway failures
    for i in range(19):
        issues.append({
            "issue_id": f"API_CASCADE_{4000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(4, 35))).isoformat(),
            "content": "API gateway returning 503 errors. All endpoints affected due to backend service failures.",
            "category": "api",
            "priority": 3,  # High
            "status": "open"
        })
    
    # Notification service failures
    for i in range(16):
        issues.append({
            "issue_id": f"NOTIF_CASCADE_{5000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(5, 40))).isoformat(),
            "content": "Notification service cannot send alerts. Database dependency causing complete service failure.",
            "category": "notification",
            "priority": 3,  # High
            "status": "open"
        })
    
    # Monitoring and logging issues
    for i in range(12):
        issues.append({
            "issue_id": f"MONITOR_CASCADE_{6000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(6, 45))).isoformat(),
            "content": "Monitoring system degraded. Cannot track system health due to database connectivity issues.",
            "category": "monitoring",
            "priority": 2,  # Medium
            "status": "open"
        })
    
    # Insert BigQuery data
    table_id = f"{bq_client.project}.customer_interactions.issues"
    errors = bq_client.insert_rows_json(table_id, issues)
    if not errors:
        print(f"✅ Inserted {len(issues)} cascade failure issues into BigQuery")
    
    # Datastore Knowledge Base - Disaster recovery focused
    kb_articles = [
        {
            "title": "Database Cluster Failure Recovery",
            "issue_type": "database",
            "product_area": "infrastructure",
            "content": "CRITICAL DB Recovery: 1. Activate standby cluster 2. Update connection strings 3. Verify data consistency 4. Restart dependent services 5. Monitor replication lag",
            "status": "active",
            "success_rate": 92,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Cascade Failure Response Protocol",
            "issue_type": "database", 
            "product_area": "infrastructure",
            "content": "Multi-service failure response: 1. Identify root cause service 2. Activate disaster recovery 3. Communicate with all teams 4. Implement service isolation 5. Gradual service restoration",
            "status": "active",
            "success_rate": 89,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Authentication Service Emergency Mode",
            "issue_type": "authentication",
            "product_area": "user_management",
            "content": "Auth service failover: 1. Enable cached authentication 2. Activate backup auth service 3. Use emergency credentials 4. Implement graceful degradation",
            "status": "active",
            "success_rate": 85,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Payment Service Circuit Breaker",
            "issue_type": "payment",
            "product_area": "billing",
            "content": "Payment failure isolation: 1. Enable circuit breaker 2. Queue payment requests 3. Use backup payment processor 4. Implement retry logic with backoff",
            "status": "active",
            "success_rate": 88,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "API Gateway Failover Procedures",
            "issue_type": "api",
            "product_area": "platform",
            "content": "API gateway recovery: 1. Route traffic to healthy instances 2. Enable API caching 3. Implement rate limiting 4. Return cached responses for non-critical endpoints",
            "status": "active",
            "success_rate": 91,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "System-Wide Incident Response",
            "issue_type": "monitoring",
            "product_area": "infrastructure",
            "content": "Major incident protocol: 1. Activate incident commander 2. Set up war room 3. Coordinate cross-team response 4. Implement communication plan 5. Document timeline",
            "status": "active",
            "success_rate": 94,
            "last_updated": datetime.utcnow().timestamp()
        }
    ]
    
    for article in kb_articles:
        key = ds_client.key("knowledge_base")
        entity = datastore.Entity(key=key)
        entity.update(article)
        ds_client.put(entity)
    
    print(f"✅ Created {len(kb_articles)} knowledge base articles")
    
    # Sample resolution history - Previous major incidents
    resolutions = [
        {
            "timestamp": (datetime.utcnow() - timedelta(days=1)).timestamp(),
            "issue_type": "database",
            "product_area": "infrastructure",
            "issue_summary": {
                "issue_type": "database",
                "product_area": "infrastructure",
                "count": 89,
                "description": "Previous database cluster failure resolved"
            },
            "resolution": {
                "resolution_text": "Successfully failed over to standby cluster and restored all services",
                "estimated_resolution_time": "2 hours 15 minutes"
            },
            "channels": ["email", "slack", "dashboard", "pager"],
            "metrics": {
                "affected_customers": 89,
                "resolution_time": 135,
                "success_rate": 96
            }
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(days=3)).timestamp(),
            "issue_type": "authentication",
            "product_area": "user_management",
            "issue_summary": {
                "issue_type": "authentication",
                "product_area": "user_management",
                "count": 156,
                "description": "Major authentication service outage"
            },
            "resolution": {
                "resolution_text": "Implemented emergency authentication mode and restored primary service",
                "estimated_resolution_time": "1 hour 45 minutes"
            },
            "channels": ["email", "slack", "dashboard"],
            "metrics": {
                "affected_customers": 156,
                "resolution_time": 105,
                "success_rate": 93
            }
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(days=7)).timestamp(),
            "issue_type": "payment",
            "product_area": "billing",
            "issue_summary": {
                "issue_type": "payment",
                "product_area": "billing",
                "count": 73,
                "description": "Payment processor cascade failure"
            },
            "resolution": {
                "resolution_text": "Activated backup payment systems and processed queued transactions",
                "estimated_resolution_time": "3 hours 20 minutes"
            },
            "channels": ["email", "dashboard"],
            "metrics": {
                "affected_customers": 73,
                "resolution_time": 200,
                "success_rate": 91
            }
        }
    ]
    
    for resolution in resolutions:
        key = ds_client.key("response_history")
        entity = datastore.Entity(key=key)
        entity.update(resolution)
        ds_client.put(entity)
    
    print("✅ Scenario 3 setup complete!")
    print("📊 Data Summary:")
    print(f"   - Database issues: 32 (CRITICAL)")
    print(f"   - Authentication issues: 28 (CRITICAL)")
    print(f"   - Payment issues: 24 (CRITICAL)")
    print(f"   - API issues: 19 (HIGH)")
    print(f"   - Notification issues: 16 (HIGH)")
    print(f"   - Monitoring issues: 12 (MEDIUM)")
    print(f"   - Total affected: ~131 users")
    print(f"   - Knowledge base: 6 articles")

if __name__ == "__main__":
    clear_existing_data()
    setup_scenario_3()
    print("\n🚀 Ready for demo! Run: streamlit run trending_issue_resolver/dashboard/dashboard.py")