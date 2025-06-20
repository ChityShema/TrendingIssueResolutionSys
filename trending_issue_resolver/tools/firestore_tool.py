"""Firestore tool for knowledge base and response management."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from adk import Tool
from google.cloud import firestore


class FirestoreTool(Tool):
    """Tool for managing knowledge base and response data in Firestore."""

    def __init__(self, client: firestore.Client):
        """Initialize the Firestore tool.
        
        Args:
            client: Initialized Firestore client
        """
        super().__init__(
            name="firestore_tool",
            description="Manages knowledge base articles and response history",
        )
        self.client = client
        self.kb_collection = self.client.collection("knowledge_base")
        self.responses_collection = self.client.collection("response_history")

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
        # Query articles matching issue type and product area
        query = (
            self.kb_collection
            .where("issue_type", "==", issue_type)
            .where("product_area", "==", product_area)
            .where("status", "==", "active")
            .order_by("last_updated", direction=firestore.Query.DESCENDING)
        )
        
        docs = query.stream()
        matches = []
        
        # Filter and score results based on keywords
        for doc in docs:
            article = doc.to_dict()
            score = sum(1 for kw in keywords if kw.lower() in article["content"].lower())
            if score > 0:
                article["id"] = doc.id
                article["relevance_score"] = score
                matches.append(article)
        
        # Sort by relevance score and return top matches
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matches[:5]  # Return top 5 matches

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
        
        query = (
            self.responses_collection
            .where("issue_type", "==", issue_type)
            .where("product_area", "==", product_area)
            .where("timestamp", ">=", cutoff)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        
        docs = query.stream()
        responses = []
        
        for doc in docs:
            response = doc.to_dict()
            response["id"] = doc.id
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
            ID of the saved response document
        """
        response_data = {
            "timestamp": datetime.utcnow().timestamp(),
            "issue_type": issue_summary["issue_type"],
            "product_area": issue_summary["product_area"],
            "issue_summary": issue_summary,
            "resolution": resolution,
            "channels": channels,
            "metrics": {
                "affected_customers": issue_summary["count"],
                "resolution_time": None,  # To be updated later
                "success_rate": None,  # To be updated later
            }
        }
        
        doc_ref = self.responses_collection.document()
        doc_ref.set(response_data)
        return doc_ref.id

    async def update_response_metrics(
        self,
        response_id: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Update metrics for a saved response.
        
        Args:
            response_id: ID of the response document
            metrics: Updated metric values
        """
        doc_ref = self.responses_collection.document(response_id)
        doc_ref.update({
            "metrics": metrics,
            "last_updated": datetime.utcnow().timestamp(),
        })