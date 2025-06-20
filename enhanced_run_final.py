"""Enhanced final runner with CRM integration and human intervention."""

import asyncio
import os
from datetime import datetime
from google.cloud import bigquery, datastore

# Import the new tools and agents
from trending_issue_resolver.tools.crm_tool import CRMTool
from trending_issue_resolver.sub_agents.human_intervention.agent import HumanInterventionAgent

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

async def detect_trending_issues():
    """Detect trending issues using actual table structure."""
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
        query.add_filter("product_area", "=", product_area)
        query.add_filter("status", "=", "active")
        
        entities = list(query.fetch(limit=3))
        
        if not entities:
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
            print("No KB articles found, creating default resolution")
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
    """Generate comprehensive resolution."""
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

async def create_crm_ticket(issue, resolution):
    """Create CRM ticket for the issue."""
    print("🎫 Creating CRM ticket...")
    
    # Initialize CRM tool with demo configuration
    crm_config = {
        "base_url": "https://api.example-crm.com",
        "api_key": "demo-api-key-12345"
    }
    
    crm_tool = CRMTool(crm_config)
    
    # Determine priority based on severity and impact
    priority = "urgent" if issue["count"] > 50 or issue["severity"] == "critical" else "high"
    
    # Create CRM ticket
    crm_response = await crm_tool.create_incident_ticket(
        issue_summary=issue,
        resolution=resolution,
        priority=priority
    )
    
    # Store CRM ticket ID in resolution
    resolution["crm_ticket_id"] = crm_response.get("ticket_id")
    
    return crm_response

async def check_human_intervention(issue, resolution):
    """Check if human intervention is needed."""
    print("👤 Evaluating need for human intervention...")
    
    # Create human intervention agent
    human_agent = HumanInterventionAgent()
    
    # Mock context for evaluation
    class MockContext:
        def __init__(self):
            self.session = MockSession()
        def get_tool(self, name):
            if name == "crm_tool":
                return CRMTool({
                    "base_url": "https://api.example-crm.com",
                    "api_key": "demo-api-key-12345"
                })
            return None
    
    class MockSession:
        def __init__(self):
            self.state = {
                "summary": {"primary_issue": issue},
                "final_resolution": resolution
            }
    
    context = MockContext()
    
    # Evaluate human intervention need
    intervention_result = await human_agent.process(context)
    
    return intervention_result

async def main():
    """Enhanced main execution with CRM and human intervention."""
    print("🚀 Enhanced Trending Issue Resolver")
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
        
        # Step 4: Create CRM ticket
        crm_response = await create_crm_ticket(issue, resolution)
        
        # Step 5: Check for human intervention
        intervention_result = await check_human_intervention(issue, resolution)
        
        # Step 6: Display comprehensive results
        print("\n" + "=" * 60)
        print("ENHANCED RESOLUTION COMPLETE")
        print("=" * 60)
        
        print(f"\n📊 ISSUE DETECTED:")
        print(f"   Type: {issue['issue_type']}")
        print(f"   Severity: {issue['severity']}")
        print(f"   Affected Users: {issue['count']}")
        
        print(f"\n🎫 CRM INTEGRATION:")
        print(f"   Ticket ID: {crm_response.get('ticket_id', 'N/A')}")
        print(f"   Status: {crm_response.get('status', 'N/A')}")
        
        print(f"\n👤 HUMAN INTERVENTION:")
        if intervention_result.get("escalation_needed"):
            details = intervention_result["escalation_details"]
            print(f"   🚨 ESCALATION REQUIRED")
            print(f"   Level: {details['escalation_level'].upper()}")
            print(f"   Team: {details['recommended_team']}")
            print(f"   Response Time: {details['estimated_response_time']}")
            print(f"   Reasons: {', '.join(details['reasons'])}")
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