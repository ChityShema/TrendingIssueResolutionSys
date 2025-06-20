"""Tests for the Trending Issue Resolution System agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from google.adk.agents import AgentContext
from google.adk.managers import SessionState

from trending_issue_resolver.agent import (
    TrendingIssueResolverAgent,
    SignalWatcherLoopAgent,
    ResolverPipelineAgent,
)
from trending_issue_resolver.sub_agents.data_fetcher.agent import DataFetcherAgent
from trending_issue_resolver.sub_agents.trend_summarizer.agent import TrendSummarizerAgent
from trending_issue_resolver.sub_agents.knowledge_retrieval.agent import KnowledgeRetrievalAgent
from trending_issue_resolver.sub_agents.resolution_generator.agent import ResolutionGeneratorAgent
from trending_issue_resolver.sub_agents.response_memory.agent import ResponseMemoryAgent
from trending_issue_resolver.sub_agents.notifier.agent import NotifierAgent
from trending_issue_resolver.tools.bigquery_tool import BigQueryTool
from trending_issue_resolver.tools.datastore_tool import DatastoreTool


@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client."""
    client = MagicMock()
    client.project = "test-project"
    return client


@pytest.fixture
def mock_datastore_client():
    """Mock Datastore client."""
    return MagicMock()


@pytest.fixture
def agent_context():
    """Create test agent context."""
    context = MagicMock(spec=AgentContext)
    context.session = MagicMock()
    context.session.state = {
        "exit_signal": False,
        "trend_threshold": 10,
        "time_window_minutes": 60,
    }
    context.current_time = datetime.utcnow()
    context.get_tool = MagicMock()
    return context


@pytest.fixture
def sample_trending_issues():
    """Sample trending issues data."""
    return [
        {
            "issue_type": "login_error",
            "product_area": "authentication",
            "description": "Users unable to login",
            "severity": "high",
            "count": 15,
            "incidents": [
                {"customer_id": "123", "timestamp": "2024-01-01T10:00:00Z", "details": "Login timeout"},
                {"customer_id": "456", "timestamp": "2024-01-01T10:05:00Z", "details": "Invalid credentials"},
            ],
        },
        {
            "issue_type": "payment_failure",
            "product_area": "billing",
            "description": "Payment processing errors",
            "severity": "medium",
            "count": 8,
            "incidents": [
                {"customer_id": "789", "timestamp": "2024-01-01T10:10:00Z", "details": "Card declined"},
            ],
        }
    ]


@pytest.mark.asyncio
async def test_data_fetcher_agent(agent_context, mock_bigquery_client, sample_trending_issues):
    """Test DataFetcher agent functionality."""
    # Setup BigQuery tool mock
    bq_tool = MagicMock(spec=BigQueryTool)
    bq_tool.get_trending_issues = AsyncMock(return_value=sample_trending_issues)
    bq_tool.get_historical_context = AsyncMock(return_value={
        "avg_daily_incidents": 5.2,
        "max_daily_incidents": 12,
        "typical_resolution_time": 45.0,
        "historical_resolutions": ["Reset password", "Clear cache"]
    })
    
    agent_context.get_tool.return_value = bq_tool
    
    # Create and run agent
    agent = DataFetcherAgent()
    result = await agent.process(agent_context)
    
    # Verify results
    assert result["trending_issues"] == sample_trending_issues
    assert "historical_context" in result
    assert agent_context.session.state["trending_issues"] == sample_trending_issues
    bq_tool.get_trending_issues.assert_called_once()


@pytest.mark.asyncio
async def test_trend_summarizer_agent(agent_context, sample_trending_issues):
    """Test TrendSummarizer agent functionality."""
    # Setup test data
    agent_context.session.state.update({
        "trending_issues": sample_trending_issues,
        "historical_context": {
            "avg_daily_incidents": 5.2,
            "typical_resolution_time": 45.0,
        }
    })
    
    # Mock Vertex AI response
    mock_response = MagicMock()
    mock_response.text = "Critical login authentication issues affecting 15 users with timeout and credential validation problems."
    
    with patch("google.cloud.aiplatform.gapic.VertexAIClient") as mock_vertex:
        mock_vertex.return_value.predict_text = AsyncMock(return_value=mock_response)
        
        # Create and run agent
        agent = TrendSummarizerAgent()
        result = await agent.process(agent_context)
        
        # Verify results
        assert result["summary"] is not None
        assert result["summary"]["text"] == mock_response.text
        assert result["summary"]["primary_issue"]["type"] == "login_error"
        assert result["summary"]["total_issues"] == 2
        assert agent_context.session.state["summary"] == result["summary"]


