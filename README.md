# Trending Issue Resolution System

A GenAI-powered Multi-Agent System (MAS) that detects and resolves trending customer issues using ADK on GCP. The system monitors user complaints, identifies patterns, generates consistent resolutions, and ensures unified communication across all channels.

## 🎯 Key Features

- **Real-time Issue Detection**: Monitors and analyzes customer interactions to identify trending issues
- **Smart Summarization**: Uses LLMs to summarize and categorize issue patterns
- **Context-Aware Resolution**: Leverages historical data and knowledge bases for accurate solutions
- **Cross-Channel Consistency**: Maintains unified messaging across UI, email, and CRM platforms
- **Human-in-the-Loop Integration**: Optional escalation paths for complex cases

## 🏗️ Architecture

The system uses a hierarchical Multi-Agent System architecture with the following components:

```
RootAgent (SequentialAgent)
│
├── SignalWatcherLoopAgent (LoopAgent)
│   ├── DataFetcherAgent (Custom Agent)
│   └── ExitConditionAgent (Custom Agent – escalates if spike detected)
│
├── TrendSummarizerAgent (LLM Agent with output_key='summary')
│
├── ContextFetcherAgent (Custom Agent – fetches CRM/ticket info)
│
├── ResolverPipelineAgent (SequentialAgent)
│   ├── KnowledgeRetrievalAgent (LLM Agent + KB Tool)
│   └── ResolutionGeneratorAgent (LLM Agent)
│
├── ResponseMemoryAgent (Custom Agent – saves consistent responses)
│
└── NotifierAgent (SequentialAgent)
    ├── UIUpdaterAgent (Custom Agent)
    ├── EmailDispatcherAgent (LLM Agent)
    └── CRMCommentAgent (Custom Agent)
```

## 🚀 Getting Started

### Prerequisites

1. Python 3.9+
2. Poetry for dependency management
3. Google Cloud Project with:
   - Vertex AI API enabled
   - BigQuery enabled
   - Firestore enabled
   - Cloud Functions/Cloud Run access
   - Firebase project (for UI dashboard)

### Environment Setup

1. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

2. Required environment variables:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   VERTEX_LOCATION=us-central1
   FIRESTORE_COLLECTION=issue-resolutions
   BIGQUERY_DATASET=customer_interactions
   SENDGRID_API_KEY=your-sendgrid-key
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

### Running the Agent

1. Start the agent locally:
   ```bash
   poetry run adk run .
   ```

2. For web interface:
   ```bash
   poetry run adk web
   ```

## 📊 Data Flow

1. `SignalWatcherLoopAgent` continuously monitors customer interaction logs in BigQuery
2. When a trend is detected, `TrendSummarizerAgent` creates a summary
3. `ContextFetcherAgent` gathers relevant historical data
4. `ResolverPipelineAgent` generates solutions using knowledge base and LLMs
5. `ResponseMemoryAgent` stores resolutions for consistency
6. `NotifierAgent` distributes responses across channels

## 🔧 Configuration

Key configuration options in `config.py`:
- Trend detection thresholds
- LLM model parameters
- Knowledge base settings
- Notification preferences

## 🧪 Testing

Run the test suite:
```bash
poetry run pytest
```

## 📦 Deployment

Deploy to GCP:
```bash
poetry run python deployment/deploy.py
```

## 📝 License

This project is licensed under the Apache 2.0 License.