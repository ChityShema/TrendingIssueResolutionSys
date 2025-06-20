"""Script to populate BigQuery with sample customer interaction data."""

from datetime import datetime, timedelta
import random
from google.cloud import bigquery

def create_tables(client, project_id):
    """Create BigQuery tables if they don't exist."""
    
    # Create dataset
    dataset_id = f"{project_id}.customer_interactions"
    try:
        client.create_dataset(dataset_id)
        print(f"Created dataset: {dataset_id}")
    except Exception:
        print(f"Dataset {dataset_id} already exists")
    
    # Issues table schema
    issues_schema = [
        bigquery.SchemaField("issue_type", "STRING"),
        bigquery.SchemaField("product_area", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("severity", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("details", "STRING"),
        bigquery.SchemaField("resolution_time_minutes", "INTEGER"),
        bigquery.SchemaField("resolution_steps", "STRING"),
    ]
    
    # Resolutions table schema
    resolutions_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("issue_type", "STRING"),
        bigquery.SchemaField("product_area", "STRING"),
        bigquery.SchemaField("affected_customers", "INTEGER"),
        bigquery.SchemaField("resolution_steps", "STRING"),
        bigquery.SchemaField("resolution_category", "STRING"),
        bigquery.SchemaField("automated", "BOOLEAN"),
    ]
    
    # Create tables
    issues_table = bigquery.Table(f"{dataset_id}.issues", schema=issues_schema)
    resolutions_table = bigquery.Table(f"{dataset_id}.resolutions", schema=resolutions_schema)
    
    try:
        client.create_table(issues_table)
        print("Created issues table")
    except Exception:
        print("Issues table already exists")
    
    try:
        client.create_table(resolutions_table)
        print("Created resolutions table")
    except Exception:
        print("Resolutions table already exists")

def populate_issues_data(client, project_id):
    """Populate issues table with sample data."""
    
    issue_types = ["authentication", "payment", "database", "api", "notification"]
    product_areas = ["user_management", "billing", "infrastructure", "platform", "communication"]
    severities = ["low", "medium", "high", "critical"]
    
    sample_descriptions = {
        "authentication": ["Login failed", "Token expired", "2FA not working", "Password reset failed"],
        "payment": ["Payment declined", "Transaction timeout", "Billing error", "Refund failed"],
        "database": ["Connection timeout", "Query slow", "Data corruption", "Backup failed"],
        "api": ["Rate limit exceeded", "Invalid response", "Endpoint down", "Timeout error"],
        "notification": ["Email not sent", "SMS failed", "Push notification error", "Template error"]
    }
    
    rows_to_insert = []
    
    # Generate data for last 30 days
    for days_back in range(30):
        date = datetime.utcnow() - timedelta(days=days_back)
        
        # Generate 20-100 issues per day
        daily_issues = random.randint(20, 100)
        
        for _ in range(daily_issues):
            issue_type = random.choice(issue_types)
            product_area = random.choice(product_areas)
            
            # Create trending patterns - more recent issues
            if days_back < 3:
                # Recent spike in authentication and payment issues
                if random.random() < 0.4:
                    issue_type = random.choice(["authentication", "payment"])
            
            timestamp = date + timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            row = {
                "issue_type": issue_type,
                "product_area": product_area,
                "description": random.choice(sample_descriptions[issue_type]),
                "severity": random.choice(severities),
                "customer_id": f"customer_{random.randint(1000, 9999)}",
                "timestamp": timestamp.isoformat(),
                "details": f"Customer reported {issue_type} issue in {product_area}",
                "resolution_time_minutes": random.randint(5, 180),
                "resolution_steps": f"Standard {issue_type} resolution procedure",
            }
            rows_to_insert.append(row)
    
    # Insert data in batches
    table_id = f"{project_id}.customer_interactions.issues"
    errors = client.insert_rows_json(table_id, rows_to_insert)
    
    if errors:
        print(f"Errors inserting issues data: {errors}")
    else:
        print(f"Inserted {len(rows_to_insert)} issue records")

def populate_resolutions_data(client, project_id):
    """Populate resolutions table with sample data."""
    
    resolutions = [
        {
            "issue_type": "authentication",
            "product_area": "user_management",
            "affected_customers": 45,
            "resolution_steps": "Clear cache, reset sessions, update tokens",
            "resolution_category": "system_fix",
        },
        {
            "issue_type": "payment",
            "product_area": "billing",
            "affected_customers": 23,
            "resolution_steps": "Switch payment gateway, retry failed transactions",
            "resolution_category": "service_switch",
        },
        {
            "issue_type": "database",
            "product_area": "infrastructure",
            "affected_customers": 67,
            "resolution_steps": "Restart connection pool, optimize queries",
            "resolution_category": "infrastructure_fix",
        },
    ]
    
    rows_to_insert = []
    
    # Generate resolution history for last 15 days
    for days_back in range(15):
        if random.random() < 0.3:  # 30% chance of resolution per day
            resolution = random.choice(resolutions)
            timestamp = datetime.utcnow() - timedelta(days=days_back)
            
            row = {
                "timestamp": timestamp.isoformat(),
                "issue_type": resolution["issue_type"],
                "product_area": resolution["product_area"],
                "affected_customers": resolution["affected_customers"] + random.randint(-10, 20),
                "resolution_steps": resolution["resolution_steps"],
                "resolution_category": resolution["resolution_category"],
                "automated": True,
            }
            rows_to_insert.append(row)
    
    table_id = f"{project_id}.customer_interactions.resolutions"
    errors = client.insert_rows_json(table_id, rows_to_insert)
    
    if errors:
        print(f"Errors inserting resolutions data: {errors}")
    else:
        print(f"Inserted {len(rows_to_insert)} resolution records")

def main():
    """Main function to populate BigQuery."""
    try:
        client = bigquery.Client()
        project_id = client.project
        print(f"Connected to BigQuery project: {project_id}")
        
        print("\nCreating tables...")
        create_tables(client, project_id)
        
        print("\nPopulating issues data...")
        populate_issues_data(client, project_id)
        
        print("\nPopulating resolutions data...")
        populate_resolutions_data(client, project_id)
        
        print("\nBigQuery populated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()