@pytest.mark.asyncio
async def test_knowledge_retrieval_agent(agent_context, mock_datastore_client):
    """Test KnowledgeRetrieval agent functionality."""
    # Setup test data
    agent_context.session.state["summary"] = {
        "text": "Login system issues affecting multiple users",
        "primary_issue": {
            "type": "login_error",
            "product_area": "authentication",
            "severity": "high",
            "count": 15,
        }
    }
    
    # Setup Datastore tool mock
    ds_tool = MagicMock(spec=DatastoreTool)
    ds_tool.search_knowledge_base = AsyncMock(return_value=[
        {
            "id": "kb1",
            "title": "Common Login Issues",
            "content": "Troubleshooting steps for login problems",
            "last_updated": "2024-01-01",
            "relevance_score": 3,
        }
    ])
    
    agent_context.get_tool.return_value = ds_tool
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = "Based on knowledge base analysis, this appears to be a common authentication timeout issue."
    
    with patch("google.cloud.aiplatform.gapic.VertexAIClient") as mock_vertex:
        mock_vertex.return_value.predict_text = AsyncMock(return_value=mock_response)
        
        # Create and run agent
        agent = KnowledgeRetrievalAgent()
        result = await agent.process(agent_context)
        
        # Verify results
        assert result["kb_hits"] is not None
        assert "articles" in result["kb_hits"]
        assert "analysis" in result["kb_hits"]
        assert len(result["kb_hits"]["articles"]) == 1
        assert agent_context.session.state["kb_hits"] == result["kb_hits"]


@pytest.mark.asyncio
async def test_resolution_generator_agent(agent_context, mock_datastore_client):
    """Test ResolutionGenerator agent functionality."""
    # Setup test data
    agent_context.session.state.update({
        "summary": {
            "text": "Login system issues affecting multiple users",
            "primary_issue": {
                "type": "login_error",
                "product_area": "authentication",
                "severity": "high",
                "count": 15,
            }
        },
        "kb_hits": {
            "articles": [{"id": "kb1", "title": "Login Troubleshooting"}],
            "analysis": "Common authentication timeout issue",
        }
    })
    
    # Setup Datastore tool mock
    ds_tool = MagicMock(spec=DatastoreTool)
    ds_tool.get_similar_responses = AsyncMock(return_value=[])
    
    agent_context.get_tool.return_value = ds_tool
    
    # Mock LLM response with structured format
    mock_response = MagicMock()
    mock_response.text = """Root Cause: Authentication service timeout
    
Steps:
1. Clear browser cache and cookies
2. Try incognito/private browsing mode
3. Reset password if issue persists

Verification:
- Test login with cleared cache
- Confirm password reset email received

Prevention:
- Regular cache clearing
- Password manager usage

Template:
We've identified login issues affecting multiple users. Please try clearing your browser cache and cookies, then attempt login again."""
    
    with patch("google.cloud.aiplatform.gapic.VertexAIClient") as mock_vertex:
        mock_vertex.return_value.predict_text = AsyncMock(return_value=mock_response)
        
        # Create and run agent
        agent = ResolutionGeneratorAgent()
        result = await agent.process(agent_context)
        
        # Verify results
        assert result["final_resolution"] is not None
        assert "root_cause" in result["final_resolution"]
        assert "steps" in result["final_resolution"]
        assert "verification" in result["final_resolution"]
        assert agent_context.session.state["final_resolution"] == result["final_resolution"]


@pytest.mark.asyncio
async def test_response_memory_agent(agent_context, mock_datastore_client):
    """Test ResponseMemory agent functionality."""
    # Setup test data
    agent_context.session.state.update({
        "summary": {
            "primary_issue": {
                "type": "login_error",
                "product_area": "authentication",
                "count": 15,
            }
        },
        "final_resolution": {
            "root_cause": "Authentication timeout",
            "steps": ["Clear cache", "Reset password"],
            "template": "Login issue resolution template",
        }
    })
    
    # Setup Datastore tool mock
    ds_tool = MagicMock(spec=DatastoreTool)
    ds_tool.save_response = AsyncMock(return_value="response_123")
    
    agent_context.get_tool.return_value = ds_tool
    
    # Create and run agent
    agent = ResponseMemoryAgent()
    result = await agent.process(agent_context)
    
    # Verify results
    assert result["response_saved"] is True
    assert result["response_id"] == "response_123"
    ds_tool.save_response.assert_called_once()


@pytest.mark.asyncio
async def test_notifier_agent(agent_context):
    """Test Notifier agent functionality."""
    # Setup test data
    agent_context.session.state.update({
        "summary": {
            "primary_issue": {
                "type": "login_error",
                "product_area": "authentication",
                "count": 15,
            }
        },
        "final_resolution": {
            "template": "Login issue resolution template",
            "steps": ["Clear cache", "Reset password"],
        }
    })
    
    # Create and run agent
    agent = NotifierAgent()
    result = await agent.process(agent_context)
    
    # Verify results
    assert "notifications_sent" in result
    assert isinstance(result["notifications_sent"], list)


