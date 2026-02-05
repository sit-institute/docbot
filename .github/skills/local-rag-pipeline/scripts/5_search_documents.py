#!/usr/bin/env python3
"""
Step 5: Search documents with two-stage retrieval.

Vector search followed by cross-encoder reranking with optional query expansion.
Output: Ranked results with metadata.

Usage:
    python 5_search_documents.py <chroma_db_path> "<query>" --collection <n> [--top-k K] [--rerank-candidates N] [--expand-queries]

Example:
    python 5_search_documents.py ./chroma_db/ "What are the payment terms?" --collection legal_docs --top-k 5
    python 5_search_documents.py ./chroma_db/ "Zahlungsbedingungen" --collection vw_reports --expand-queries
"""

import sys
import json
import argparse
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch

QueryExpander = None
EXPANDER_AVAILABLE = False

try:
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from query_expander import QueryExpander as QE

    QueryExpander = QE
    EXPANDER_AVAILABLE = True
except (ImportError, Exception):
    pass


def _deduplicate_results(documents, metadatas):
    seen = set()
    unique_docs = []
    unique_metas = []
    for doc, meta in zip(documents, metadatas):
        doc_hash = hash(doc[:200])
        if doc_hash not in seen:
            seen.add(doc_hash)
            unique_docs.append(doc)
            unique_metas.append(meta)
    return {"documents": unique_docs, "metadatas": unique_metas}


def search_documents(
    chroma_db_path: str,
    query: str,
    collection_name: str,
    top_k: int = 5,
    rerank_candidates: int = 20,
    reranker_model: str = "BAAI/bge-reranker-v2-m3",
    filter_filename: str = None,
    expand_queries: bool = True,
    num_expansions: int = 5,
):
    """
    Search documents with two-stage retrieval and optional query expansion.

    Args:
        chroma_db_path: Path to ChromaDB database
        query: Search query
        collection_name: Name of collection to search
        top_k: Number of final results to return
        rerank_candidates: Number of candidates for reranking
        reranker_model: Cross-encoder model for reranking
        expand_queries: Enable query expansion (default: True)
        num_expansions: Number of expanded queries (default: 5)
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print(f"Loading ChromaDB from: {chroma_db_path}")
    client = chromadb.PersistentClient(
        path=chroma_db_path, settings=Settings(anonymized_telemetry=False)
    )

    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error: Collection '{collection_name}' not found")
        print(f"Available collections: {[c.name for c in client.list_collections()]}")
        sys.exit(1)

    coll_metadata = collection.metadata
    embedding_model_name = coll_metadata.get("embedding_model", "BAAI/bge-base-en-v1.5")
    print(f"Collection: {collection_name}")
    print(f"Embedding model: {embedding_model_name}")
    print(f"Total chunks: {collection.count()}")

    print(f"\n[Stage 1] Loading embedding model...")
    embedder = SentenceTransformer(
        embedding_model_name, device=device, local_files_only=True
    )

    queries_to_search = [query]
    if expand_queries and EXPANDER_AVAILABLE:
        print(f"[Query Expansion] Expanding query...")
        expander = QueryExpander(num_expansions=num_expansions)
        expanded = expander.expand(query)
        queries_to_search = expanded
        print(f"[Query Expansion] Original: '{query}'")
        print(f"[Query Expansion] Expanded ({len(queries_to_search)} queries):")
        for i, q in enumerate(queries_to_search, 1):
            print(f"  {i}. {q}")
    elif expand_queries and not EXPANDER_AVAILABLE:
        print("[Query Expansion] Module not available, using original query only")

    print(f"\n[Stage 1] Vector search...")
    all_candidates = []
    all_metadatas = []

    for q in queries_to_search:
        q_embedding = embedder.encode(
            [q], convert_to_tensor=True, normalize_embeddings=True
        )

        query_params = {
            "query_embeddings": q_embedding.cpu().numpy().tolist(),
            "n_results": min(rerank_candidates, collection.count()),
        }

        if filter_filename:
            query_params["where"] = {"filename": {"$eq": filter_filename}}

        results = collection.query(**query_params)
        if results["documents"][0]:
            all_candidates.extend(results["documents"][0])
            all_metadatas.extend(results["metadatas"][0])

    if not all_candidates:
        print("No results found")
        return

    deduped = _deduplicate_results(all_candidates, all_metadatas)
    candidates = deduped["documents"]
    candidate_metadatas = deduped["metadatas"]
    print(f"Retrieved {len(candidates)} unique candidates")

    print(f"\n[Stage 2] Reranking with {reranker_model}...")
    reranker = CrossEncoder(
        reranker_model, device=device, max_length=512, local_files_only=True
    )

    pairs = [[query, doc] for doc in candidates]
    rerank_scores = reranker.predict(pairs, batch_size=16, show_progress_bar=False)

    reranked_results = sorted(
        zip(candidates, candidate_metadatas, rerank_scores),
        key=lambda x: x[2],
        reverse=True,
    )[:top_k]

    print(f"\n{'=' * 80}")
    print(f"Query: {query}")
    print(f"{'=' * 80}\n")

    for rank, (doc, meta, score) in enumerate(reranked_results, 1):
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
    parser.add_argument(
        "--collection", required=True, help="Name of collection to search"
    )
    parser.add_argument(
        "--top-k", type=int, default=5, help="Number of final results (default: 5)"
    )
    parser.add_argument(
        "--rerank-candidates",
        type=int,
        default=20,
        help="Number of candidates for reranking (default: 20)",
    )
    parser.add_argument(
        "--reranker",
        default="BAAI/bge-reranker-v2-m3",
        help="Reranker model (default: BAAI/bge-reranker-v2-m3)",
    )
    parser.add_argument(
        "--filter-filename",
        help="Filter results by source filename",
    )
    parser.add_argument(
        "--expand-queries",
        action="store_true",
        default=True,
        help="Enable query expansion (default: enabled, use --no-expand-queries to disable)",
    )
    parser.add_argument(
        "--no-expand-queries",
        dest="expand_queries",
        action="store_false",
        help="Disable query expansion",
    )
    parser.add_argument(
        "--num-expansions",
        type=int,
        default=5,
        help="Number of expanded queries (default: 5)",
    )

    args = parser.parse_args()

    search_documents(
        args.chroma_db_path,
        args.query,
        args.collection,
        args.top_k,
        args.rerank_candidates,
        args.reranker,
        args.filter_filename,
        args.expand_queries,
        args.num_expansions,
    )


if __name__ == "__main__":
    main()
