"""Setup BigQuery and Datastore data quickly."""

import os
from datetime import datetime, timedelta
import random
from google.cloud import bigquery, datastore

# Set project
os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

def setup_bigquery():
    """Create BigQuery dataset and table with sample data."""
    print("Setting up BigQuery...")
    
    client = bigquery.Client()
    dataset_id = f"{client.project}.customer_interactions"
    
    # Create dataset
    try:
        dataset = bigquery.Dataset(dataset_id)
        client.create_dataset(dataset)
        print(f"✓ Created dataset: {dataset_id}")
    except Exception:
        print(f"✓ Dataset exists: {dataset_id}")
    
    # Create issues table
    table_id = f"{dataset_id}.issues"
    schema = [
        bigquery.SchemaField("issue_type", "STRING"),
        bigquery.SchemaField("product_area", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("severity", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("details", "STRING"),
    ]
    
    try:
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)
        print(f"✓ Created table: {table_id}")
    except Exception:
        print(f"✓ Table exists: {table_id}")
    
    # Insert sample data
    rows = []
    now = datetime.utcnow()
    
    # Create recent trending issues
    for i in range(20):
        rows.append({
            "issue_type": "authentication",
            "product_area": "user_management", 
            "description": "Login failed",
            "severity": "high",
            "customer_id": f"customer_{1000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 30))).isoformat(),
            "details": "User unable to login with valid credentials"
        })
    
    for i in range(15):
        rows.append({
            "issue_type": "payment",
            "product_area": "billing",
            "description": "Payment declined", 
            "severity": "medium",
            "customer_id": f"customer_{2000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 45))).isoformat(),
            "details": "Payment processing failed at checkout"
        })
    
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        print(f"❌ Errors inserting data: {errors}")
    else:
        print(f"✓ Inserted {len(rows)} sample issues")

def setup_datastore():
    """Create Datastore entities with sample data."""
    print("Setting up Datastore...")
    
    client = datastore.Client()
    
    # Knowledge base articles
    articles = [
        {
            "title": "Authentication Troubleshooting",
            "issue_type": "authentication",
            "product_area": "user_management",
            "content": "Common login issues: clear cache, reset password, check 2FA settings",
            "status": "active",
            "success_rate": 85,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Payment Processing Guide", 
            "issue_type": "payment",
            "product_area": "billing",
            "content": "Payment failures: verify card details, check account balance, retry transaction",
            "status": "active", 
            "success_rate": 92,
            "last_updated": datetime.utcnow().timestamp()
        }
    ]
    
    for article in articles:
        key = client.key("knowledge_base")
        entity = datastore.Entity(key=key)
        entity.update(article)
        client.put(entity)
    
    print(f"✓ Created {len(articles)} knowledge base articles")

def main():
    """Setup all data."""
    print("🚀 Setting up sample data...")
    print("=" * 30)
    
    try:
        setup_bigquery()
        setup_datastore()
        print("\n✅ Data setup completed!")
        print("\nNow run: python run_simple.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()