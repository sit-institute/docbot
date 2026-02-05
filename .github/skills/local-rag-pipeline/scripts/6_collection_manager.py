#!/usr/bin/env python3
"""
Step 6: Manage ChromaDB collections.

List, inspect, and delete collections.

Usage:
    python 6_collection_manager.py <chroma_db_path> --list
    python 6_collection_manager.py <chroma_db_path> --info <collection_name>
    python 6_collection_manager.py <chroma_db_path> --delete <collection_name>
    python 6_collection_manager.py <chroma_db_path> --delete-ids <id1> <id2> ... --collection <name>
    python 6_collection_manager.py <chroma_db_path> --delete-source <filename> --collection <name>

Examples:
    python 6_collection_manager.py ./chroma_db/ --list
    python 6_collection_manager.py ./chroma_db/ --info legal_docs
    python 6_collection_manager.py ./chroma_db/ --delete old_docs
    python 6_collection_manager.py ./chroma_db/ --delete-ids doc1 doc2 --collection vw_reports
    python 6_collection_manager.py ./chroma_db/ --delete-source report.pdf --collection vw_reports
"""

import sys
import json
import argparse
import chromadb
from chromadb.config import Settings


def list_collections(chroma_db_path: str):
    """List all collections in the database."""
    client = chromadb.PersistentClient(
        path=chroma_db_path, settings=Settings(anonymized_telemetry=False)
    )

    collections = client.list_collections()

    if not collections:
        print("No collections found in database")
        return

    print(f"\nCollections in {chroma_db_path}:")
    print("=" * 80)
    for coll in collections:
        print(f"\n📁 {coll.name}")
        print(f"   Chunks: {coll.count()}")
        if coll.metadata:
            for key, value in coll.metadata.items():
                print(f"   {key}: {value}")
    print("=" * 80)


def collection_info(chroma_db_path: str, collection_name: str):
    """Display detailed information about a collection."""
    client = chromadb.PersistentClient(
        path=chroma_db_path, settings=Settings(anonymized_telemetry=False)
    )

    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error: Collection '{collection_name}' not found")
        print(f"Available collections: {[c.name for c in client.list_collections()]}")
        sys.exit(1)

    print(f"\n{'=' * 80}")
    print(f"Collection: {collection_name}")
    print(f"{'=' * 80}")
    print(f"\nMetadata:")
    if collection.metadata:
        for key, value in collection.metadata.items():
            print(f"  {key}: {value}")

    print(f"\nStatistics:")
    print(f"  Total chunks: {collection.count()}")

    # Sample a few documents
    if collection.count() > 0:
        sample = collection.peek(limit=3)
        print(f"\nSample documents (first 3):")
        for i, (doc_id, doc, meta) in enumerate(
            zip(sample["ids"], sample["documents"], sample["metadatas"]), 1
        ):
            print(f"\n  [{i}] ID: {doc_id}")
            print(f"      File: {meta.get('filename', 'N/A')}")
            print(f"      Pages: {json.loads(meta.get('page_numbers', '[]'))}")
            print(f"      Text: {doc[:150]}...")

    print("\n" + "=" * 80)


def delete_documents_by_ids(chroma_db_path: str, collection_name: str, doc_ids: list):
    """Delete specific documents by their IDs."""
    client = chromadb.PersistentClient(
        path=chroma_db_path, settings=Settings(anonymized_telemetry=False)
    )

    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error: Collection '{collection_name}' not found")
        print(f"Available collections: {[c.name for c in client.list_collections()]}")
        sys.exit(1)

    existing_ids = collection.get(ids=doc_ids)["ids"]
    if not existing_ids:
        print(f"No matching documents found for provided IDs")
        return

    response = input(
        f"\n⚠️  Delete {len(existing_ids)} document(s) from collection '{collection_name}'? (yes/no): "
    )
    if response.lower() != "yes":
        print("Deletion cancelled")
        return

    collection.delete(ids=existing_ids)
    print(f"✓ {len(existing_ids)} document(s) deleted successfully")


def delete_documents_by_source(chroma_db_path: str, collection_name: str, source: str):
    """Delete all documents from a specific source file."""
    client = chromadb.PersistentClient(
        path=chroma_db_path, settings=Settings(anonymized_telemetry=False)
    )

    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error: Collection '{collection_name}' not found")
        print(f"Available collections: {[c.name for c in client.list_collections()]}")
        sys.exit(1)

    results = collection.get(where={"filename": source})
    doc_ids = results["ids"]

    if not doc_ids:
        print(f"No documents found for source: {source}")
        return

    response = input(
        f"\n⚠️  Delete {len(doc_ids)} document(s) from '{source}' in collection '{collection_name}'? (yes/no): "
    )
    if response.lower() != "yes":
        print("Deletion cancelled")
        return

    collection.delete(ids=doc_ids)
    print(f"✓ {len(doc_ids)} document(s) from '{source}' deleted successfully")


def delete_collection(chroma_db_path: str, collection_name: str):
    """Delete a collection from the database."""
    client = chromadb.PersistentClient(
        path=chroma_db_path, settings=Settings(anonymized_telemetry=False)
    )

    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()

        response = input(
            f"\n⚠️  Delete collection '{collection_name}' with {count} chunks? (yes/no): "
        )
        if response.lower() != "yes":
            print("Deletion cancelled")
            return

        client.delete_collection(name=collection_name)
        print(f"✓ Collection '{collection_name}' deleted successfully")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage ChromaDB collections")
    parser.add_argument("chroma_db_path", help="Path to ChromaDB database")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all collections")
    group.add_argument(
        "--info", metavar="COLLECTION", help="Show detailed info for a collection"
    )
    group.add_argument("--delete", metavar="COLLECTION", help="Delete a collection")
    group.add_argument(
        "--delete-ids",
        nargs="+",
        metavar="ID",
        help="Delete documents by their IDs (requires --collection)",
    )
    group.add_argument(
        "--delete-source",
        metavar="SOURCE",
        help="Delete all documents from a source file (requires --collection)",
    )

    parser.add_argument(
        "--collection",
        metavar="NAME",
        help="Collection name (required for --delete-ids and --delete-source)",
    )

    args = parser.parse_args()

    if args.list:
        list_collections(args.chroma_db_path)
    elif args.info:
        collection_info(args.chroma_db_path, args.info)
    elif args.delete:
        delete_collection(args.chroma_db_path, args.delete)
    elif args.delete_ids:
        if not args.collection:
            print("Error: --collection is required for --delete-ids")
            sys.exit(1)
        delete_documents_by_ids(args.chroma_db_path, args.collection, args.delete_ids)
    elif args.delete_source:
        if not args.collection:
            print("Error: --collection is required for --delete-source")
            sys.exit(1)
        delete_documents_by_source(
            args.chroma_db_path, args.collection, args.delete_source
        )


if __name__ == "__main__":
    main()
