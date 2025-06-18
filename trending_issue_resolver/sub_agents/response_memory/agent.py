"""ResponseMemory agent for maintaining consistent responses."""

from typing import Any, Dict, Optional

from google.adk import Agent, AgentContext, register_agent
from google.adk.managers import SessionState
from google.cloud import aiplatform


@register_agent
class ResponseMemoryAgent(Agent):
    """Agent that ensures response consistency across similar issues."""

    def __init__(self) -> None:
        super().__init__(
            name="response_memory",
            description="Maintains consistency in issue resolutions",
        )

    async def _check_consistency(
        self,
        current_resolution: Dict[str, Any],
        past_responses: List[Dict[str, Any]],
        vertex_ai: Any,
    ) -> Dict[str, Any]:
        """Check and ensure consistency with past responses.
        
        Args:
            current_resolution: Current resolution
            past_responses: Previous similar responses
            vertex_ai: Vertex AI client
            
        Returns:
            Potentially modified resolution
        """
        if not past_responses:
            return current_resolution
        
        # Prepare comparison prompt
        responses_text = []
        for idx, resp in enumerate(past_responses[:3], 1):  # Compare with last 3
            responses_text.extend([
                f"\nPast Response {idx}:",
                f"Root Cause: {resp['resolution']['root_cause']}",
                f"Steps: {resp['resolution']['steps']}",
                f"Communication: {resp['resolution']['communication_template']}",
            ])
        
        prompt = f"""Compare the current resolution with past responses and ensure consistency.
        Identify any contradictions or improvements needed.

        Current Resolution:
        Root Cause: {current_resolution['root_cause']}
        Steps: {current_resolution['steps']}
        Communication: {current_resolution['communication_template']}

        Past Responses:
        {'\n'.join(responses_text)}

        Please analyze and suggest any needed adjustments to maintain consistency while preserving accuracy.
        """
        
        # Get consistency analysis
        response = await vertex_ai.predict_text(
            model_name="gemini-pro",
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=1024,
        )
        
        # If significant changes suggested, generate updated resolution
        if "suggested changes" in response.text.lower():
            update_prompt = f"""Based on the consistency analysis, please provide an updated resolution that maintains consistency with past responses while addressing the current issue effectively.

            Analysis: {response.text}

            Please provide the updated resolution in the same format as the original.
            """
            
            update_response = await vertex_ai.predict_text(
                model_name="gemini-pro",
                prompt=update_prompt,
                temperature=0.2,
                max_output_tokens=1024,
            )
            
            # Parse updated sections
            sections = update_response.text.split("\n\n")
            if len(sections) >= 5:
                current_resolution.update({
                    "root_cause": sections[0],
                    "steps": sections[1],
                    "verification": sections[2],
                    "prevention": sections[3],
                    "communication_template": sections[4],
                    "consistency_changes": response.text,
                })
        
        return current_resolution

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Process and ensure consistency of resolutions.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing the consistent resolution
        """
        resolution = context.session.state.get("final_resolution")
        if not resolution:
            return {"consistent_resolution": None}
        
        # Get Firestore tool
        firestore_tool = context.get_tool("firestore_tool")
        if not firestore_tool:
            raise RuntimeError("Firestore tool not found")
        
        # Get similar past responses
        past_responses = await firestore_tool.get_similar_responses(
            issue_type=resolution["issue_type"],
            product_area=resolution["product_area"],
        )
        
        if not past_responses:
            return {"consistent_resolution": resolution}
        
        # Get Vertex AI client
        vertex_ai = aiplatform.gapic.VertexAIClient()
        
        # Check and ensure consistency
        consistent_resolution = await self._check_consistency(
            current_resolution=resolution,
            past_responses=past_responses,
            vertex_ai=vertex_ai,
        )
        
        # Update session state
        context.session.state["final_resolution"] = consistent_resolution
        
        # If resolution was modified, update in Firestore
        if consistent_resolution.get("consistency_changes"):
            await firestore_tool.update_response_metrics(
                response_id=resolution["id"],
                metrics={
                    "consistency_adjusted": True,
                    "adjustment_reason": consistent_resolution["consistency_changes"],
                },
            )
        
        return {"consistent_resolution": consistent_resolution}