"""Script to populate Datastore with sample knowledge base and response data."""

from datetime import datetime, timedelta
from google.cloud import datastore

def populate_knowledge_base(client):
    """Populate knowledge base with sample articles."""
    
    articles = [
        {
            "title": "Login Authentication Failures",
            "issue_type": "authentication",
            "product_area": "user_management",
            "content": "Common causes: expired tokens, incorrect credentials, rate limiting. Solution: Clear cache, reset password, check API limits.",
            "status": "active",
            "success_rate": 85,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Payment Processing Errors",
            "issue_type": "payment",
            "product_area": "billing",
            "content": "Payment gateway timeouts, invalid card details, insufficient funds. Solution: Retry payment, validate card info, check account balance.",
            "status": "active",
            "success_rate": 92,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Database Connection Issues",
            "issue_type": "database",
            "product_area": "infrastructure",
            "content": "Connection pool exhaustion, network timeouts, credential issues. Solution: Restart connection pool, check network, verify credentials.",
            "status": "active",
            "success_rate": 78,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "API Rate Limiting",
            "issue_type": "api",
            "product_area": "platform",
            "content": "Too many requests, quota exceeded, throttling. Solution: Implement backoff, increase limits, optimize request frequency.",
            "status": "active",
            "success_rate": 95,
            "last_updated": datetime.utcnow().timestamp()
        },
        {
            "title": "Email Delivery Failures",
            "issue_type": "notification",
            "product_area": "communication",
            "content": "SMTP errors, blacklisted domains, invalid addresses. Solution: Check SMTP config, verify domain reputation, validate email addresses.",
            "status": "active",
            "success_rate": 88,
            "last_updated": datetime.utcnow().timestamp()
        }
    ]
    
    for article in articles:
        key = client.key("knowledge_base")
        entity = datastore.Entity(key=key)
        entity.update(article)
        client.put(entity)
        print(f"Added KB article: {article['title']}")

def populate_response_history(client):
    """Populate response history with sample data."""
    
    responses = [
        {
            "timestamp": (datetime.utcnow() - timedelta(days=5)).timestamp(),
            "issue_type": "authentication",
            "product_area": "user_management",
            "issue_summary": {
                "issue_type": "authentication",
                "product_area": "user_management",
                "count": 150,
                "text": "Multiple users reporting login failures"
            },
            "resolution": {
                "root_cause": "Expired authentication tokens",
                "steps": ["Clear browser cache", "Reset user sessions", "Update token expiry"],
                "communication_template": "We've identified and resolved login issues. Please clear your browser cache and try again."
            },
            "channels": ["email", "slack"],
            "metrics": {
                "affected_customers": 150,
                "resolution_time": 45,
                "success_rate": 95
            }
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(days=12)).timestamp(),
            "issue_type": "payment",
            "product_area": "billing",
            "issue_summary": {
                "issue_type": "payment",
                "product_area": "billing",
                "count": 75,
                "text": "Payment processing delays and failures"
            },
            "resolution": {
                "root_cause": "Payment gateway timeout issues",
                "steps": ["Switch to backup gateway", "Increase timeout limits", "Implement retry logic"],
                "communication_template": "Payment processing has been restored. Failed transactions will be automatically retried."
            },
            "channels": ["email", "dashboard"],
            "metrics": {
                "affected_customers": 75,
                "resolution_time": 120,
                "success_rate": 98
            }
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(days=20)).timestamp(),
            "issue_type": "database",
            "product_area": "infrastructure",
            "issue_summary": {
                "issue_type": "database",
                "product_area": "infrastructure",
                "count": 200,
                "text": "Database connection timeouts affecting multiple services"
            },
            "resolution": {
                "root_cause": "Connection pool exhaustion",
                "steps": ["Increase connection pool size", "Optimize query performance", "Add connection monitoring"],
                "communication_template": "Database connectivity issues have been resolved. All services are now operating normally."
            },
            "channels": ["email", "slack", "dashboard"],
            "metrics": {
                "affected_customers": 200,
                "resolution_time": 90,
                "success_rate": 92
            }
        }
    ]
    
    for response in responses:
        key = client.key("response_history")
        entity = datastore.Entity(key=key)
        entity.update(response)
        client.put(entity)
        print(f"Added response: {response['issue_type']} - {response['product_area']}")

def main():
    """Main function to populate Datastore."""
    try:
        client = datastore.Client()
        print("Connected to Datastore successfully")
        
        print("\nPopulating knowledge base...")
        populate_knowledge_base(client)
        
        print("\nPopulating response history...")
        populate_response_history(client)
        
        print("\nDatastore populated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()