"""Main agent implementation for the Trending Issue Resolution System."""

from typing import Any, Dict, List, Optional

from google.adk.agents import (
    Agent,
    AgentContext,
    LoopAgent,
    SequentialAgent,
    register_agent,
    register_tool,
)
from google.adk.managers import SessionState
from google.cloud import aiplatform, bigquery, datastore

from .prompt import ROOT_AGENT_PROMPT
from .sub_agents.context_fetcher.agent import ContextFetcherAgent
from .sub_agents.data_fetcher.agent import DataFetcherAgent
from .sub_agents.exit_condition.agent import ExitConditionAgent
from .sub_agents.knowledge_retrieval.agent import KnowledgeRetrievalAgent
from .sub_agents.notifier.agent import NotifierAgent
from .sub_agents.resolution_generator.agent import ResolutionGeneratorAgent
from .sub_agents.response_memory.agent import ResponseMemoryAgent
from .sub_agents.trend_summarizer.agent import TrendSummarizerAgent
from .tools.bigquery_tool import BigQueryTool
from .tools.datastore_tool import DatastoreTool


@register_agent
class SignalWatcherLoopAgent(LoopAgent):
    """Agent that continuously monitors for trending issues."""

    def __init__(self) -> None:
        super().__init__(
            name="signal_watcher",
            description="Monitors customer interaction logs for trending issues",
            sub_agents=[
                DataFetcherAgent(),
                ExitConditionAgent(),
            ],
        )

    async def should_continue(self, context: AgentContext) -> bool:
        """Check if monitoring should continue based on exit condition."""
        return not context.session.state.get("exit_signal", False)


@register_agent
class ResolverPipelineAgent(SequentialAgent):
    """Agent that handles the resolution generation pipeline."""

    def __init__(self) -> None:
        super().__init__(
            name="resolver_pipeline",
            description="Generates solutions for trending issues",
            sub_agents=[
                KnowledgeRetrievalAgent(),
                ResolutionGeneratorAgent(),
            ],
        )


@register_agent
class TrendingIssueResolverAgent(SequentialAgent):
    """Root agent that orchestrates the entire trending issue resolution system."""

    def __init__(self) -> None:
        super().__init__(
            name="trending_issue_resolver",
            description="GenAI-powered system for detecting and resolving trending customer issues",
            prompt=ROOT_AGENT_PROMPT,
            sub_agents=[
                SignalWatcherLoopAgent(),
                TrendSummarizerAgent(),
                ContextFetcherAgent(),
                ResolverPipelineAgent(),
                ResponseMemoryAgent(),
                NotifierAgent(),
            ],
        )
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Initialize and register tools used by the agent system."""
        # Initialize GCP clients
        bq_client = bigquery.Client()
        datastore_client = datastore.Client()
        
        # Register tools
        register_tool(BigQueryTool(bq_client))
        register_tool(DatastoreTool(datastore_client))

    async def initialize_session(self, context: AgentContext) -> None:
        """Initialize session state with required configuration."""
        context.session.state.update({
            "exit_signal": False,
            "trend_threshold": 10,  # Minimum incidents to consider a trend
            "time_window_minutes": 60,  # Time window for trend analysis
            "summary": None,
            "customer_context": None,
            "kb_hits": None,
            "final_resolution": None,
        })

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Execute the main agent workflow."""
        # Initialize session if needed
        if not context.session.state:
            await self.initialize_session(context)

        # Execute sequential workflow through sub-agents
        result = await super().process(context)

        # Return final state
        return {
            "summary": context.session.state.get("summary"),
            "resolution": context.session.state.get("final_resolution"),
            "notifications_sent": context.session.state.get("notifications_sent", []),
        }