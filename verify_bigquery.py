"""Script to verify BigQuery data population."""

from google.cloud import bigquery

def verify_tables(client, project_id):
    """Verify that tables exist and have data."""
    
    dataset_id = f"{project_id}.customer_interactions"
    
    # Check issues table
    issues_query = f"SELECT COUNT(*) as count FROM `{dataset_id}.issues`"
    result = client.query(issues_query).result()
    issues_count = next(iter(result)).count
    print(f"Issues table: {issues_count} records")
    
    # Check resolutions table
    resolutions_query = f"SELECT COUNT(*) as count FROM `{dataset_id}.resolutions`"
    result = client.query(resolutions_query).result()
    resolutions_count = next(iter(result)).count
    print(f"Resolutions table: {resolutions_count} records")

def test_trending_query(client, project_id):
    """Test the trending issues query."""
    
    query = f"""
    SELECT 
        issue_type,
        product_area,
        COUNT(*) as occurrence_count
    FROM `{project_id}.customer_interactions.issues`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 MINUTE)
    GROUP BY issue_type, product_area
    HAVING COUNT(*) >= 5
    ORDER BY occurrence_count DESC
    LIMIT 5
    """
    
    result = client.query(query).result()
    
    print("\nRecent trending issues (last 60 minutes):")
    for row in result:
        print(f"  - {row.issue_type}/{row.product_area}: {row.occurrence_count} occurrences")

def test_historical_query(client, project_id):
    """Test historical context query."""
    
    query = f"""
    SELECT
        issue_type,
        product_area,
        COUNT(*) as total_count,
        AVG(resolution_time_minutes) as avg_resolution_time
    FROM `{project_id}.customer_interactions.issues`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    GROUP BY issue_type, product_area
    ORDER BY total_count DESC
    LIMIT 5
    """
    
    result = client.query(query).result()
    
    print("\nHistorical data (last 7 days):")
    for row in result:
        print(f"  - {row.issue_type}/{row.product_area}: {row.total_count} issues, avg {row.avg_resolution_time:.1f}min resolution")

def main():
    """Main verification function."""
    try:
        client = bigquery.Client()
        project_id = client.project
        print(f"Connected to BigQuery project: {project_id}\n")
        
        verify_tables(client, project_id)
        test_trending_query(client, project_id)
        test_historical_query(client, project_id)
        
        print("\nBigQuery verification completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()