"""Datastore tool for knowledge base and response management."""

from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from google.adk import Tool
except ImportError:
    # Fallback if ADK not available
    class Tool:
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
from google.cloud import datastore


class DatastoreTool(Tool):
    """Tool for managing knowledge base and response data in Datastore."""

    def __init__(self, client: datastore.Client):
        """Initialize the Datastore tool.
        
        Args:
            client: Initialized Datastore client
        """
        super().__init__(
            name="datastore_tool",
            description="Manages knowledge base articles and response history",
        )
        self.client = client

    async def search_knowledge_base(
        self,
        issue_type: str,
        product_area: str,
        keywords: List[str],
    ) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant articles.
        
        Args:
            issue_type: Type of issue to search for
            product_area: Affected product area
            keywords: List of relevant keywords
            
        Returns:
            List of matching knowledge base articles
        """
        # Query entities matching issue type and product area
        query = self.client.query(kind="knowledge_base")
        query.add_filter("issue_type", "=", issue_type)
        query.add_filter("product_area", "=", product_area)
        query.add_filter("status", "=", "active")
        query.order = ["-last_updated"]
        
        entities = list(query.fetch())
        matches = []
        
        # Filter and score results based on keywords
        for entity in entities:
            content = entity.get("content", "").lower()
            score = sum(1 for kw in keywords if kw in content)
            if score > 0:
                article = dict(entity)
                article["id"] = entity.key.id or entity.key.name
                article["relevance_score"] = score
                matches.append(article)
        
        # Sort by relevance score and return top matches
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matches[:5]

    async def get_similar_responses(
        self,
        issue_type: str,
        product_area: str,
        last_n_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Retrieve similar recent responses for consistency.
        
        Args:
            issue_type: Type of issue to match
            product_area: Affected product area
            last_n_days: Number of days to look back
            
        Returns:
            List of recent similar responses
        """
        cutoff = datetime.utcnow().timestamp() - (last_n_days * 86400)
        
        query = self.client.query(kind="response_history")
        query.add_filter("issue_type", "=", issue_type)
        query.add_filter("product_area", "=", product_area)
        query.add_filter("timestamp", ">=", cutoff)
        query.order = ["-timestamp"]
        
        entities = list(query.fetch())
        responses = []
        
        for entity in entities:
            response = dict(entity)
            response["id"] = entity.key.id or entity.key.name
            responses.append(response)
        
        return responses

    async def save_response(
        self,
        issue_summary: Dict[str, Any],
        resolution: Dict[str, Any],
        channels: List[str],
    ) -> str:
        """Save a response for future reference.
        
        Args:
            issue_summary: Summary of the trending issue
            resolution: Resolution details and steps
            channels: List of notification channels used
            
        Returns:
            ID of the saved response entity
        """
        key = self.client.key("response_history")
        entity = datastore.Entity(key=key)
        
        entity.update({
            "timestamp": datetime.utcnow().timestamp(),
            "issue_type": issue_summary["issue_type"],
            "product_area": issue_summary["product_area"],
            "issue_summary": issue_summary,
            "resolution": resolution,
            "channels": channels,
            "metrics": {
                "affected_customers": issue_summary["count"],
                "resolution_time": None,
                "success_rate": None,
            }
        })
        
        self.client.put(entity)
        return str(entity.key.id)

    async def update_response_metrics(
        self,
        response_id: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Update metrics for a saved response.
        
        Args:
            response_id: ID of the response entity
            metrics: Updated metric values
        """
        key = self.client.key("response_history", int(response_id))
        entity = self.client.get(key)
        
        if entity:
            entity["metrics"] = metrics
            entity["last_updated"] = datetime.utcnow().timestamp()
            self.client.put(entity)