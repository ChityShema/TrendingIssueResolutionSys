"""Demo Runner - Interactive script to run different demo scenarios"""

import subprocess
import sys
import time

def run_scenario(scenario_num):
    """Run a specific demo scenario."""
    scenarios = {
        1: {
            "name": "Authentication Crisis",
            "description": "Major login outage affecting hundreds of users",
            "script": "demo_scenario_1.py"
        },
        2: {
            "name": "E-commerce Peak Traffic", 
            "description": "Black Friday style load issues across payment and infrastructure",
            "script": "demo_scenario_2.py"
        },
        3: {
            "name": "Multi-Service Cascade Failure",
            "description": "Complex interconnected system failure with multiple services affected",
            "script": "demo_scenario_3.py"
        }
    }
    
    if scenario_num not in scenarios:
        print("❌ Invalid scenario number")
        return False
    
    scenario = scenarios[scenario_num]
    print(f"\n🎬 Running Demo Scenario {scenario_num}: {scenario['name']}")
    print(f"📝 Description: {scenario['description']}")
    print("-" * 60)
    
    try:
        subprocess.run([sys.executable, scenario['script']], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running scenario: {e}")
        return False

def run_dashboard():
    """Launch the Streamlit dashboard."""
    print("\n🚀 Launching Trending Issue Resolver Dashboard...")
    print("📊 Dashboard will open at: http://localhost:8501")
    print("⏹️  Press Ctrl+C in the dashboard terminal to stop")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "trending_issue_resolver/dashboard/dashboard.py"
        ])
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def run_trending_resolver():
    """Run the trending issue resolver on current data."""
    print("\n🤖 Running Trending Issue Resolver...")
    try:
        subprocess.run([sys.executable, "run_final.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running resolver: {e}")

def run_enhanced_resolver():
    """Run the enhanced resolver with CRM and human intervention."""
    print("\n🚀 Running Enhanced Resolver (CRM + Human Intervention)...")
    try:
        subprocess.run([sys.executable, "enhanced_standalone.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running enhanced resolver: {e}")

def main():
    """Main demo runner interface."""
    print("🎯 Trending Issue Resolver - Demo Runner")
    print("=" * 50)
    
    while True:
        print("\n📋 Available Demo Options:")
        print("1. 🚨 Authentication Crisis (45 auth issues, 25 payment, 18 API)")
        print("2. 🛒 E-commerce Peak Traffic (35 payment, 28 DB, 22 API, 15 notifications)")
        print("3. ⚡ Multi-Service Cascade Failure (131 total issues across 6 services)")
        print("4. 📊 Launch Dashboard")
        print("5. 🤖 Run Issue Resolver (Basic)")
        print("6. 🚀 Run Enhanced Resolver (CRM + Human Intervention)")
        print("7. 🔄 Show Current Data Summary")
        print("0. ❌ Exit")
        
        try:
            choice = int(input("\n🎯 Select option (0-7): "))
            
            if choice == 0:
                print("👋 Goodbye!")
                break
            elif choice in [1, 2, 3]:
                success = run_scenario(choice)
                if success:
                    print(f"\n✅ Scenario {choice} setup complete!")
                    
                    # Ask if user wants to launch dashboard
                    launch = input("\n🚀 Launch dashboard now? (y/n): ").lower().strip()
                    if launch == 'y':
                        run_dashboard()
                        
            elif choice == 4:
                run_dashboard()
                
            elif choice == 5:
                run_trending_resolver()
                
            elif choice == 6:
                run_enhanced_resolver()
                
            elif choice == 7:
                print("\n📊 Checking current data...")
                try:
                    from google.cloud import bigquery, datastore
                    
                    # Check BigQuery
                    bq_client = bigquery.Client()
                    query = f"SELECT category, COUNT(*) as count FROM `{bq_client.project}.customer_interactions.issues` GROUP BY category ORDER BY count DESC"
                    results = list(bq_client.query(query).result())
                    
                    print("\n📈 Current BigQuery Issues:")
                    total_issues = 0
                    for row in results:
                        print(f"   {row.category}: {row.count}")
                        total_issues += row.count
                    print(f"   TOTAL: {total_issues}")
                    
                    # Check Datastore
                    ds_client = datastore.Client()
                    kb_query = ds_client.query(kind="knowledge_base")
                    kb_count = len(list(kb_query.fetch()))
                    
                    resp_query = ds_client.query(kind="response_history")
                    resp_count = len(list(resp_query.fetch()))
                    
                    print(f"\n📚 Datastore Data:")
                    print(f"   Knowledge Base Articles: {kb_count}")
                    print(f"   Response History: {resp_count}")
                    
                    # Check for CRM integration data
                    crm_tickets = [r for r in list(ds_client.query(kind="response_history").fetch()) if r.get('crm_ticket_id')]
                    escalated = [r for r in list(ds_client.query(kind="response_history").fetch()) if r.get('escalated_to_human')]
                    
                    print(f"\n🎫 CRM Integration:")
                    print(f"   CRM Tickets Created: {len(crm_tickets)}")
                    print(f"   Human Escalations: {len(escalated)}")
                    
                except Exception as e:
                    print(f"❌ Error checking data: {e}")
                    
            else:
                print("❌ Invalid option. Please select 0-7.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()