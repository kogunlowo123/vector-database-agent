# Vector Database Agent

[![CI](https://github.com/kogunlowo123/vector-database-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/kogunlowo123/vector-database-agent/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Category**: AI Engineering | **Cloud**: MULTI-CLOUD | **LLM**: gpt-4o

Vector database operations agent that manages embedding storage, index optimization, collection lifecycle, similarity search tuning, and hybrid search configuration across vector database platforms.

---

## Domain-Specific Tools

| Tool | Description |
|------|-------------|
| `create_collection` | Create a vector collection with specified index configuration |
| `upsert_vectors` | Upsert embeddings with metadata into a collection |
| `search_similar` | Search for similar vectors with filtering and reranking |
| `optimize_index` | Optimize index parameters for query latency vs recall tradeoff |
| `get_collection_stats` | Get collection statistics including size, index health, and query metrics |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/vectors/collections` | Create collection |
| `POST` | `/api/v1/vectors/upsert` | Upsert vectors |
| `POST` | `/api/v1/vectors/search` | Search similar vectors |
| `POST` | `/api/v1/vectors/optimize` | Optimize index |
| `GET` | `/api/v1/vectors/collections/{name}/stats` | Get collection stats |

## Features

- Index Management
- Collection Lifecycle
- Search Tuning
- Hybrid Search
- Embedding Management

## Integrations

- Pinecone
- Weaviate
- Qdrant
- Chromadb
- Milvus

## Architecture

```
vector-database-agent/
├── src/
│   ├── agent/              # Domain-specific agent logic
│   │   ├── vector_database_agent_agent.py  # Main agent with domain tools
│   │   ├── tools.py        # 5 domain-specific tools
│   │   └── prompts.py      # Expert system prompts
│   ├── api/                # FastAPI routes
│   │   └── routes/
│   │       ├── domain.py   # 5 domain-specific endpoints
│   │       └── health.py   # Health check
│   ├── connectors/         # 5 integration connectors
│   ├── config/             # Settings and configuration
│   ├── models/             # Domain-specific Pydantic schemas
│   ├── rag/                # RAG pipeline
│   ├── mcp/                # MCP server
│   └── a2a/                # Agent-to-agent protocol
├── tests/
├── infrastructure/         # Terraform, K8s, Helm, Docker
├── dashboard/              # Next.js frontend
└── docs/                   # Architecture and deployment docs
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run
make dev

# Test
make test

# Docker
docker compose up -d
```

## Primary Service

**Pinecone + Weaviate + Qdrant + ChromaDB + Milvus**

---

Built as part of the Enterprise AI Agent Platform.
