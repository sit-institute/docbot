#!/usr/bin/env python3
"""
Step 4: Index embeddings to ChromaDB.

Store embeddings and metadata in ChromaDB collections.
Output: ChromaDB persistent database.

Usage:
    python 4_index_to_chromadb.py <embeddings_dir> <chroma_db_path> --collection <name>

Example:
    python 4_index_to_chromadb.py ./embeddings/ ./chroma_db/ --collection legal_docs
"""

import sys
import os
import json
import numpy as np
import argparse
from pathlib import Path
import chromadb
from chromadb.config import Settings
from tqdm import tqdm


def index_to_chromadb(embeddings_dir: str, chroma_db_path: str, collection_name: str):
    """
    Index embeddings to ChromaDB collection.

    ⚠️ WARNING: Do not run multiple instances writing to the same collection!
    ChromaDB uses SQLite backend which only supports single-writer mode.
    For parallel indexing, use different collection names.

    Args:
        embeddings_dir: Directory containing embedding NPZ files
        chroma_db_path: Path to ChromaDB database
        collection_name: Name of ChromaDB collection
    """
    embeddings_path = Path(embeddings_dir)

    # Find all embedding NPZ files
    npz_files = list(embeddings_path.glob("*_embeddings.npz"))

    if not npz_files:
        print(f"No embedding NPZ files found in {embeddings_dir}")
        return

    print(f"Found {len(npz_files)} embedding files")

    # Initialize ChromaDB client
    print(f"Initializing ChromaDB at: {chroma_db_path}")
    client = chromadb.PersistentClient(
        path=chroma_db_path,
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )

    # Load first file to get embedding dimension
    first_data = np.load(npz_files[0], allow_pickle=True)
    embedding_dim = int(first_data["embedding_dim"])
    model_name = str(first_data["model_name"])

    print(f"Embedding model: {model_name}")
    print(f"Embedding dimension: {embedding_dim}")

    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={
            "description": f"Collection for {collection_name}",
            "embedding_model": model_name,
            "embedding_dim": embedding_dim,
        },
    )

    print(f"Using collection: {collection_name}")

    # Index all embeddings
    total_indexed = 0
    for npz_file in tqdm(npz_files, desc="Indexing to ChromaDB"):
        try:
            # Load embeddings and metadata
            data = np.load(npz_file, allow_pickle=True)
            embeddings = data["embeddings"]
            metadata_list = json.loads(str(data["metadata"]))
            texts = json.loads(str(data["texts"]))

            # Generate IDs
            doc_name = npz_file.stem.replace("_chunks_embeddings", "")
            ids = [f"{doc_name}_chunk_{i}" for i in range(len(embeddings))]

            # Prepare metadata for ChromaDB (convert lists to strings)
            chromadb_metadata = []
            for meta in metadata_list:
                chromadb_meta = {
                    "filename": meta.get("filename", ""),
                    "page_numbers": json.dumps(meta.get("page_numbers", [])),
                    "headings": json.dumps(meta.get("headings", [])),
                    "chunk_index": meta.get("chunk_index", 0),
                    "has_table": meta.get("has_table", False),
                }
                chromadb_metadata.append(chromadb_meta)

            # Add to collection (ChromaDB expects list of lists for embeddings)
            collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=chromadb_metadata,
            )

            total_indexed += len(embeddings)
            tqdm.write(f"  ✓ {npz_file.name}: {len(embeddings)} chunks indexed")

        except Exception as e:
            tqdm.write(f"  ✗ Error indexing {npz_file.name}: {e}")

    print(f"\nTotal chunks indexed: {total_indexed}")
    print(f"Collection: {collection_name}")
    print(f"Database location: {chroma_db_path}")
    print(
        f'Next step: python 5_search_documents.py {chroma_db_path} "your query" --collection {collection_name}'
    )


def main():
    parser = argparse.ArgumentParser(description="Index embeddings to ChromaDB")
    parser.add_argument(
        "embeddings_dir", help="Directory containing embedding NPZ files"
    )
    parser.add_argument("chroma_db_path", help="Path to ChromaDB database")
    parser.add_argument(
        "--collection", required=True, help="Name of ChromaDB collection"
    )

    args = parser.parse_args()

    if not os.path.exists(args.embeddings_dir):
        print(f"Error: Embeddings directory not found: {args.embeddings_dir}")
        sys.exit(1)

    index_to_chromadb(args.embeddings_dir, args.chroma_db_path, args.collection)


if __name__ == "__main__":
    main()
