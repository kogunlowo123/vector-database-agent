# Vector Database Agent Architecture

Vector database operations agent that manages embedding storage, index optimization, collection lifecycle, similarity search tuning, and hybrid search configuration across vector database platforms.

## Domain Tools

- **create_collection**: Create a vector collection with specified index configuration
- **upsert_vectors**: Upsert embeddings with metadata into a collection
- **search_similar**: Search for similar vectors with filtering and reranking
- **optimize_index**: Optimize index parameters for query latency vs recall tradeoff
- **get_collection_stats**: Get collection statistics including size, index health, and query metrics