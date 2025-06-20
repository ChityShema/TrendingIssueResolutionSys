"""Notifier agent for managing communications across channels."""

from typing import Any, Dict, List, Optional
import json

from google.adk.agents import Agent, AgentContext, SequentialAgent, register_agent
from google.adk.managers import SessionState
from google.cloud import aiplatform
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ...prompt import NOTIFIER_PROMPT


@register_agent
class UIUpdaterAgent(Agent):
    """Agent that updates the UI dashboard with resolutions."""

    def __init__(self) -> None:
        super().__init__(
            name="ui_updater",
            description="Updates UI dashboard with issue resolutions",
        )

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Update UI dashboard with resolution.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing UI update status
        """
        resolution = context.session.state.get("final_resolution")
        if not resolution:
            return {"ui_updated": False}
        
        # Format dashboard update
        dashboard_data = {
            "type": "trending_issue",
            "status": "active",
            "issue_type": resolution["issue_type"],
            "product_area": resolution["product_area"],
            "summary": context.session.state["summary"]["text"],
            "resolution": {
                "steps": resolution["steps"],
                "verification": resolution["verification"],
            },
            "affected_users": context.session.state["summary"]["primary_issue"]["count"],
            "timestamp": resolution["generated_at"],
        }
        
        # In a real implementation, this would use Firebase Admin SDK
        # to update the dashboard. For this example, we'll just log it.
        print(f"Dashboard Update: {json.dumps(dashboard_data, indent=2)}")
        
        return {"ui_updated": True}


@register_agent
class EmailDispatcherAgent(Agent):
    """Agent that sends email notifications about resolutions."""

    def __init__(self) -> None:
        super().__init__(
            name="email_dispatcher",
            description="Sends email notifications about issue resolutions",
            prompt=NOTIFIER_PROMPT,
        )

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Send email notifications about the resolution.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing email dispatch status
        """
        resolution = context.session.state.get("final_resolution")
        if not resolution:
            return {"emails_sent": False}
        
        # Get Vertex AI client for email content generation
        vertex_ai = aiplatform.gapic.VertexAIClient()
        
        # Generate email content
        prompt = f"""{self.prompt}

Please generate an email notification for the following resolution:

Issue Type: {resolution['issue_type']}
Product Area: {resolution['product_area']}
Resolution Steps: {resolution['steps']}

The email should be professional, clear, and actionable."""
        
        response = await vertex_ai.predict_text(
            model_name="gemini-pro",
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=1024,
        )
        
        # Parse email content
        email_content = response.text
        
        # In a real implementation, this would use SendGrid to send emails
        # For this example, we'll just log it
        print(f"Email Content: {email_content}")
        
        return {"emails_sent": True}


@register_agent
class CRMCommentAgent(Agent):
    """Agent that updates CRM tickets with resolutions."""

    def __init__(self) -> None:
        super().__init__(
            name="crm_comment",
            description="Updates CRM tickets with issue resolutions",
        )

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Update CRM tickets with resolution information.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing CRM update status
        """
        resolution = context.session.state.get("final_resolution")
        summary = context.session.state.get("summary")
        if not resolution or not summary:
            return {"crm_updated": False}
        
        # Format CRM update
        crm_data = {
            "issue_type": resolution["issue_type"],
            "product_area": resolution["product_area"],
            "affected_customers": summary["primary_issue"]["count"],
            "resolution": {
                "root_cause": resolution["root_cause"],
                "steps": resolution["steps"],
                "verification": resolution["verification"],
            },
            "kb_articles": resolution["kb_articles_used"],
            "timestamp": resolution["generated_at"],
        }
        
        # In a real implementation, this would use the CRM's API
        # For this example, we'll just log it
        print(f"CRM Update: {json.dumps(crm_data, indent=2)}")
        
        return {"crm_updated": True}


@register_agent
class NotifierAgent(SequentialAgent):
    """Agent that coordinates notifications across all channels."""

    def __init__(self) -> None:
        super().__init__(
            name="notifier",
            description="Manages consistent communication across channels",
            sub_agents=[
                UIUpdaterAgent(),
                EmailDispatcherAgent(),
                CRMCommentAgent(),
            ],
        )

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Coordinate notifications across all channels.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing notification status
        """
        # Execute all notification sub-agents
        results = await super().process(context)
        
        # Collect notification status
        notifications = {
            "ui": results.get("ui_updated", False),
            "email": results.get("emails_sent", False),
            "crm": results.get("crm_updated", False),
        }
        
        # Update session state
        context.session.state["notifications_sent"] = notifications
        
        return {"notifications": notifications}