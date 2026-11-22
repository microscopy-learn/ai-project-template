# Retrieval-augmented generation

Retrieval-augmented generation, or RAG, retrieves relevant passages from a document collection and gives them to a language model as context, so answers are grounded in your own data.

Hybrid retrieval combines keyword search such as BM25 with vector search over embeddings. It usually finds more relevant passages than either method alone.

GraphRAG adds a knowledge graph to retrieval. The system follows relationships between entities to collect connected facts, which helps with questions that span several documents.

A RAG system should be evaluated in two parts. Retrieval metrics such as hit rate check whether the right passages were found, and answer metrics check whether the generated answer is correct and faithful to the passages.
