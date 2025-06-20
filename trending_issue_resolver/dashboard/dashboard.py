from typing import Dict, List, Any
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from google.cloud import bigquery, datastore
from datetime import datetime

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

class TrendingIssuesDashboard:
    def __init__(self):
        self.title = "🚀 Trending Issues Resolution Dashboard"

    def run(self):
        st.set_page_config(page_title="Trending Issues Dashboard", layout="wide")
        st.title(self.title)
        
        # Auto-refresh
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Main content
        self._render_overview()
        self._render_trending_issues()
        self._render_human_intervention_panel()
        self._render_crm_integration()
        self._render_knowledge_base()
        self._render_recent_resolutions()
        
    def _get_trending_issues(self):
        try:
            client = bigquery.Client()
            query = f"""
            SELECT 
                category,
                COUNT(*) as count,
                MAX(priority) as max_priority
            FROM `{client.project}.customer_interactions.issues`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
            AND status = 'open'
            GROUP BY category
            ORDER BY count DESC
            """
            return list(client.query(query).result())
        except:
            return []
    
    def _get_kb_stats(self):
        try:
            client = datastore.Client()
            query = client.query(kind="knowledge_base")
            entities = list(query.fetch())
            return entities
        except:
            return []
        
    def _render_overview(self):
        st.header("📊 System Overview")
        
        issues = self._get_trending_issues()
        kb_articles = self._get_kb_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_issues = sum(issue.count for issue in issues)
            st.metric("Active Issues", total_issues)
        with col2:
            active_trends = len([i for i in issues if i.count >= 5])
            st.metric("Trending Issues", active_trends)
        with col3:
            st.metric("KB Articles", len(kb_articles))
        with col4:
            avg_success = sum(a.get('success_rate', 0) for a in kb_articles) / len(kb_articles) if kb_articles else 0
            st.metric("Avg Success Rate", f"{avg_success:.1f}%")
            
    def _render_trending_issues(self):
        st.header("🔥 Trending Issues")
        
        issues = self._get_trending_issues()
        
        if issues:
            data = []
            for issue in issues:
                data.append({
                    'Category': issue.category,
                    'Count': issue.count,
                    'Severity': 'High' if issue.max_priority >= 3 else 'Medium',
                    'Status': 'Active' if issue.count >= 5 else 'Monitoring'
                })
            
            df = pd.DataFrame(data)
            
            # Display table
            st.dataframe(df, use_container_width=True)
            
            # Chart
            fig = px.bar(df, x='Category', y='Count', color='Severity',
                        title="Issue Count by Category")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No trending issues detected")
    
    def _render_human_intervention_panel(self):
        st.header("👤 Human Intervention Panel")
        
        # Get current trending issues for manual intervention
        issues = self._get_trending_issues()
        
        if issues:
            st.subheader("🚨 Manual Escalation Controls")
            
            # Issue selection
            issue_options = [f"{issue.category} ({issue.count} users)" for issue in issues]
            selected_issue_idx = st.selectbox("Select Issue to Escalate:", range(len(issue_options)), 
                                            format_func=lambda x: issue_options[x])
            
            if selected_issue_idx is not None:
                selected_issue = issues[selected_issue_idx]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Issue Details:**")
                    st.write(f"- Category: {selected_issue.category}")
                    st.write(f"- Affected Users: {selected_issue.count}")
                    st.write(f"- Priority: {selected_issue.max_priority}")
                    
                    # Escalation controls
                    escalation_reason = st.text_area("Escalation Reason:", 
                                                   placeholder="Why does this need human intervention?")
                    
                    team_options = ["infrastructure_team", "identity_team", "billing_team", 
                                  "platform_team", "communication_team", "incident_response_team"]
                    assigned_team = st.selectbox("Assign to Team:", team_options)
                    
                    priority_level = st.selectbox("Priority Level:", ["urgent", "high", "normal"])
                
                with col2:
                    st.write("**Actions:**")
                    
                    if st.button("🚨 Escalate to Human", type="primary"):
                        if escalation_reason.strip():
                            success = self._manual_escalation(selected_issue, escalation_reason, 
                                                           assigned_team, priority_level)
                            if success:
                                st.success(f"✅ Issue escalated to {assigned_team}")
                                st.balloons()
                            else:
                                st.error("❌ Escalation failed")
                        else:
                            st.error("Please provide an escalation reason")
                    
                    if st.button("✅ Mark as Resolved"):
                        success = self._mark_resolved(selected_issue)
                        if success:
                            st.success("✅ Issue marked as resolved")
                        else:
                            st.error("❌ Failed to mark as resolved")
        
        # Human intervention history
        st.subheader("📋 Recent Human Interventions")
        try:
            client = datastore.Client()
            query = client.query(kind="human_interventions")
            query.order = ["-timestamp"]
            interventions = list(query.fetch(limit=5))
            
            if interventions:
                intervention_data = []
                for intervention in interventions:
                    intervention_data.append({
                        'Timestamp': datetime.fromtimestamp(intervention.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
                        'Issue Type': intervention.get('issue_type', 'Unknown'),
                        'Action': intervention.get('action', 'Unknown'),
                        'Operator': intervention.get('operator', 'Unknown'),
                        'Reason': intervention.get('reason', 'N/A')[:50] + "..." if len(intervention.get('reason', '')) > 50 else intervention.get('reason', 'N/A')
                    })
                
                df = pd.DataFrame(intervention_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No recent human interventions")
                
        except Exception as e:
            st.error(f"Error loading intervention history: {e}")
    
    def _manual_escalation(self, issue, reason, team, priority):
        """Handle manual escalation from dashboard."""
        try:
            client = datastore.Client()
            
            # Create escalation record
            key = client.key("human_interventions")
            entity = datastore.Entity(key=key)
            
            entity.update({
                "timestamp": datetime.utcnow().timestamp(),
                "issue_type": issue.category,
                "action": "manual_escalation",
                "operator": "dashboard_user",
                "reason": reason,
                "assigned_team": team,
                "priority": priority,
                "affected_users": issue.count
            })
            
            client.put(entity)
            
            # Create CRM ticket
            crm_ticket_id = f"MANUAL-{datetime.now().strftime('%Y%m%d')}-{hash(reason) % 10000:04d}"
            
            # Update response history with manual escalation
            resp_key = client.key("response_history")
            resp_entity = datastore.Entity(key=resp_key)
            
            resp_entity.update({
                "timestamp": datetime.utcnow().timestamp(),
                "issue_type": issue.category,
                "product_area": "manual_intervention",
                "escalated_to_human": True,
                "manual_escalation": True,
                "crm_ticket_id": crm_ticket_id,
                "escalation_details": {
                    "escalation_level": priority,
                    "recommended_team": team,
                    "reasons": [f"Manual escalation: {reason}"],
                    "estimated_response_time": "15 minutes" if priority == "urgent" else "30 minutes"
                },
                "metrics": {
                    "affected_customers": issue.count,
                    "manual_intervention": True
                },
                "channels": ["dashboard", "crm"]
            })
            
            client.put(resp_entity)
            return True
            
        except Exception as e:
            st.error(f"Error in manual escalation: {e}")
            return False
    
    def _mark_resolved(self, issue):
        """Mark issue as resolved manually."""
        try:
            client = datastore.Client()
            
            # Log resolution
            key = client.key("human_interventions")
            entity = datastore.Entity(key=key)
            
            entity.update({
                "timestamp": datetime.utcnow().timestamp(),
                "issue_type": issue.category,
                "action": "manual_resolution",
                "operator": "dashboard_user",
                "reason": f"Manually marked as resolved - {issue.count} users affected",
                "affected_users": issue.count
            })
            
            client.put(entity)
            return True
            
        except Exception as e:
            st.error(f"Error marking as resolved: {e}")
            return False
            
    def _render_knowledge_base(self):
        st.header("📚 Knowledge Base")
        
        kb_articles = self._get_kb_stats()
        
        if kb_articles:
            data = []
            for article in kb_articles:
                data.append({
                    'Title': article.get('title', 'Unknown'),
                    'Issue Type': article.get('issue_type', 'Unknown'),
                    'Success Rate': f"{article.get('success_rate', 0)}%",
                    'Last Updated': datetime.fromtimestamp(article.get('last_updated', 0)).strftime('%Y-%m-%d')
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Success rate chart
            success_data = pd.DataFrame({
                'Article': [a.get('title', f'Article {i}') for i, a in enumerate(kb_articles)],
                'Success Rate': [a.get('success_rate', 0) for a in kb_articles]
            })
            fig = px.bar(success_data, x='Article', y='Success Rate',
                        title="Knowledge Base Article Success Rates")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No knowledge base articles found")
            
    def _render_recent_resolutions(self):
        st.header("🔧 Recent Resolutions")
        
        try:
            client = datastore.Client()
            query = client.query(kind="response_history")
            query.order = ["-timestamp"]
            entities = list(query.fetch(limit=10))
            
            if entities:
                data = []
                for entity in entities:
                    # Check for escalation status
                    escalated = entity.get('escalated_to_human', False)
                    crm_ticket = entity.get('crm_ticket_id', 'N/A')
                    
                    data.append({
                        'Issue Type': entity.get('issue_type', 'Unknown'),
                        'Product Area': entity.get('product_area', 'Unknown'),
                        'Affected Users': entity.get('metrics', {}).get('affected_customers', 0),
                        'CRM Ticket': crm_ticket,
                        'Human Escalation': '🚨 Yes' if escalated else '✅ No',
                        'Resolved At': datetime.fromtimestamp(entity.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
                        'Channels': ', '.join(entity.get('channels', []))
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # Escalation metrics
                escalated_count = sum(1 for entity in entities if entity.get('escalated_to_human', False))
                total_count = len(entities)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Resolutions", total_count)
                with col2:
                    escalation_rate = (escalated_count / total_count * 100) if total_count > 0 else 0
                    st.metric("Human Escalation Rate", f"{escalation_rate:.1f}%")
                    
            else:
                st.info("No recent resolutions found")
        except Exception as e:
            st.error(f"Error loading resolutions: {e}")
    
    def _render_crm_integration(self):
        st.header("🎫 CRM Integration Status")
        
        try:
            client = datastore.Client()
            query = client.query(kind="response_history")
            entities = list(query.fetch(limit=20))
            
            if entities:
                # CRM ticket statistics
                crm_tickets = [e for e in entities if e.get('crm_ticket_id')]
                escalated_tickets = [e for e in entities if e.get('escalated_to_human', False)]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CRM Tickets Created", len(crm_tickets))
                with col2:
                    st.metric("Escalated to Humans", len(escalated_tickets))
                with col3:
                    automation_rate = ((len(entities) - len(escalated_tickets)) / len(entities) * 100) if entities else 0
                    st.metric("Automation Success Rate", f"{automation_rate:.1f}%")
                
                # Recent CRM activity
                if crm_tickets:
                    st.subheader("Recent CRM Tickets")
                    crm_data = []
                    for entity in crm_tickets[:5]:
                        escalation_details = entity.get('escalation_details', {})
                        crm_data.append({
                            'Ticket ID': entity.get('crm_ticket_id', 'N/A'),
                            'Issue Type': entity.get('issue_type', 'Unknown'),
                            'Priority': escalation_details.get('escalation_level', 'normal').upper(),
                            'Team': escalation_details.get('recommended_team', 'N/A'),
                            'Status': '🚨 Escalated' if entity.get('escalated_to_human') else '✅ Resolved',
                            'Created': datetime.fromtimestamp(entity.get('timestamp', 0)).strftime('%m-%d %H:%M')
                        })
                    
                    df = pd.DataFrame(crm_data)
                    st.dataframe(df, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error loading CRM data: {e}")

if __name__ == "__main__":
    dashboard = TrendingIssuesDashboard()
    dashboard.run()