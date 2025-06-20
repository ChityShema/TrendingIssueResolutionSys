"""Web dashboard for Trending Issue Resolver."""

import os
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from google.cloud import bigquery, datastore
import json

os.environ["GOOGLE_CLOUD_PROJECT"] = "hacker2025-team-98-dev"

app = Flask(__name__)

def get_trending_issues():
    """Get trending issues from BigQuery."""
    try:
        client = bigquery.Client()
        query = f"""
        SELECT 
            category,
            COUNT(*) as count,
            MAX(priority) as max_priority,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM `{client.project}.customer_interactions.issues`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
        AND status = 'open'
        GROUP BY category
        ORDER BY count DESC
        """
        
        results = list(client.query(query).result())
        issues = []
        
        for row in results:
            issues.append({
                'category': row.category,
                'count': row.count,
                'severity': 'High' if row.max_priority >= 3 else 'Medium',
                'first_seen': row.first_seen.strftime('%H:%M:%S'),
                'last_seen': row.last_seen.strftime('%H:%M:%S'),
                'status': 'Active' if row.count >= 5 else 'Monitoring'
            })
        
        return issues
    except Exception as e:
        print(f"Error getting trending issues: {e}")
        return []

def get_knowledge_base_stats():
    """Get knowledge base statistics."""
    try:
        client = datastore.Client()
        query = client.query(kind="knowledge_base")
        entities = list(query.fetch())
        
        stats = {
            'total_articles': len(entities),
            'by_category': {},
            'avg_success_rate': 0
        }
        
        if entities:
            for entity in entities:
                category = entity.get('issue_type', 'unknown')
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            success_rates = [e.get('success_rate', 0) for e in entities if e.get('success_rate')]
            stats['avg_success_rate'] = sum(success_rates) / len(success_rates) if success_rates else 0
        
        return stats
    except Exception as e:
        print(f"Error getting KB stats: {e}")
        return {'total_articles': 0, 'by_category': {}, 'avg_success_rate': 0}

def get_recent_resolutions():
    """Get recent resolutions from Datastore."""
    try:
        client = datastore.Client()
        query = client.query(kind="response_history")
        query.order = ["-timestamp"]
        entities = list(query.fetch(limit=10))
        
        resolutions = []
        for entity in entities:
            resolutions.append({
                'issue_type': entity.get('issue_type', 'Unknown'),
                'product_area': entity.get('product_area', 'Unknown'),
                'affected_customers': entity.get('metrics', {}).get('affected_customers', 0),
                'timestamp': datetime.fromtimestamp(entity.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'channels': ', '.join(entity.get('channels', []))
            })
        
        return resolutions
    except Exception as e:
        print(f"Error getting resolutions: {e}")
        return []

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/trending-issues')
def api_trending_issues():
    """API endpoint for trending issues."""
    return jsonify(get_trending_issues())

@app.route('/api/kb-stats')
def api_kb_stats():
    """API endpoint for knowledge base stats."""
    return jsonify(get_knowledge_base_stats())

@app.route('/api/recent-resolutions')
def api_recent_resolutions():
    """API endpoint for recent resolutions."""
    return jsonify(get_recent_resolutions())

@app.route('/api/system-status')
def api_system_status():
    """API endpoint for system status."""
    trending = get_trending_issues()
    kb_stats = get_knowledge_base_stats()
    
    status = {
        'status': 'Active' if trending else 'Monitoring',
        'active_issues': len([i for i in trending if i['status'] == 'Active']),
        'total_issues': sum(i['count'] for i in trending),
        'kb_articles': kb_stats['total_articles'],
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)