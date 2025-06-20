"""BigQuery tool for analyzing customer interaction data."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from adk import Tool
from google.cloud import bigquery


class BigQueryTool(Tool):
    """Tool for querying and analyzing customer interaction data in BigQuery."""

    def __init__(self, client: bigquery.Client):
        """Initialize the BigQuery tool.
        
        Args:
            client: Initialized BigQuery client
        """
        super().__init__(
            name="bigquery_tool",
            description="Analyzes customer interaction data to identify trends",
        )
        self.client = client

    async def get_trending_issues(
        self,
        time_window_minutes: int = 60,
        min_occurrences: int = 10,
    ) -> List[Dict[str, Any]]:
        """Query recent customer interactions to identify trending issues.
        
        Args:
            time_window_minutes: Time window to analyze in minutes
            min_occurrences: Minimum number of occurrences to consider a trend
            
        Returns:
            List of trending issues with counts and details
        """
        query = f"""
        WITH recent_issues AS (
            SELECT 
                issue_type,
                product_area,
                description,
                severity,
                COUNT(*) as occurrence_count,
                ARRAY_AGG(STRUCT(customer_id, timestamp, details)) as incidents
            FROM `{self.client.project}.customer_interactions.issues`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {time_window_minutes} MINUTE)
            GROUP BY issue_type, product_area, description, severity
            HAVING COUNT(*) >= {min_occurrences}
        )
        SELECT *
        FROM recent_issues
        ORDER BY occurrence_count DESC
        """
        
        query_job = self.client.query(query)
        results = query_job.result()
        
        trending_issues = []
        for row in results:
            trending_issues.append({
                "issue_type": row.issue_type,
                "product_area": row.product_area,
                "description": row.description,
                "severity": row.severity,
                "count": row.occurrence_count,
                "incidents": [dict(i) for i in row.incidents],
            })
        
        return trending_issues

    async def get_historical_context(
        self,
        issue_type: str,
        product_area: str,
        lookback_days: int = 30,
    ) -> Dict[str, Any]:
        """Retrieve historical context for similar issues.
        
        Args:
            issue_type: Type of issue to analyze
            product_area: Affected product area
            lookback_days: Number of days to look back
            
        Returns:
            Historical statistics and patterns
        """
        query = f"""
        WITH historical_data AS (
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as daily_count,
                AVG(resolution_time_minutes) as avg_resolution_time,
                ARRAY_AGG(resolution_steps) as resolutions
            FROM `{self.client.project}.customer_interactions.issues`
            WHERE 
                timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {lookback_days} DAY)
                AND issue_type = @issue_type
                AND product_area = @product_area
            GROUP BY DATE(timestamp)
        )
        SELECT
            AVG(daily_count) as avg_daily_incidents,
            MAX(daily_count) as max_daily_incidents,
            AVG(avg_resolution_time) as typical_resolution_time,
            ARRAY_AGG(DISTINCT resolutions) as historical_resolutions
        FROM historical_data
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("issue_type", "STRING", issue_type),
                bigquery.ScalarQueryParameter("product_area", "STRING", product_area),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        result = next(iter(query_job.result()))
        
        return {
            "avg_daily_incidents": result.avg_daily_incidents,
            "max_daily_incidents": result.max_daily_incidents,
            "typical_resolution_time": result.typical_resolution_time,
            "historical_resolutions": [r for r in result.historical_resolutions if r],
        }

    async def log_resolution(
        self,
        issue_summary: Dict[str, Any],
        resolution: Dict[str, Any],
    ) -> None:
        """Log a resolution for future reference.
        
        Args:
            issue_summary: Summary of the trending issue
            resolution: Details of the resolution provided
        """
        table_id = f"{self.client.project}.customer_interactions.resolutions"
        
        rows_to_insert = [{
            "timestamp": datetime.utcnow().isoformat(),
            "issue_type": issue_summary["issue_type"],
            "product_area": issue_summary["product_area"],
            "affected_customers": issue_summary["count"],
            "resolution_steps": resolution["steps"],
            "resolution_category": resolution["category"],
            "automated": True,
        }]
        
        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            raise RuntimeError(f"Failed to log resolution: {errors}")