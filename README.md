# Helix Navigator

**Learn LangGraph and Knowledge Graphs through Biomedical AI**

An interactive educational project that teaches modern AI development through hands-on biomedical applications. Build AI agents that answer complex questions about genes, proteins, diseases, and drugs using graph databases and multi-step AI workflows.

*Navigate: [Getting Started](docs/getting-started.md) | [Foundations Guide](docs/foundations-and-background.md) | [Reference](docs/reference.md) | [Technical Guide](docs/technical-guide.md)*


## What You'll Learn

- **Knowledge Graphs**: Represent domain knowledge as nodes and relationships
- **LangGraph**: Build multi-step AI workflows with state management  
- **Cypher Queries**: Query graph databases effectively
- **AI Integration**: Combine language models with structured knowledge
- **Biomedical Applications**: Apply AI to drug discovery and personalized medicine

## Quick Start

1. **New to these concepts?** Read the [Foundations Guide](docs/foundations-and-background.md)
2. **Setup**: Follow [Getting Started](docs/getting-started.md) for installation
3. **Learn**: Use the interactive Streamlit web interface
4. **Practice**: Work through the exercises in the web app

## Technology Stack

- **LangGraph**: AI workflow orchestration
- **Neo4j**: Graph database
- **Anthropic Claude**: Language model
- **Streamlit**: Interactive web interface
- **LangGraph Studio**: Visual debugging

## Installation

**Quick Setup**: Python 3.10+, Neo4j, PDM

```bash
# Install dependencies
pdm install

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Load data and start
pdm run load-data
pdm run app
```

## Project Structure

```
├── src/agents/              # AI agent implementations
├── src/web/app.py          # Interactive Streamlit interface
├── docs/                   # Documentation and tutorials
├── data/                   # Biomedical datasets
├── scripts/                # Data loading utilities
└── tests/                  # Test suite
```

**Key Files**:
- `src/agents/workflow_agent.py` - Main LangGraph agent
- `src/web/app.py` - Interactive Streamlit interface
- `docs/` - Complete documentation

## Running the Application

### Basic Usage
```bash
pdm run load-data         # Load biomedical data
pdm run app              # Start web interface
```

### Visual Debugging
```bash
pdm run langgraph    # Start LangGraph Studio
```

### Development
```bash
pdm run test            # Run tests (14 tests)
pdm run format          # Format code
pdm run lint            # Check quality
```

**Full commands**: See [Reference Guide](docs/reference.md)

## AI Agent

**WorkflowAgent** - LangGraph implementation with transparent processing for learning core LangGraph concepts through biomedical applications

## Example Questions

- **"Which drugs have high efficacy for treating diseases?"**
- **"Which approved drugs treat cardiovascular diseases?"**
- **"Which genes encode proteins that are biomarkers for diseases?"**
- **"What drugs target proteins with high confidence disease associations?"**
- **"Which approved drugs target specific proteins?"**
- **"Which genes are linked to multiple disease categories?"**
- **"What proteins have causal associations with diseases?"** 

## Helix Navigator Project Further Improvements

For this, there are two main improvements: A query learning system for the agent that scores user queries and suggests new ones based on previous activity, and a cypher query explainer that would improve the user experience when using the application. When working on the query learning system, I wanted to create a system that can store successful queries and user feedback to build a "query library" that improves over time with user actions, input and feedback. I found this part interesting because I wanted this query learning system to give new query recommendations based on the user's activity and previous questions. This required me to learn more about how to train the model to identify queries similar to one another to recommend them. Working on this part of the task was very interesting and I was able to find training methods to teach the model to recommend accurate results.

The Query Learning System with a feedback loop was chosen due to the many benefits and improvements it would bring to the project. These include having a persistent storage for queries, results and feedback, in addition to user analytics to track queries that are effective and working well. These are on top the main reason this tool was added to the project, which was to improve the user experience and quality of suggested queries.
