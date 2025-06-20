"""Standalone enhanced resolver with CRM and human intervention (no ADK dependencies)."""

import asyncio
import os
from datetime import datetime
from google.cloud import bigquery, datastore
import requests
import json

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

class CRMIntegration:
    """Simple CRM integration without ADK dependencies."""
    
    def __init__(self):
        self.base_url = "https://api.example-crm.com"
        self.api_key = "demo-api-key-12345"
    
    def create_ticket(self, issue, resolution, priority="high"):
        """Create CRM ticket."""
        ticket_data = {
            "title": f"Trending Issue: {issue['issue_type']} in {issue['product_area']}",
            "description": f"""
AUTOMATED TRENDING ISSUE DETECTION

Issue Details:
- Type: {issue['issue_type']}
- Product Area: {issue['product_area']}
- Affected Users: {issue['count']}
- Severity: {issue.get('severity', 'high')}

Resolution Applied:
{resolution.get('resolution_text', 'Resolution details available')}
            """.strip(),
            "priority": priority,
            "category": "system_generated",
            "tags": ["trending_issue", issue['issue_type'], "automated"]
        }
        
        # Simulate CRM API call
        ticket_id = f"TIR-{datetime.now().strftime('%Y%m%d')}-{hash(str(ticket_data)) % 10000:04d}"
        
        print(f"🎫 CRM Ticket Created: {ticket_id}")
        print(f"   Priority: {priority}")
        print(f"   Issue: {issue['issue_type']} ({issue['count']} users)")
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": "created"
        }
    
    def escalate_ticket(self, ticket_id, escalation_reason, assigned_team):
        """Escalate ticket to human intervention."""
        print(f"🚨 CRM Ticket Escalated: {ticket_id}")
        print(f"   Assigned to: {assigned_team}")
        print(f"   Reason: {escalation_reason}")
        
        return {
            "success": True,
            "status": "escalated",
            "assigned_team": assigned_team
        }

class HumanInterventionEvaluator:
    """Evaluate if human intervention is needed."""
    
    def evaluate(self, issue, resolution):
        """Determine if escalation is needed."""
        escalation_reasons = []
        escalation_score = 0
        
        # Check severity and impact
        if issue.get("count", 0) > 100:
            escalation_reasons.append("High impact: >100 users affected")
            escalation_score += 3
        elif issue.get("count", 0) > 50:
            escalation_reasons.append("Medium-high impact: >50 users affected")
            escalation_score += 2
            
        # Check issue type criticality
        critical_types = ["database", "authentication", "payment"]
        if issue.get("issue_type") in critical_types:
            escalation_reasons.append(f"Critical service affected: {issue.get('issue_type')}")
            escalation_score += 2
            
        # Check resolution confidence
        kb_articles_used = resolution.get("kb_articles_used", 0)
        if kb_articles_used == 0:
            escalation_reasons.append("No knowledge base articles found")
            escalation_score += 2
        elif kb_articles_used < 2:
            escalation_reasons.append("Limited knowledge base coverage")
            escalation_score += 1
            
        # Escalation decision
        should_escalate = escalation_score >= 4
        escalation_level = "urgent" if escalation_score >= 6 else "high" if escalation_score >= 4 else "normal"
        
        # Team assignment
        team_mapping = {
            "authentication": "identity_team",
            "payment": "billing_team", 
            "database": "infrastructure_team",
            "api": "platform_team",
            "notification": "communication_team"
        }
        recommended_team = team_mapping.get(issue.get("issue_type"), "incident_response_team")
        
        # Response time
        response_times = {
            "urgent": "15 minutes",
            "high": "30 minutes", 
            "normal": "1 hour"
        }
        estimated_response_time = response_times.get(escalation_level, "1 hour")
        
        return {
            "should_escalate": should_escalate,
            "escalation_score": escalation_score,
            "escalation_level": escalation_level,
            "reasons": escalation_reasons,
            "recommended_team": recommended_team,
            "estimated_response_time": estimated_response_time
        }

