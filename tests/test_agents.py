"""Tests for the Trending Issue Resolution System agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from adk import AgentContext
from adk.managers import SessionState

from trending_issue_resolver.agent import (
    TrendingIssueResolverAgent,
    SignalWatcherLoopAgent,
)
from trending_issue_resolver.sub_agents.data_fetcher.agent import DataFetcherAgent
from trending_issue_resolver.sub_agents.trend_summarizer.agent import TrendSummarizerAgent
from trending_issue_resolver.sub_agents.knowledge_retrieval.agent import KnowledgeRetrievalAgent
from trending_issue_resolver.sub_agents.resolution_generator.agent import ResolutionGeneratorAgent
from trending_issue_resolver.tools.bigquery_tool import BigQueryTool
from trending_issue_resolver.tools.firestore_tool import FirestoreTool


@pytest.fixture
def mock_bigquery():
    """Mock BigQuery client."""
    return MagicMock()


@pytest.fixture
def mock_firestore():
    """Mock Firestore client."""
    return MagicMock()


@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI client."""
    return MagicMock()


@pytest.fixture
def agent_context():
    """Create test agent context."""
    context = AgentContext()
    context.session = SessionState()
    return context


@pytest.mark.asyncio
async def test_data_fetcher_agent(agent_context, mock_bigquery):
    """Test DataFetcher agent functionality."""
    # Mock trending issues data
    mock_trending_issues = [
        {
            "issue_type": "login_error",
            "product_area": "authentication",
            "description": "Users unable to login",
            "severity": "high",
            "count": 15,
            "incidents": [
                {"customer_id": "123", "details": "Login timeout"},
                {"customer_id": "456", "details": "Invalid credentials"},
            ],
        }
    ]
    
    # Setup BigQuery tool with mock
    bq_tool = BigQueryTool(mock_bigquery)
    bq_tool.get_trending_issues = AsyncMock(return_value=mock_trending_issues)
    agent_context.register_tool(bq_tool)
    
    # Create and run agent
    agent = DataFetcherAgent()
    result = await agent.process(agent_context)
    
    # Verify results
    assert result["trending_issues"] == mock_trending_issues
    assert agent_context.session.state["trending_issues"] == mock_trending_issues


@pytest.mark.asyncio
async def test_trend_summarizer_agent(agent_context, mock_vertex_ai):
    """Test TrendSummarizer agent functionality."""
    # Setup test data
    agent_context.session.state["trending_issues"] = [
        {
            "issue_type": "login_error",
            "product_area": "authentication",
            "description": "Users unable to login",
            "severity": "high",
            "count": 15,
        }
    ]
    
    # Mock LLM response
    mock_vertex_ai.predict_text = AsyncMock(
        return_value=MagicMock(text="Summary of login issues affecting authentication system.")
    )
    
    with patch("google.cloud.aiplatform.gapic.VertexAIClient", return_value=mock_vertex_ai):
        # Create and run agent
        agent = TrendSummarizerAgent()
        result = await agent.process(agent_context)
        
        # Verify results
        assert result["summary"] is not None
        assert "text" in result["summary"]
        assert agent_context.session.state["summary"] == result["summary"]


@pytest.mark.asyncio
async def test_knowledge_retrieval_agent(agent_context, mock_firestore, mock_vertex_ai):
    """Test KnowledgeRetrieval agent functionality."""
    # Setup test data
    agent_context.session.state["summary"] = {
        "text": "Login system issues affecting multiple users",
        "primary_issue": {
            "type": "login_error",
            "product_area": "authentication",
        }
    }
    
    # Setup Firestore tool with mock
    firestore_tool = FirestoreTool(mock_firestore)
    firestore_tool.search_knowledge_base = AsyncMock(return_value=[
        {
            "id": "kb1",
            "title": "Common Login Issues",
            "content": "Troubleshooting steps for login problems",
            "last_updated": "2024-01-01",
        }
    ])
    agent_context.register_tool(firestore_tool)
    
    # Mock LLM responses
    mock_vertex_ai.predict_text = AsyncMock(
        return_value=MagicMock(text="Analysis of knowledge base articles")
    )
    
    with patch("google.cloud.aiplatform.gapic.VertexAIClient", return_value=mock_vertex_ai):
        # Create and run agent
        agent = KnowledgeRetrievalAgent()
        result = await agent.process(agent_context)
        
        # Verify results
        assert result["kb_hits"] is not None
        assert "articles" in result["kb_hits"]
        assert "analysis" in result["kb_hits"]
        assert agent_context.session.state["kb_hits"] == result["kb_hits"]


@pytest.mark.asyncio
async def test_resolution_generator_agent(agent_context, mock_vertex_ai, mock_firestore):
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
            "articles": [{"id": "kb1"}],
            "analysis": "Relevant knowledge base findings",
        }
    })
    
    # Setup Firestore tool with mock
    firestore_tool = FirestoreTool(mock_firestore)
    firestore_tool.save_response = AsyncMock(return_value="res1")
    agent_context.register_tool(firestore_tool)
    
    # Mock LLM response
    mock_vertex_ai.predict_text = AsyncMock(
        return_value=MagicMock(text="Root cause\n\nSteps\n\nVerification\n\nPrevention\n\nTemplate")
    )
    
    with patch("google.cloud.aiplatform.gapic.VertexAIClient", return_value=mock_vertex_ai):
        # Create and run agent
        agent = ResolutionGeneratorAgent()
        result = await agent.process(agent_context)
        
        # Verify results
        assert result["final_resolution"] is not None
        assert "root_cause" in result["final_resolution"]
        assert "steps" in result["final_resolution"]
        assert agent_context.session.state["final_resolution"] == result["final_resolution"]


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