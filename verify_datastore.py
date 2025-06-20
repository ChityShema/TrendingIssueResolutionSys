"""Script to verify Datastore data population."""

from google.cloud import datastore

def verify_knowledge_base(client):
    """Verify knowledge base data."""
    query = client.query(kind="knowledge_base")
    entities = list(query.fetch())
    
    print(f"Knowledge Base Articles: {len(entities)}")
    for entity in entities:
        print(f"  - {entity['title']} ({entity['issue_type']}/{entity['product_area']})")

def verify_response_history(client):
    """Verify response history data."""
    query = client.query(kind="response_history")
    entities = list(query.fetch())
    
    print(f"Response History Records: {len(entities)}")
    for entity in entities:
        print(f"  - {entity['issue_type']}/{entity['product_area']} - {entity['metrics']['affected_customers']} customers")

def test_search_functionality(client):
    """Test search functionality."""
    print("\nTesting search functionality:")
    
    # Test knowledge base search
    query = client.query(kind="knowledge_base")
    query.add_filter("issue_type", "=", "authentication")
    query.add_filter("product_area", "=", "user_management")
    results = list(query.fetch())
    print(f"Authentication/User Management articles: {len(results)}")
    
    # Test response history search
    query = client.query(kind="response_history")
    query.add_filter("issue_type", "=", "payment")
    results = list(query.fetch())
    print(f"Payment-related responses: {len(results)}")

def main():
    """Main verification function."""
    try:
        client = datastore.Client()
        print("Connected to Datastore successfully\n")
        
        verify_knowledge_base(client)
        print()
        verify_response_history(client)
        
        test_search_functionality(client)
        
        print("\nVerification completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()