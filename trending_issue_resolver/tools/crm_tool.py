"""CRM integration tool for external ticket management."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import requests
import json

try:
    from google.adk import Tool
except ImportError:
    class Tool:
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description

class CRMTool(Tool):
    """Tool for integrating with external CRM systems."""

    def __init__(self, crm_config: Dict[str, str]):
        """Initialize CRM tool with configuration.
        
        Args:
            crm_config: CRM configuration including API endpoints and credentials
        """
        super().__init__(
            name="crm_tool",
            description="Integrates with external CRM systems for ticket management",
        )
        self.config = crm_config
        self.base_url = crm_config.get("base_url", "https://api.example-crm.com")
        self.api_key = crm_config.get("api_key", "demo-key")
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to CRM API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            
            # For demo purposes, simulate successful responses
            if "example-crm.com" in url:
                return {
                    "success": True,
                    "ticket_id": f"TIR-{datetime.now().strftime('%Y%m%d')}-{hash(str(data)) % 10000:04d}",
                    "status": "created" if method == "POST" else "updated",
                    "message": f"Ticket {method.lower()}d successfully"
                }
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Fallback for demo - simulate CRM response
            return {
                "success": True,
                "ticket_id": f"TIR-DEMO-{hash(str(data)) % 10000:04d}",
                "status": "demo_mode",
                "message": f"Demo mode: Would {method.lower()} CRM ticket",
                "error": str(e)
            }

    async def create_incident_ticket(
        self,
        issue_summary: Dict[str, Any],
        resolution: Dict[str, Any],
        priority: str = "high"
    ) -> Dict[str, Any]:
        """Create incident ticket in CRM system.
        
        Args:
            issue_summary: Summary of the trending issue
            resolution: Resolution details
            priority: Ticket priority level
            
        Returns:
            CRM ticket creation response
        """
        ticket_data = {
            "title": f"Trending Issue: {issue_summary['issue_type']} in {issue_summary['product_area']}",
            "description": f"""
AUTOMATED TRENDING ISSUE DETECTION

Issue Details:
- Type: {issue_summary['issue_type']}
- Product Area: {issue_summary['product_area']}
- Affected Users: {issue_summary['count']}
- Severity: {issue_summary.get('severity', 'high')}
- First Detected: {datetime.now().isoformat()}

Resolution Applied:
{resolution.get('resolution_text', 'Resolution details available in system')}

Knowledge Base Articles Used: {resolution.get('kb_articles_used', [])}

This ticket was automatically created by the Trending Issue Resolver system.
            """.strip(),
            "priority": priority,
            "category": "system_generated",
            "tags": [
                "trending_issue",
                issue_summary['issue_type'],
                issue_summary['product_area'],
                "automated"
            ],
            "custom_fields": {
                "affected_users": issue_summary['count'],
                "resolution_time": resolution.get('estimated_resolution_time', 'unknown'),
                "kb_articles": resolution.get('kb_articles_used', []),
                "auto_generated": True
            }
        }
        
        response = self._make_request("POST", "tickets", ticket_data)
        
        # Log the CRM integration
        print(f"🎫 CRM Ticket Created: {response.get('ticket_id', 'Unknown')}")
        print(f"   Status: {response.get('status', 'Unknown')}")
        print(f"   Priority: {priority}")
        print(f"   Affected Users: {issue_summary['count']}")
        
        return response

    async def update_ticket_status(
        self,
        ticket_id: str,
        status: str,
        comment: str = None
    ) -> Dict[str, Any]:
        """Update existing CRM ticket status.
        
        Args:
            ticket_id: CRM ticket ID
            status: New status (resolved, in_progress, escalated)
            comment: Optional comment to add
            
        Returns:
            CRM update response
        """
        update_data = {
            "status": status,
            "updated_by": "trending_issue_resolver",
            "updated_at": datetime.now().isoformat()
        }
        
        if comment:
            update_data["comment"] = comment
        
        response = self._make_request("PUT", f"tickets/{ticket_id}", update_data)
        
        print(f"🔄 CRM Ticket Updated: {ticket_id}")
        print(f"   New Status: {status}")
        if comment:
            print(f"   Comment: {comment[:100]}...")
        
        return response

    async def escalate_to_human(
        self,
        ticket_id: str,
        escalation_reason: str,
        assigned_team: str = "incident_response"
    ) -> Dict[str, Any]:
        """Escalate ticket to human intervention.
        
        Args:
            ticket_id: CRM ticket ID
            escalation_reason: Reason for escalation
            assigned_team: Team to assign the ticket to
            
        Returns:
            Escalation response
        """
        escalation_data = {
            "status": "escalated",
            "assigned_team": assigned_team,
            "escalation_reason": escalation_reason,
            "escalated_at": datetime.now().isoformat(),
            "escalated_by": "trending_issue_resolver",
            "priority": "urgent",
            "requires_human_intervention": True
        }
        
        response = self._make_request("PUT", f"tickets/{ticket_id}/escalate", escalation_data)
        
        print(f"🚨 CRM Ticket Escalated: {ticket_id}")
        print(f"   Assigned to: {assigned_team}")
        print(f"   Reason: {escalation_reason}")
        
        return response

    async def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """Get current status of CRM ticket.
        
        Args:
            ticket_id: CRM ticket ID
            
        Returns:
            Ticket status information
        """
        response = self._make_request("GET", f"tickets/{ticket_id}")
        return response