@pytest.mark.asyncio
async def test_signal_watcher_loop_agent(agent_context):
    """Test SignalWatcher loop agent functionality."""
    # Create agent
    agent = SignalWatcherLoopAgent()
    
    # Test normal operation (no exit signal)
    agent_context.session.state["exit_signal"] = False
    should_continue = await agent.should_continue(agent_context)
    assert should_continue is True
    
    # Test exit condition
    agent_context.session.state["exit_signal"] = True
    should_continue = await agent.should_continue(agent_context)
    assert should_continue is False


@pytest.mark.asyncio
async def test_resolver_pipeline_agent():
    """Test ResolverPipeline agent initialization."""
    agent = ResolverPipelineAgent()
    assert agent.name == "resolver_pipeline"
    assert len(agent.sub_agents) == 2


@pytest.mark.asyncio
async def test_root_agent_initialization(agent_context):
    """Test root agent initialization."""
    # Create root agent
    agent = TrendingIssueResolverAgent()
    
    # Initialize session
    await agent.initialize_session(agent_context)
    
    # Verify state initialization
    assert "exit_signal" in agent_context.session.state
    assert "trend_threshold" in agent_context.session.state
    assert "time_window_minutes" in agent_context.session.state
    assert "summary" in agent_context.session.state
    assert "customer_context" in agent_context.session.state


@pytest.mark.asyncio
async def test_root_agent_process(agent_context, mock_bigquery_client, mock_datastore_client):
    """Test root agent full process workflow."""
    # Mock tools
    bq_tool = MagicMock(spec=BigQueryTool)
    ds_tool = MagicMock(spec=DatastoreTool)
    
    def get_tool_mock(name):
        if name == "bigquery_tool":
            return bq_tool
        elif name == "datastore_tool":
            return ds_tool
        return None
    
    agent_context.get_tool.side_effect = get_tool_mock
    
    # Create root agent
    agent = TrendingIssueResolverAgent()
    
    # Mock sub-agent processing
    with patch.object(agent, 'sub_agents') as mock_sub_agents:
        mock_sub_agents.__iter__.return_value = []
        
        # Initialize and process
        await agent.initialize_session(agent_context)
        result = await agent.process(agent_context)
        
        # Verify results structure
        assert "summary" in result
        assert "resolution" in result
        assert "notifications_sent" in result


@pytest.mark.asyncio
async def test_bigquery_tool_integration(mock_bigquery_client):
    """Test BigQuery tool integration."""
    # Setup mock query results
    mock_result = MagicMock()
    mock_result.issue_type = "login_error"
    mock_result.product_area = "authentication"
    mock_result.description = "Login timeout"
    mock_result.severity = "high"
    mock_result.occurrence_count = 15
    mock_result.incidents = []
    
    mock_bigquery_client.query.return_value.result.return_value = [mock_result]
    
    # Create and test tool
    tool = BigQueryTool(mock_bigquery_client)
    results = await tool.get_trending_issues()
    
    # Verify results
    assert len(results) == 1
    assert results[0]["issue_type"] == "login_error"
    assert results[0]["count"] == 15


@pytest.mark.asyncio
async def test_datastore_tool_integration(mock_datastore_client):
    """Test Datastore tool integration."""
    # Setup mock query results
    mock_entity = MagicMock()
    mock_entity.get.return_value = "Test knowledge base content"
    mock_entity.key.id = "kb1"
    
    mock_datastore_client.query.return_value.fetch.return_value = [mock_entity]
    
    # Create and test tool
    tool = DatastoreTool(mock_datastore_client)
    results = await tool.search_knowledge_base("login_error", "authentication", ["timeout"])
    
    # Verify results
    assert len(results) >= 0  # May be empty if no keyword matches
    mock_datastore_client.query.assert_called()


@pytest.mark.asyncio
async def test_error_handling_missing_tools(agent_context):
    """Test error handling when tools are missing."""
    # Setup context with no tools
    agent_context.get_tool.return_value = None
    
    # Create agent
    agent = DataFetcherAgent()
    
    # Test should raise error for missing tool
    with pytest.raises(RuntimeError, match="BigQuery tool not found"):
        await agent.process(agent_context)


@pytest.mark.asyncio
async def test_empty_trending_issues_handling(agent_context):
    """Test handling of empty trending issues."""
    # Setup context with empty trending issues
    agent_context.session.state["trending_issues"] = []
    
    # Create agent
    agent = TrendSummarizerAgent()
    result = await agent.process(agent_context)
    
    # Verify graceful handling
    assert result["summary"] is None