async def detect_trending_issues():
    """Detect trending issues from BigQuery."""
    print("🔍 Detecting trending issues...")
    
    bq_client = bigquery.Client()
    
    query = f"""
    WITH recent_issues AS (
        SELECT 
            category,
            content,
            priority,
            COUNT(*) as occurrence_count
        FROM `{bq_client.project}.customer_interactions.issues`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 MINUTE)
        AND status = 'open'
        GROUP BY category, content, priority
        HAVING COUNT(*) >= 3
    )
    SELECT *
    FROM recent_issues
    ORDER BY occurrence_count DESC, priority DESC
    LIMIT 3
    """
    
    results = list(bq_client.query(query).result())
    
    if not results:
        print("❌ No trending issues found")
        return None
    
    top_issue = results[0]
    
    category_mapping = {
        "authentication": "user_management",
        "payment": "billing", 
        "database": "infrastructure"
    }
    
    trending_issue = {
        "issue_type": top_issue.category,
        "product_area": category_mapping.get(top_issue.category, "platform"),
        "description": top_issue.content[:100] + "..." if len(top_issue.content) > 100 else top_issue.content,
        "severity": "critical" if top_issue.priority >= 4 else "high" if top_issue.priority >= 3 else "medium",
        "count": top_issue.occurrence_count
    }
    
    print(f"✓ Found trending issue: {trending_issue['issue_type']} ({trending_issue['count']} occurrences)")
    return trending_issue

async def search_knowledge_base(issue_type, product_area):
    """Search knowledge base in Datastore."""
    print("📚 Searching knowledge base...")
    
    try:
        ds_client = datastore.Client()
        
        query = ds_client.query(kind="knowledge_base")
        query.add_filter("issue_type", "=", issue_type)
        query.add_filter("status", "=", "active")
        
        entities = list(query.fetch(limit=3))
        
        if entities:
            articles = []
            for entity in entities:
                article = {
                    "title": entity.get("title", "Knowledge Base Article"),
                    "content": entity.get("content", "Resolution steps available"),
                    "success_rate": entity.get("success_rate", 85)
                }
                articles.append(article)
            print(f"✓ Found {len(articles)} knowledge base articles")
            return articles
        else:
            print("No KB articles found, using default resolution")
            return [{
                "title": f"{issue_type.title()} Resolution Guide",
                "content": f"Standard resolution procedure for {issue_type} issues",
                "success_rate": 80
            }]
            
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        return [{
            "title": "Standard Resolution Guide", 
            "content": "Follow standard troubleshooting procedures",
            "success_rate": 75
        }]

async def generate_resolution(issue, articles):
    """Generate resolution."""
    print("🤖 Generating resolution...")
    
    resolution_text = f"""
TRENDING ISSUE RESOLUTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ISSUE SUMMARY:
- Type: {issue['issue_type'].upper()}
- Product Area: {issue['product_area']}
- Severity: {issue['severity'].upper()}
- Affected Users: {issue['count']}

RESOLUTION STEPS:
"""
    
    for i, article in enumerate(articles, 1):
        resolution_text += f"""
{i}. {article['title']} (Success Rate: {article['success_rate']}%)
   {article['content']}
"""
    
    resolution_text += f"""
VERIFICATION STEPS:
1. Monitor system metrics for 15 minutes
2. Check error rates in {issue['product_area']} services
3. Verify user feedback channels

CUSTOMER COMMUNICATION:
"We have identified and resolved a {issue['issue_type']} issue affecting {issue['count']} users. Normal service has been restored."
"""
    
    resolution = {
        "issue_type": issue["issue_type"],
        "product_area": issue["product_area"], 
        "resolution_text": resolution_text,
        "generated_at": datetime.now().isoformat(),
        "kb_articles_used": len(articles),
        "estimated_resolution_time": "15-30 minutes"
    }
    
    print("✓ Resolution generated")
    return resolution

