"""DataFetcher agent for monitoring customer interactions."""

from typing import Any, Dict, Optional

from google.adk.agents import Agent, AgentContext, register_agent
from google.adk.managers import SessionState

from ...tools.bigquery_tool import BigQueryTool


@register_agent
class DataFetcherAgent(Agent):
    """Agent responsible for fetching and analyzing customer interaction data."""

    def __init__(self) -> None:
        super().__init__(
            name="data_fetcher",
            description="Fetches and analyzes customer interaction data to identify trends",
        )

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Process customer interaction data to identify trends.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing trending issues if found
        """
        # Get configuration from session state
        time_window = context.session.state.get("time_window_minutes", 60)
        trend_threshold = context.session.state.get("trend_threshold", 10)
        
        # Get BigQuery tool
        bq_tool = context.get_tool("bigquery_tool")
        if not bq_tool:
            raise RuntimeError("BigQuery tool not found")
        
        # Query for trending issues
        trending_issues = await bq_tool.get_trending_issues(
            time_window_minutes=time_window,
            min_occurrences=trend_threshold,
        )
        
        # Update session state with results
        context.session.state.update({
            "trending_issues": trending_issues,
            "last_check_time": context.current_time,
        })
        
        # If trends found, gather historical context
        if trending_issues:
            primary_issue = trending_issues[0]  # Focus on most significant trend
            historical_context = await bq_tool.get_historical_context(
                issue_type=primary_issue["issue_type"],
                product_area=primary_issue["product_area"],
            )
            context.session.state["historical_context"] = historical_context
        
        return {
            "trending_issues": trending_issues,
            "historical_context": context.session.state.get("historical_context"),
        }