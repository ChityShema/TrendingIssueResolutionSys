"""KnowledgeRetrieval agent for finding relevant solutions."""

from typing import Any, Dict, List, Optional

from google.adk.agents import Agent, AgentContext, register_agent
from google.adk.managers import SessionState
from google.cloud import aiplatform

from ...prompt import KNOWLEDGE_RETRIEVAL_PROMPT


@register_agent
class KnowledgeRetrievalAgent(Agent):
    """Agent that searches knowledge base for relevant solutions."""

    def __init__(self) -> None:
        super().__init__(
            name="knowledge_retrieval",
            description="Searches knowledge base for relevant issue solutions",
            prompt=KNOWLEDGE_RETRIEVAL_PROMPT,
        )

    def _extract_keywords(self, text: str, vertex_ai: Any) -> List[str]:
        """Extract relevant keywords from text using LLM.
        
        Args:
            text: Text to analyze
            vertex_ai: Vertex AI client
            
        Returns:
            List of extracted keywords
        """
        prompt = f"""
        Extract key technical terms and concepts from the following text as a comma-separated list.
        Focus on product names, feature names, error messages, and technical terms.
        
        Text: {text}
        
        Keywords:"""
        
        response = vertex_ai.predict_text(
            model_name="gemini-pro",
            prompt=prompt,
            temperature=0.1,
            max_output_tokens=256,
        )
        
        # Split response into keywords and clean
        keywords = [
            k.strip().lower()
            for k in response.text.split(",")
            if k.strip()
        ]
        
        return keywords

    async def process(self, context: AgentContext) -> Dict[str, Any]:
        """Search knowledge base for relevant solutions.
        
        Args:
            context: Agent context with session state
            
        Returns:
            Dictionary containing relevant knowledge base articles
        """
        summary = context.session.state.get("summary")
        if not summary:
            return {"kb_hits": None}
        
        # Get Datastore tool
        datastore_tool = context.get_tool("datastore_tool")
        if not datastore_tool:
            raise RuntimeError("Datastore tool not found")
        
        # Get Vertex AI client for keyword extraction
        vertex_ai = aiplatform.gapic.VertexAIClient()
        
        # Extract keywords from summary and description
        issue_text = f"{summary['text']}\n{summary['primary_issue']['type']}"
        keywords = await self._extract_keywords(issue_text, vertex_ai)
        
        # Search knowledge base
        kb_articles = await datastore_tool.search_knowledge_base(
            issue_type=summary["primary_issue"]["type"],
            product_area=summary["primary_issue"]["product_area"],
            keywords=keywords,
        )
        
        if not kb_articles:
            return {"kb_hits": None}
        
        # Format articles for LLM consumption
        articles_text = []
        for idx, article in enumerate(kb_articles, 1):
            articles_text.extend([
                f"\nArticle {idx}:",
                f"Title: {article['title']}",
                f"Last Updated: {article['last_updated']}",
                f"Content: {article['content']}",
                f"Success Rate: {article.get('success_rate', 'N/A')}%",
            ])
        
        # Generate synthesis prompt
        prompt = f"""{self.prompt}

Issue Summary:
{summary['text']}

Relevant Knowledge Base Articles:
{'\n'.join(articles_text)}

Please analyze these articles and provide:
1. Most relevant solutions
2. Success rates and applicability
3. Any gaps or additional considerations
"""
        
        # Generate analysis using LLM
        response = await vertex_ai.predict_text(
            model_name="gemini-pro",
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=1024,
        )
        
        kb_hits = {
            "articles": kb_articles,
            "analysis": response.text,
            "keywords_used": keywords,
        }
        
        # Update session state
        context.session.state["kb_hits"] = kb_hits
        
        return {"kb_hits": kb_hits}