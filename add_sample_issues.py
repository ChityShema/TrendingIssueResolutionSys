"""Add sample issues to the existing BigQuery table."""

import os
from datetime import datetime, timedelta
import random
from google.cloud import bigquery

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

def add_sample_issues():
    """Add sample issues to match the existing table structure."""
    client = bigquery.Client()
    table_id = f"{client.project}.customer_interactions.issues"
    
    # Create sample issues matching the actual schema
    rows = []
    now = datetime.utcnow()
    
    # Authentication issues (trending)
    for i in range(15):
        rows.append({
            "issue_id": f"AUTH_{1000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 30))).isoformat(),
            "content": "User unable to login with valid credentials. Authentication service returning errors.",
            "category": "authentication",
            "priority": 3,  # High priority
            "status": "open"
        })
    
    # Payment issues (trending)
    for i in range(12):
        rows.append({
            "issue_id": f"PAY_{2000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 45))).isoformat(),
            "content": "Payment processing failed at checkout. Transaction declined by payment gateway.",
            "category": "payment",
            "priority": 2,  # Medium priority
            "status": "open"
        })
    
    # Database issues
    for i in range(8):
        rows.append({
            "issue_id": f"DB_{3000+i}",
            "timestamp": (now - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "content": "Database connection timeout. Queries taking longer than expected.",
            "category": "database",
            "priority": 3,  # High priority
            "status": "open"
        })
    
    # Insert the data
    errors = client.insert_rows_json(table_id, rows)
    
    if errors:
        print(f"❌ Errors inserting data: {errors}")
    else:
        print(f"✅ Successfully inserted {len(rows)} sample issues")
        
        # Verify the data
        query = f"SELECT category, COUNT(*) as count FROM `{table_id}` GROUP BY category ORDER BY count DESC"
        results = list(client.query(query).result())
        
        print("\nIssue counts by category:")
        for row in results:
            print(f"  {row.category}: {row.count}")

if __name__ == "__main__":
    add_sample_issues()