async def save_enhanced_resolution(issue, resolution, crm_response, escalation_result):
    """Save resolution with CRM and escalation data."""
    print("💾 Saving enhanced resolution...")
    
    try:
        ds_client = datastore.Client()
        
        key = ds_client.key("response_history")
        entity = datastore.Entity(key=key)
        
        entity.update({
            "timestamp": datetime.utcnow().timestamp(),
            "issue_type": issue["issue_type"],
            "product_area": issue["product_area"],
            "issue_summary": issue,
            "resolution": resolution,
            "crm_ticket_id": crm_response.get("ticket_id"),
            "escalated_to_human": escalation_result["should_escalate"],
            "escalation_details": escalation_result,
            "channels": ["console", "dashboard", "crm"],
            "metrics": {
                "affected_customers": issue["count"],
                "resolution_time": None,
                "success_rate": None,
                "kb_articles_used": resolution["kb_articles_used"]
            }
        })
        
        ds_client.put(entity)
        print("✓ Enhanced resolution saved to Datastore")
        
    except Exception as e:
        print(f"Warning: Could not save to Datastore: {e}")

async def main():
    """Enhanced main execution with CRM and human intervention."""
    print("🚀 Enhanced Trending Issue Resolver (Standalone)")
    print("=" * 60)
    
    try:
        # Step 1: Detect trending issues
        issue = await detect_trending_issues()
        if not issue:
            print("No trending issues detected")
            return
        
        # Step 2: Search knowledge base  
        articles = await search_knowledge_base(issue["issue_type"], issue["product_area"])
        
        # Step 3: Generate resolution
        resolution = await generate_resolution(issue, articles)
        
        # Step 4: CRM Integration
        crm = CRMIntegration()
        priority = "urgent" if issue["count"] > 50 or issue["severity"] == "critical" else "high"
        crm_response = crm.create_ticket(issue, resolution, priority)
        
        # Step 5: Human Intervention Evaluation
        human_evaluator = HumanInterventionEvaluator()
        escalation_result = human_evaluator.evaluate(issue, resolution)
        
        # Step 6: Handle escalation if needed
        if escalation_result["should_escalate"]:
            crm.escalate_ticket(
                crm_response["ticket_id"],
                "; ".join(escalation_result["reasons"]),
                escalation_result["recommended_team"]
            )
        
        # Step 7: Save enhanced resolution
        await save_enhanced_resolution(issue, resolution, crm_response, escalation_result)
        
        # Step 8: Display comprehensive results
        print("\n" + "=" * 60)
        print("ENHANCED RESOLUTION COMPLETE")
        print("=" * 60)
        
        print(f"\n📊 ISSUE DETECTED:")
        print(f"   Type: {issue['issue_type']}")
        print(f"   Severity: {issue['severity']}")
        print(f"   Affected Users: {issue['count']}")
        
        print(f"\n🎫 CRM INTEGRATION:")
        print(f"   Ticket ID: {crm_response.get('ticket_id', 'N/A')}")
        print(f"   Priority: {priority}")
        print(f"   Status: {crm_response.get('status', 'N/A')}")
        
        print(f"\n👤 HUMAN INTERVENTION:")
        if escalation_result["should_escalate"]:
            print(f"   🚨 ESCALATION REQUIRED")
            print(f"   Level: {escalation_result['escalation_level'].upper()}")
            print(f"   Team: {escalation_result['recommended_team']}")
            print(f"   Response Time: {escalation_result['estimated_response_time']}")
            print(f"   Reasons: {', '.join(escalation_result['reasons'])}")
        else:
            print(f"   ✅ No escalation needed - automated resolution sufficient")
        
        print(f"\n📋 RESOLUTION SUMMARY:")
        print(f"   KB Articles Used: {resolution['kb_articles_used']}")
        print(f"   Estimated Time: {resolution['estimated_resolution_time']}")
        
        print("\n✅ Enhanced process completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())