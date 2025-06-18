"""ExitCondition agent for determining when to escalate issues."""

from typing import Any, Dict, Optional

from google.adk import Agent, AgentContext, register_agent
from google.adk.managers import SessionState


@register_agent
class ExitConditionAgent(Agent):
    """Agent that determines when to escalate trending issues."""

    def __init__(self) -> None:
        super().__init__(
            name="exit_condition",
            description="Evaluates trending issues and determines when to escalate",
        )

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Evaluate current trends and determine if escalation is needed.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing escalation decision and reasons
        """
        trending_issues = context.session.state.get("trending_issues", [])
        historical_context = context.session.state.get("historical_context", {})
        
        escalation_reasons = []
        should_escalate = False
        
        # No trends found - continue monitoring
        if not trending_issues:
            return {
                "should_escalate": False,
                "reasons": ["No trending issues detected"],
            }
        
        primary_issue = trending_issues[0]
        
        # Check escalation conditions
        
        # 1. Severity-based escalation
        if primary_issue["severity"] in ["critical", "high"]:
            escalation_reasons.append(
                f"High severity issue detected: {primary_issue['severity']}"
            )
            should_escalate = True
        
        # 2. Volume-based escalation
        if historical_context:
            avg_daily = historical_context.get("avg_daily_incidents", 0)
            current_count = primary_issue["count"]
            
            if current_count > (avg_daily * 2):  # 2x normal volume
                escalation_reasons.append(
                    f"Abnormal volume: {current_count} vs avg {avg_daily:.1f}"
                )
                should_escalate = True
        
        # 3. Multiple trending issues
        if len(trending_issues) > 2:
            escalation_reasons.append(
                f"Multiple trending issues: {len(trending_issues)}"
            )
            should_escalate = True
        
        # 4. Rapid increase in incidents
        recent_incidents = sorted(
            primary_issue["incidents"],
            key=lambda x: x["timestamp"]
        )
        if len(recent_incidents) >= 5:
            # Check if 50% of incidents occurred in last 25% of time window
            time_window = context.session.state.get("time_window_minutes", 60)
            recent_window = time_window * 0.25
            recent_count = sum(
                1 for i in recent_incidents
                if (context.current_time - i["timestamp"]).total_seconds() <= (recent_window * 60)
            )
            if recent_count >= (len(recent_incidents) * 0.5):
                escalation_reasons.append("Rapid increase in incident rate")
                should_escalate = True
        
        # Update session state
        context.session.state["exit_signal"] = should_escalate
        
        return {
            "should_escalate": should_escalate,
            "reasons": escalation_reasons or ["Conditions normal - continue monitoring"],
        }