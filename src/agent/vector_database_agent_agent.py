"""Vector Database Agent - Main Agent Implementation."""

import uuid
import time
import asyncio
from typing import AsyncIterator, Any, Optional
from datetime import datetime, timezone

import structlog
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from src.config import get_settings
from src.models.schemas import ChatRequest, ChatResponse, StreamChunk
from src.rag.pipeline import RAGPipeline
from src.mcp.server import MCPServer
from src.a2a.handler import A2AHandler
from src.agent.tools import AgentTools
from src.agent.prompts import SYSTEM_PROMPT, RAG_CONTEXT_PROMPT, TOOL_SELECTION_PROMPT

logger = structlog.get_logger(__name__)
settings = get_settings()


class VectorDatabaseAgentAgent:
    """
    Vector database operations agent that manages embedding storage, index optimization, collection lifecycle, similarity search tuning, and hybrid search configuration across vector database platforms.

    Domain-specific capabilities:
    - Create a vector collection with specified index configuration
    - Upsert embeddings with metadata into a collection
    - Search for similar vectors with filtering and reranking
    - Optimize index parameters for query latency vs recall tradeoff
    - Get collection statistics including size, index health, and query metrics

    Infrastructure:
    - RAG-augmented knowledge retrieval with domain-specific embeddings
    - Tool invocation via MCP with domain-specific tool registry
    - Agent-to-agent communication via A2A protocol
    - Conversation memory with Redis
    - Audit logging and observability via OpenTelemetry
    """

    def __init__(self):
        self.agent_id = settings.a2a_agent_id
        self.rag_pipeline = RAGPipeline()
        self.mcp_server = MCPServer()
        self.a2a_handler = A2AHandler()
        self.tools = AgentTools()
        self._conversation_cache: dict[str, list[dict]] = {}
        self._system_prompt = SYSTEM_PROMPT
        self.index_management_enabled = True
        self.collection_lifecycle_enabled = True
        self.search_tuning_enabled = True
        self.hybrid_search_enabled = True
        self.embedding_management_enabled = True
        self._tool_dispatch = {
            "create_collection": self.tools.create_collection,
            "upsert_vectors": self.tools.upsert_vectors,
            "search_similar": self.tools.search_similar,
            "optimize_index": self.tools.optimize_index,
            "get_collection_stats": self.tools.get_collection_stats,
        }
        logger.info(
            "agent_initialized",
            agent_id=self.agent_id,
            model=settings.llm_model,
            tools=list(self._tool_dispatch.keys()),
            features=['index_management', 'collection_lifecycle', 'search_tuning', 'hybrid_search', 'embedding_management'],
        )

    async def process_message(self, request: ChatRequest, user_id: str) -> ChatResponse:
        """
        Process a user message with domain-specific tool selection and RAG context.

        Pipeline:
        1. Retrieve conversation history
        2. Run RAG retrieval for domain-relevant context
        3. Determine if tool execution is needed
        4. Execute domain-specific tools if applicable
        5. Build prompt with context, tool results, and history
        6. Generate response via LLM
        7. Store message and response
        8. Return formatted response with sources and tool outputs
        """
        start_time = time.time()
        conversation_id = request.conversation_id or uuid.uuid4()
        message_id = uuid.uuid4()

        logger.info(
            "processing_message",
            conversation_id=str(conversation_id),
            user_id=user_id,
            message_length=len(request.message),
        )

        # Step 1: Get conversation history
        history = await self._get_conversation_history(str(conversation_id))

        # Step 2: RAG retrieval with domain-specific filtering
        rag_results = await self.rag_pipeline.retrieve(
            query=request.message,
            top_k=5,
            filters={"user_id": user_id, "domain": "ai_engineering"},
        )
        context = self._format_context(rag_results)
        sources = [
            {
                "title": r.get("title", "Unknown"),
                "source": r.get("source", ""),
                "score": r.get("score", 0.0),
                "snippet": r.get("content", "")[:200],
            }
            for r in rag_results
        ]

        # Step 3: Tool selection and execution
        tool_results = await self._maybe_execute_tools(request.message, context)

        # Step 4: Build messages with domain context
        messages = [
            SystemMessage(content=self._system_prompt),
        ]
        if context:
            messages.append(SystemMessage(content=RAG_CONTEXT_PROMPT.format(context=context)))
        if tool_results:
            tool_context = "\n".join(
                f"Tool '{tr['tool']}' result: {tr['result']}"
                for tr in tool_results
            )
            messages.append(SystemMessage(content=f"Tool execution results:\n{tool_context}"))

        for msg in history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=request.message))

        # Step 5: Generate response
        response_text = await self._generate_response(messages)
        latency_ms = (time.time() - start_time) * 1000

        # Step 6: Store conversation
        await self._store_message(str(conversation_id), "user", request.message, user_id)
        await self._store_message(str(conversation_id), "assistant", response_text, user_id)

        logger.info(
            "message_processed",
            conversation_id=str(conversation_id),
            latency_ms=round(latency_ms, 2),
            sources_count=len(sources),
            tools_used=len(tool_results),
        )

        return ChatResponse(
            message=response_text,
            conversation_id=conversation_id,
            message_id=message_id,
            sources=sources,
            tool_results=tool_results,
            model=settings.llm_model,
            latency_ms=round(latency_ms, 2),
            timestamp=datetime.now(timezone.utc),
        )

    async def _maybe_execute_tools(self, message: str, context: str) -> list[dict]:
        """Determine if tools should be executed and run them."""
        # Simple keyword-based tool selection — in production, use LLM function calling
        results = []
        message_lower = message.lower()

        tool_keywords = {
            "create_collection": ['create', 'collection'],
            "upsert_vectors": ['upsert', 'vectors'],
            "search_similar": ['search', 'similar'],
            "optimize_index": ['optimize', 'index'],
            "get_collection_stats": ['get', 'collection', 'stats'],
        }

        for tool_name, keywords in tool_keywords.items():
            if any(kw in message_lower for kw in keywords):
                try:
                    tool_fn = self._tool_dispatch.get(tool_name)
                    if tool_fn:
                        result = await tool_fn(**self._extract_tool_params(tool_name, message))
                        results.append({"tool": tool_name, "result": result})
                except Exception as e:
                    logger.error("tool_execution_failed", tool=tool_name, error=str(e))
                    results.append({"tool": tool_name, "error": str(e)})

        return results

    def _extract_tool_params(self, tool_name: str, message: str) -> dict:
        """Extract tool parameters from the user message."""
        # Simplified extraction — production uses LLM-based parameter extraction
        return {"query": message}

    async def _generate_response(self, messages: list) -> str:
        """Generate LLM response from messages."""
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)
            response = await llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            return f"I apologize, I encountered an error generating a response: {str(e)}"

    async def _get_conversation_history(self, conversation_id: str) -> list[dict]:
        """Retrieve conversation history from cache or Redis."""
        if conversation_id in self._conversation_cache:
            return self._conversation_cache[conversation_id]
        return []

    async def _store_message(self, conversation_id: str, role: str, content: str, user_id: str):
        """Store a message in conversation history."""
        if conversation_id not in self._conversation_cache:
            self._conversation_cache[conversation_id] = []
        self._conversation_cache[conversation_id].append({
            "role": role,
            "content": content,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _format_context(self, results: list[dict]) -> str:
        """Format RAG results into context string."""
        if not results:
            return ""
        parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Unknown")
            content = r.get("content", "")[:500]
            source = r.get("source", "")
            parts.append(f"[{i}] {title} ({source})\n{content}")
        return "\n\n".join(parts)

    async def process_stream(self, request: ChatRequest, user_id: str) -> AsyncIterator[StreamChunk]:
        """Stream response chunks for real-time display."""
        response = await self.process_message(request, user_id)
        words = response.message.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield StreamChunk(
                chunk=chunk,
                conversation_id=response.conversation_id,
                done=i + 3 >= len(words),
            )
            await asyncio.sleep(0.05)
