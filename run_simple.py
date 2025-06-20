"""Simple runner without ADK dependencies."""

import asyncio
import os
from datetime import datetime
from google.cloud import bigquery, datastore, aiplatform

# Set project ID
os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

async def detect_trending_issues():
    """Detect trending issues from BigQuery."""
    print("🔍 Detecting trending issues...")
    
    bq_client = bigquery.Client()
    
    query = f"""
    WITH recent_issues AS (
        SELECT 
            issue_type,
            product_area,
            description,
            severity,
            COUNT(*) as occurrence_count
        FROM `{bq_client.project}.customer_interactions.issues`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 MINUTE)
        GROUP BY issue_type, product_area, description, severity
        HAVING COUNT(*) >= 5
    )
    SELECT *
    FROM recent_issues
    ORDER BY occurrence_count DESC
    LIMIT 3
    """
    
    results = list(bq_client.query(query).result())
    
    if not results:
        print("❌ No trending issues found")
        return None
    
    trending_issue = {
        "issue_type": results[0].issue_type,
        "product_area": results[0].product_area,
        "description": results[0].description,
        "severity": results[0].severity,
        "count": results[0].occurrence_count
    }
    
    print(f"✓ Found trending issue: {trending_issue['issue_type']} ({trending_issue['count']} occurrences)")
    return trending_issue

async def search_knowledge_base(issue_type, product_area):
    """Search knowledge base in Datastore."""
    print("📚 Searching knowledge base...")
    
    ds_client = datastore.Client()
    
    query = ds_client.query(kind="knowledge_base")
    query.add_filter("issue_type", "=", issue_type)
    query.add_filter("product_area", "=", product_area)
    query.add_filter("status", "=", "active")
    
    entities = list(query.fetch(limit=3))
    
    if not entities:
        print("❌ No knowledge base articles found")
        return []
    
    articles = []
    for entity in entities:
        article = {
            "title": entity.get("title", ""),
            "content": entity.get("content", ""),
            "success_rate": entity.get("success_rate", 0)
        }
        articles.append(article)
    
    print(f"✓ Found {len(articles)} knowledge base articles")
    return articles

async def generate_resolution(issue, articles):
    """Generate resolution using Vertex AI."""
    print("🤖 Generating resolution...")
    
    # Format context
    context = f"""
    Issue: {issue['issue_type']} in {issue['product_area']}
    Description: {issue['description']}
    Severity: {issue['severity']}
    Affected Users: {issue['count']}
    
    Knowledge Base Articles:
    """
    
    for i, article in enumerate(articles, 1):
        context += f"\nArticle {i}: {article['title']}\n{article['content']}\n"
    
    prompt = f"""
    Based on the following trending issue and knowledge base articles, provide a comprehensive resolution:
    
    {context}
    
    Please provide:
    1. Root cause analysis
    2. Step-by-step resolution
    3. Verification steps
    4. Customer communication template
    """
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=os.environ["GOOGLE_CLOUD_PROJECT"])
        
        from vertexai.generative_models import GenerativeModel
        model = GenerativeModel("gemini-pro")
        
        response = model.generate_content(prompt)
        
        resolution = {
            "issue_type": issue["issue_type"],
            "product_area": issue["product_area"],
            "resolution_text": response.text,
            "generated_at": datetime.now().isoformat()
        }
        
        print("✓ Resolution generated successfully")
        return resolution
        
    except Exception as e:
        print(f"❌ Error generating resolution: {e}")
        return {
            "issue_type": issue["issue_type"],
            "product_area": issue["product_area"],
            "resolution_text": "Manual resolution required - AI generation failed",
            "generated_at": datetime.now().isoformat()
        }

async def save_resolution(issue, resolution):
    """Save resolution to Datastore."""
    print("💾 Saving resolution...")
    
    ds_client = datastore.Client()
    
    key = ds_client.key("response_history")
    entity = datastore.Entity(key=key)
    
    entity.update({
        "timestamp": datetime.utcnow().timestamp(),
        "issue_type": issue["issue_type"],
        "product_area": issue["product_area"],
        "issue_summary": issue,
        "resolution": resolution,
        "channels": ["console"],
        "metrics": {
            "affected_customers": issue["count"],
            "resolution_time": None,
            "success_rate": None,
        }
    })
    
    ds_client.put(entity)
    print("✓ Resolution saved to Datastore")

async def main():
    """Main execution function."""
    print("🚀 Trending Issue Resolver (Simplified)")
    print("=" * 50)
    
    try:
        # Step 1: Detect trending issues
        issue = await detect_trending_issues()
        if not issue:
            print("No trending issues to process")
            return
        
        # Step 2: Search knowledge base
        articles = await search_knowledge_base(issue["issue_type"], issue["product_area"])
        
        # Step 3: Generate resolution
        resolution = await generate_resolution(issue, articles)
        
        # Step 4: Save resolution
        await save_resolution(issue, resolution)
        
        # Step 5: Display results
        print("\n" + "=" * 50)
        print("FINAL RESULTS")
        print("=" * 50)
        print(f"\n📊 ISSUE: {issue['issue_type']} in {issue['product_area']}")
        print(f"Severity: {issue['severity']}")
        print(f"Affected Users: {issue['count']}")
        print(f"\n🔧 RESOLUTION:\n{resolution['resolution_text']}")
        
        print("\n✅ Process completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())