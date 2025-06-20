"""ResolutionGenerator agent for creating comprehensive solutions."""

from typing import Any, Dict, Optional

from google.adk.agents import Agent, AgentContext, register_agent
from google.adk.managers import SessionState
from google.cloud import aiplatform

from ...prompt import RESOLUTION_GENERATOR_PROMPT


@register_agent
class ResolutionGeneratorAgent(Agent):
    """Agent that generates comprehensive issue resolutions."""

    def __init__(self) -> None:
        super().__init__(
            name="resolution_generator",
            description="Generates detailed solutions for trending issues",
            prompt=RESOLUTION_GENERATOR_PROMPT,
        )

    def _format_context(
        self,
        summary: Dict[str, Any],
        kb_hits: Dict[str, Any],
    ) -> str:
        """Format context information for the LLM prompt.
        
        Args:
            summary: Issue summary
            kb_hits: Knowledge base findings
            
        Returns:
            Formatted context string
        """
        context = [
            "Issue Context:",
            f"Type: {summary['primary_issue']['type']}",
            f"Product Area: {summary['primary_issue']['product_area']}",
            f"Severity: {summary['primary_issue']['severity']}",
            f"Affected Users: {summary['primary_issue']['count']}",
            "",
            "Issue Summary:",
            summary['text'],
            "",
            "Knowledge Base Analysis:",
            kb_hits['analysis'],
        ]
        
        return "\n".join(context)

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Generate comprehensive issue resolution.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing the final resolution
        """
        summary = context.session.state.get("summary")
        kb_hits = context.session.state.get("kb_hits")
        
        if not summary or not kb_hits:
            return {"final_resolution": None}
        
        # Format context for LLM
        context_text = self._format_context(summary, kb_hits)
        
        # Prepare LLM prompt
        prompt = f"""{self.prompt}

{context_text}

Please generate a comprehensive resolution that includes:
1. Root cause analysis
2. Step-by-step resolution steps
3. Verification steps
4. Prevention measures
5. Customer communication template
"""
        
        # Get Vertex AI client
        vertex_ai = aiplatform.gapic.VertexAIClient()
        
        # Generate resolution using Gemini Pro
        response = await vertex_ai.predict_text(
            model_name="gemini-pro",
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=2048,
        )
        
        # Parse response sections
        sections = response.text.split("\n\n")
        
        resolution = {
            "issue_type": summary["primary_issue"]["type"],
            "product_area": summary["primary_issue"]["product_area"],
            "root_cause": sections[0] if len(sections) > 0 else "",
            "steps": sections[1] if len(sections) > 1 else "",
            "verification": sections[2] if len(sections) > 2 else "",
            "prevention": sections[3] if len(sections) > 3 else "",
            "communication_template": sections[4] if len(sections) > 4 else "",
            "kb_articles_used": [a["id"] for a in kb_hits["articles"]],
            "generated_at": context.current_time.isoformat(),
        }
        
        # Update session state
        context.session.state["final_resolution"] = resolution
        
        # Save resolution to Datastore
        datastore_tool = context.get_tool("datastore_tool")
        if datastore_tool:
            resolution_id = await datastore_tool.save_response(
                issue_summary=summary,
                resolution=resolution,
                channels=["ui", "email", "crm"],
            )
            resolution["id"] = resolution_id
        
        return {"final_resolution": resolution}