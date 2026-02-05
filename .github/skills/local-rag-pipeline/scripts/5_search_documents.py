#!/usr/bin/env python3
"""
Step 5: Search documents with two-stage retrieval.

Vector search followed by cross-encoder reranking.
Output: Ranked results with metadata.

Usage:
    python 5_search_documents.py <chroma_db_path> "<query>" --collection <n> [--top-k K] [--rerank-candidates N]

Example:
    python 5_search_documents.py ./chroma_db/ "What are the payment terms?" --collection legal_docs --top-k 5
"""

import sys
import json
import argparse
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch


def search_documents(
    chroma_db_path: str,
    query: str,
    collection_name: str,
    top_k: int = 5,
    rerank_candidates: int = 20,
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
):
    """
    Search documents with two-stage retrieval.
    
    Args:
        chroma_db_path: Path to ChromaDB database
        query: Search query
        collection_name: Name of collection to search
        top_k: Number of final results to return
        rerank_candidates: Number of candidates for reranking
        reranker_model: Cross-encoder model for reranking
    """
    # Check GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Initialize ChromaDB
    print(f"Loading ChromaDB from: {chroma_db_path}")
    client = chromadb.PersistentClient(
        path=chroma_db_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get collection
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error: Collection '{collection_name}' not found")
        print(f"Available collections: {[c.name for c in client.list_collections()]}")
        sys.exit(1)
    
    # Get collection metadata to determine embedding model
    coll_metadata = collection.metadata
    embedding_model_name = coll_metadata.get("embedding_model", "BAAI/bge-base-en-v1.5")
    print(f"Collection: {collection_name}")
    print(f"Embedding model: {embedding_model_name}")
    print(f"Total chunks: {collection.count()}")
    
    # Load embedding model (same as used for indexing)
    print(f"\n[Stage 1] Loading embedding model...")
    embedder = SentenceTransformer(embedding_model_name, device=device)
    
    # Generate query embedding
    print(f"Generating query embedding...")
    query_embedding = embedder.encode(
        [query],
        convert_to_tensor=True,
        normalize_embeddings=True
    )
    
    # Stage 1: Vector search
    print(f"\n[Stage 1] Vector search (retrieving top-{rerank_candidates} candidates)...")
    results = collection.query(
        query_embeddings=query_embedding.cpu().numpy().tolist(),
        n_results=min(rerank_candidates, collection.count())
    )
    
    if not results['documents'][0]:
        print("No results found")
        return
    
    candidates = results['documents'][0]
    candidate_metadatas = results['metadatas'][0]
    print(f"Retrieved {len(candidates)} candidates")
    
    # Stage 2: Reranking
    print(f"\n[Stage 2] Reranking with {reranker_model}...")
    reranker = CrossEncoder(reranker_model, device=device, max_length=512)
    
    # Create query-document pairs
    pairs = [[query, doc] for doc in candidates]
    
    # Get reranking scores
    rerank_scores = reranker.predict(pairs, batch_size=16, show_progress_bar=False)
    
    # Sort by reranking score
    reranked_results = sorted(
        zip(candidates, candidate_metadatas, rerank_scores),
        key=lambda x: x[2],
        reverse=True
    )[:top_k]
    
    # Display results
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    for rank, (doc, meta, score) in enumerate(reranked_results, 1):
        # Parse metadata (ChromaDB stores lists as JSON strings)
        filename = meta.get("filename", "Unknown")
        page_numbers = json.loads(meta.get("page_numbers", "[]"))
        headings = json.loads(meta.get("headings", "[]"))
        has_table = meta.get("has_table", False)
        
        print(f"[Rank {rank}] Score: {score:.4f}")
        print(f"Source: {filename} (Pages: {page_numbers if page_numbers else 'N/A'})")
        if headings:
            print(f"Context: {' > '.join(headings)}")
        if has_table:
            print(f"Contains: Table")
        print(f"\nText:\n{doc[:500]}{'...' if len(doc) > 500 else ''}\n")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Search documents with two-stage retrieval"
    )
    parser.add_argument("chroma_db_path", help="Path to ChromaDB database")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--collection", required=True,
                       help="Name of collection to search")
    parser.add_argument("--top-k", type=int, default=5,
                       help="Number of final results (default: 5)")
    parser.add_argument("--rerank-candidates", type=int, default=20,
                       help="Number of candidates for reranking (default: 20)")
    parser.add_argument("--reranker", default="BAAI/bge-reranker-v2-m3",
                       help="Reranker model (default: BAAI/bge-reranker-v2-m3)")
    
    args = parser.parse_args()
    
    search_documents(
        args.chroma_db_path,
        args.query,
        args.collection,
        args.top_k,
        args.rerank_candidates,
        args.reranker
    )


if __name__ == "__main__":
    main()
