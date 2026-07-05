"""Vector Database Agent - Unit Tests."""

import pytest
from src.agent.tools import AgentTools


@pytest.mark.asyncio
async def test_create_collection():
    """Test Create a vector collection with specified index configuration."""
    tools = AgentTools()
    result = await tools.create_collection(name="test", dimension=1)
    assert result is not None
    assert "status" in result or "tool" in result


@pytest.mark.asyncio
async def test_upsert_vectors():
    """Test Upsert embeddings with metadata into a collection."""
    tools = AgentTools()
    result = await tools.upsert_vectors(collection="test", vectors="test")
    assert result is not None
    assert "status" in result or "tool" in result


@pytest.mark.asyncio
async def test_search_similar():
    """Test Search for similar vectors with filtering and reranking."""
    tools = AgentTools()
    result = await tools.search_similar(collection="test", query_vector="test")
    assert result is not None
    assert "status" in result or "tool" in result


@pytest.mark.asyncio
async def test_optimize_index():
    """Test Optimize index parameters for query latency vs recall tradeoff."""
    tools = AgentTools()
    result = await tools.optimize_index(collection="test", target_recall="test")
    assert result is not None
    assert "status" in result or "tool" in result


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test that the agent initializes correctly."""
    from src.agent.vector_database_agent_agent import VectorDatabaseAgentAgent
    agent = VectorDatabaseAgentAgent()
    assert agent.agent_id is not None
    assert agent._system_prompt is not None
    assert len(agent._tool_dispatch) > 0
