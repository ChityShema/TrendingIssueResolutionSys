"""Simple runner script to test the Trending Issue Resolver system."""

import asyncio
import os
from datetime import datetime

from google.adk.managers import SessionManager
from trending_issue_resolver import TrendingIssueResolverAgent

async def main():
    """Run the trending issue resolver agent."""
    print("Starting Trending Issue Resolver...")
    print(f"Timestamp: {datetime.now()}")
    
    try:
        # Initialize the main agent
        agent = TrendingIssueResolverAgent()
        print("✓ Agent initialized successfully")
        
        # Create session manager
        session_manager = SessionManager()
        session = session_manager.create_session()
        print("✓ Session created")
        
        # Create agent context
        from google.adk.agents import AgentContext
        context = AgentContext(
            session=session,
            current_time=datetime.now()
        )
        print("✓ Context created")
        
        # Run the agent
        print("\n🔍 Running trending issue detection...")
        result = await agent.process(context)
        
        # Display results
        print("\n" + "="*50)
        print("RESULTS")
        print("="*50)
        
        if result.get("summary"):
            summary = result["summary"]
            print(f"\n📊 ISSUE SUMMARY:")
            print(f"Type: {summary['primary_issue']['type']}")
            print(f"Product Area: {summary['primary_issue']['product_area']}")
            print(f"Affected Users: {summary['primary_issue']['count']}")
            print(f"Severity: {summary['primary_issue']['severity']}")
            print(f"\nDescription: {summary['text']}")
        
        if result.get("resolution"):
            resolution = result["resolution"]
            print(f"\n🔧 RESOLUTION:")
            print(f"Root Cause: {resolution['root_cause']}")
            print(f"Steps: {resolution['steps']}")
            print(f"Verification: {resolution['verification']}")
        
        if result.get("notifications_sent"):
            notifications = result["notifications_sent"]
            print(f"\n📢 NOTIFICATIONS:")
            for channel, sent in notifications.items():
                status = "✓" if sent else "✗"
                print(f"{status} {channel.upper()}")
        
        print("\n✅ Agent execution completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "your-project-id")
    
    # Run the agent
    asyncio.run(main())