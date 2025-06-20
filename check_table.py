"""Check BigQuery table structure."""

import os
from google.cloud import bigquery

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

def check_table():
    """Check what tables and columns exist."""
    client = bigquery.Client()
    
    # List datasets
    datasets = list(client.list_datasets())
    print("Available datasets:")
    for dataset in datasets:
        print(f"  - {dataset.dataset_id}")
    
    # Check customer_interactions dataset
    try:
        dataset_id = f"{client.project}.customer_interactions"
        tables = list(client.list_tables(dataset_id))
        print(f"\nTables in {dataset_id}:")
        for table in tables:
            print(f"  - {table.table_id}")
            
            # Get table schema
            table_ref = client.get_table(f"{dataset_id}.{table.table_id}")
            print(f"    Columns:")
            for field in table_ref.schema:
                print(f"      - {field.name} ({field.field_type})")
            
            # Sample data
            query = f"SELECT * FROM `{dataset_id}.{table.table_id}` LIMIT 3"
            results = list(client.query(query).result())
            print(f"    Sample rows: {len(results)}")
            for row in results:
                print(f"      {dict(row)}")
            print()
            
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    check_table()