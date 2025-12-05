# Helix Navigator

The Helix Navigator is a project focused on building AI systems using biomedical datasets, multi-step AI agents, and knowledge-graph-based reasoning. The goal is to build AI agents that answer complex questions about genes, proteins, diseases, and drugs using graph databases and multi-step AI workflows.

*Navigate: [Getting Started](docs/getting-started.md) | [Foundations Guide](docs/foundations-and-background.md) | [Reference](docs/reference.md) | [Technical Guide](docs/technical-guide.md)*


## Key Concepts in Helix Navigator

- **Knowledge Graphs**: Represent domain knowledge as nodes and relationships
- **LangGraph**: Build multi-step AI workflows with state management  
- **Cypher Queries**: Query graph databases effectively
- **AI Integration**: Combine language models with structured knowledge
- **Biomedical Applications**: Apply AI to drug discovery and personalized medicine

## Quick Start

1. **Start with the basics:** Review the [Foundations Guide](docs/foundations-and-background.md) if you're new to knowledge graphs or LangGraph.  
2. **Set up your environment:** Follow the installation steps in [Getting Started](docs/getting-started.md).  
3. **Explore the tools:** Open the Streamlit interface to interact with the system directly.  
4. **Apply what you learn:** Complete the exercises and guided tasks available in the web application.

---

## Technology Stack

- **LangGraph** — Framework for building structured, multi-step AI workflows  
- **Neo4j** — Graph database powering all knowledge retrieval  
- **Anthropic Claude** — Language model used for reasoning and natural language responses  
- **Streamlit** — Interactive front-end interface  
- **LangGraph Studio** — Visual debugging tool for understanding agent execution  


## Installation

**Quick Setup**: Python 3.10+, Neo4j, PDM

NOTE: this is a simple brief overview of the commands and steps. For full detailed instructions on how to install dependencies and setup the environment at [Getting Started](docs/getting-started.md).

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
- `src/agents/query_explainer.py`(new) — Explains Cypher queries and breaks down their components  
- `src/agents/query_learning_system.py`(new) — Interactive system for practicing and improving Cypher query construction  
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

- **"Which approved drugs target specific proteins?"**
- **"Which drugs have high efficacy for treating diseases?"**
- **"Which approved drugs treat cardiovascular diseases?"**
- **"Which genes encode proteins that are biomarkers for diseases?"**
- **"Which genes are linked to multiple disease categories?"**
- **"What proteins have causal associations with diseases?"**
- **"What drugs target proteins with high confidence disease associations?"**


## Helix Navigator Project Additional Improvements Overview

There are two main improvements I've added in the files mentioned above (query_explainer.py, query_learning_system.py). 

The first is a query learning system for the agent that scores user queries and suggests new ones based on previous activity. When working on the query learning system, I wanted to create a system that can store successful queries and user feedback to build a "query library" that improves over time with user actions, input and feedback. I found this part interesting because I wanted this query learning system to give new query recommendations based on the user's activity and previous questions. This required me to learn more about how to train the model to identify queries similar to one another to recommend them. Working on this part of the task was very interesting and I was able to find training methods to teach the model to recommend accurate results. These include having a persistent storage for queries, results and feedback, in addition to user analytics to track queries that are effective and working well.

THe second a cypher query explainer that would improve the user experience when using the application. Cypher queries is the language that is used to query information from the Neo4j graph database. As many people are not extremely familar with cypher queries and they're not intuitive at first glace, I wanted to add a feature that breaks down and explains Cypher queries in plain, common English. This speeds up the learning process for individuals who want to understand the type of query that the agent is generating and running against the databse from their prompt.


### 1. Query Explainer

This feature provides clear, high-level explanations of Cypher queries to help users understand graph database operations more intuitively.

#### What It Does
- Summarizes what a query is doing in plain language  
- Breaks queries into major components (MATCH, WHERE, RETURN, etc.)  
- Highlights potential issues or inefficiencies  
- Provides simple text-based diagrams of graph patterns  
- Estimates query complexity and expected result size

#### Why It Exists
`query_explainer.py` supports learning, debugging, and teaching Cypher by turning complex queries into readable, structured explanations.

#### Example Capabilities
- Identify nodes, relationships, filters, and return items  
- Flag missing `LIMIT` or overly broad patterns  
- Produce short natural-language descriptions of query logic  

This file allows educational features in the app and improves transparency around how graph queries work.

### 2. Query Learning System

This feature tracks query usage and feedback to help the system generate better Cypher queries over time.

#### What It Does
- Logs every query execution (success, errors, results)
- Stores user ratings and feedback
- Learns recurring successful query patterns
- Suggests similar past queries to users
- Provides confidence scores for new queries
- Generates basic analytics on performance and improvement

#### Why It's Useful
It gives the system a simple “memory,” allowing queries to improve based on what has worked well for users in the past.

#### Core Features
- Query history database  
- Pattern extraction and scoring  
- User feedback integration  
- Similar-query recommendations  
- Lightweight analytics (success rate, ratings, trends)

## Modifications Made

My version of the Helix Navigator introduces two additional modules to support interactive learning and query understanding. Both of these files were completely created by me and were not present in the original version:

### ✔ `src/agents/query_explainer.py`
A helper module that explains the structure and meaning of Cypher queries. It breaks down clauses, describes data flow, and makes graph queries more interpretable.

### ✔ `src/agents/query_learning_system.py`
An interactive query-building and feedback system designed to teach users how to construct, debug, and refine Cypher queries.

These files integrate with the existing agent workflow and expand the educational scope of the project.


