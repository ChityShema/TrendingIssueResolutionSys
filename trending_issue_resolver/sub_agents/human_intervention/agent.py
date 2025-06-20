"""Human Intervention Agent for escalating complex issues."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from google.adk.agents import Agent, AgentContext, register_agent
from google.adk.managers import SessionState

@register_agent
class HumanInterventionAgent(Agent):
    """Agent that determines when human intervention is required."""

    def __init__(self) -> None:
        super().__init__(
            name="human_intervention",
            description="Evaluates issues and escalates to humans when needed",
        )

    def _should_escalate(self, issue_summary: Dict[str, Any], resolution: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if issue requires human intervention.
        
        Args:
            issue_summary: Summary of the trending issue
            resolution: Generated resolution
            
        Returns:
            Escalation decision with reasons
        """
        escalation_reasons = []
        escalation_score = 0
        
        # Check severity and impact
        if issue_summary.get("count", 0) > 100:
            escalation_reasons.append("High impact: >100 users affected")
            escalation_score += 3
        elif issue_summary.get("count", 0) > 50:
            escalation_reasons.append("Medium-high impact: >50 users affected")
            escalation_score += 2
            
        # Check issue type criticality
        critical_types = ["database", "authentication", "payment"]
        if issue_summary.get("issue_type") in critical_types:
            escalation_reasons.append(f"Critical service affected: {issue_summary.get('issue_type')}")
            escalation_score += 2
            
        # Check if multiple services affected (cascade failure)
        if len(escalation_reasons) > 1:
            escalation_reasons.append("Multiple critical systems affected")
            escalation_score += 2
            
        # Check resolution confidence
        kb_articles_used = resolution.get("kb_articles_used", 0)
        if kb_articles_used == 0:
            escalation_reasons.append("No knowledge base articles found")
            escalation_score += 2
        elif kb_articles_used < 2:
            escalation_reasons.append("Limited knowledge base coverage")
            escalation_score += 1
            
        # Check for novel/unknown issues
        if "unknown" in str(resolution.get("resolution_text", "")).lower():
            escalation_reasons.append("Unknown or novel issue pattern")
            escalation_score += 3
            
        # Escalation decision
        should_escalate = escalation_score >= 4
        escalation_level = "urgent" if escalation_score >= 6 else "high" if escalation_score >= 4 else "normal"
        
        return {
            "should_escalate": should_escalate,
            "escalation_score": escalation_score,
            "escalation_level": escalation_level,
            "reasons": escalation_reasons,
            "recommended_team": self._get_recommended_team(issue_summary),
            "estimated_response_time": self._get_response_time(escalation_level)
        }

    def _get_recommended_team(self, issue_summary: Dict[str, Any]) -> str:
        """Get recommended team for escalation based on issue type."""
        team_mapping = {
            "authentication": "identity_team",
            "payment": "billing_team", 
            "database": "infrastructure_team",
            "api": "platform_team",
            "notification": "communication_team"
        }
        return team_mapping.get(issue_summary.get("issue_type"), "incident_response_team")

    def _get_response_time(self, escalation_level: str) -> str:
        """Get expected response time based on escalation level."""
        response_times = {
            "urgent": "15 minutes",
            "high": "30 minutes", 
            "normal": "1 hour"
        }
        return response_times.get(escalation_level, "1 hour")

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Evaluate if human intervention is needed.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing escalation decision and actions taken
        """
        summary = context.session.state.get("summary")
        resolution = context.session.state.get("final_resolution")
        
        if not summary or not resolution:
            return {"human_intervention": None}
        
        # Evaluate escalation need
        escalation_decision = self._should_escalate(summary["primary_issue"], resolution)
        
        result = {
            "escalation_needed": escalation_decision["should_escalate"],
            "escalation_details": escalation_decision
        }
        
        # If escalation needed, trigger CRM escalation
        if escalation_decision["should_escalate"]:
            crm_tool = context.get_tool("crm_tool")
            if crm_tool:
                # Create escalation ticket
                escalation_response = await crm_tool.escalate_to_human(
                    ticket_id=resolution.get("crm_ticket_id", "AUTO-GENERATED"),
                    escalation_reason="; ".join(escalation_decision["reasons"]),
                    assigned_team=escalation_decision["recommended_team"]
                )
                
                result["crm_escalation"] = escalation_response
                
                # Update session state
                context.session.state["escalated_to_human"] = True
                context.session.state["escalation_details"] = escalation_decision
                
                print(f"🚨 HUMAN INTERVENTION REQUIRED")
                print(f"   Escalation Level: {escalation_decision['escalation_level'].upper()}")
                print(f"   Assigned Team: {escalation_decision['recommended_team']}")
                print(f"   Expected Response: {escalation_decision['estimated_response_time']}")
                print(f"   Reasons: {', '.join(escalation_decision['reasons'])}")
            else:
                print("⚠️  CRM tool not available for escalation")
        else:
            print("✅ No human intervention required - automated resolution sufficient")
            context.session.state["escalated_to_human"] = False
        
        return result