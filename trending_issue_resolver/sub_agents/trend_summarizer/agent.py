"""TrendSummarizer agent for analyzing and summarizing trending issues."""

from typing import Any, Dict, List, Optional

from google.adk import Agent, AgentContext, register_agent
from google.adk.managers import SessionState
from google.cloud import aiplatform

from ...prompt import TREND_SUMMARIZER_PROMPT


@register_agent
class TrendSummarizerAgent(Agent):
    """Agent that generates concise summaries of trending issues."""

    def __init__(self) -> None:
        super().__init__(
            name="trend_summarizer",
            description="Analyzes and summarizes trending customer issues",
            prompt=TREND_SUMMARIZER_PROMPT,
        )

    def _format_issue_data(
        self,
        trending_issues: List[Dict[str, Any]],
        historical_context: Dict[str, Any],
    ) -> str:
        """Format issue data for the LLM prompt.
        
        Args:
            trending_issues: List of trending issues
            historical_context: Historical data for context
            
        Returns:
            Formatted string for LLM consumption
        """
        if not trending_issues:
            return "No trending issues detected."
        
        primary_issue = trending_issues[0]
        
        # Format primary issue details
        summary = [
            f"Primary Trending Issue:",
            f"- Type: {primary_issue['issue_type']}",
            f"- Product Area: {primary_issue['product_area']}",
            f"- Description: {primary_issue['description']}",
            f"- Severity: {primary_issue['severity']}",
            f"- Current Incident Count: {primary_issue['count']}",
            "",
            "Recent Incidents:",
        ]
        
        # Add recent incident details
        for incident in primary_issue["incidents"][:5]:  # Show last 5 incidents
            summary.append(
                f"- Customer {incident['customer_id']}: {incident['details']}"
            )
        
        # Add historical context if available
        if historical_context:
            summary.extend([
                "",
                "Historical Context:",
                f"- Average Daily Incidents: {historical_context['avg_daily_incidents']:.1f}",
                f"- Typical Resolution Time: {historical_context['typical_resolution_time']:.1f} minutes",
            ])
        
        # Add other trending issues if present
        if len(trending_issues) > 1:
            summary.extend([
                "",
                "Other Trending Issues:",
            ])
            for issue in trending_issues[1:]:
                summary.append(
                    f"- {issue['issue_type']} ({issue['count']} incidents): {issue['description']}"
                )
        
        return "\n".join(summary)

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Generate a summary of trending issues.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing the issue summary
        """
        trending_issues = context.session.state.get("trending_issues", [])
        historical_context = context.session.state.get("historical_context", {})
        
        if not trending_issues:
            return {"summary": None}
        
        # Format data for the LLM
        issue_data = self._format_issue_data(trending_issues, historical_context)
        
        # Prepare LLM prompt
        prompt = f"{self.prompt}\n\nCurrent Issue Data:\n{issue_data}\n\nPlease provide a comprehensive summary."
        
        # Get Vertex AI client
        vertex_ai = aiplatform.gapic.VertexAIClient()
        
        # Generate summary using Gemini Pro
        response = await vertex_ai.predict_text(
            model_name="gemini-pro",
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=1024,
        )
        
        summary = {
            "text": response.text,
            "primary_issue": {
                "type": trending_issues[0]["issue_type"],
                "product_area": trending_issues[0]["product_area"],
                "severity": trending_issues[0]["severity"],
                "count": trending_issues[0]["count"],
            },
            "total_issues": len(trending_issues),
            "timestamp": context.current_time.isoformat(),
        }
        
        # Update session state
        context.session.state["summary"] = summary
        
        return {"summary": summary}