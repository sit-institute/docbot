#!/usr/bin/env python3
"""
Step 6: Manage ChromaDB collections.

List, inspect, and delete collections.

Usage:
    python 6_collection_manager.py <chroma_db_path> --list
    python 6_collection_manager.py <chroma_db_path> --info <collection_name>
    python 6_collection_manager.py <chroma_db_path> --delete <collection_name>

Examples:
    python 6_collection_manager.py ./chroma_db/ --list
    python 6_collection_manager.py ./chroma_db/ --info legal_docs
    python 6_collection_manager.py ./chroma_db/ --delete old_docs
"""

import sys
import json
import argparse
import chromadb
from chromadb.config import Settings


def list_collections(chroma_db_path: str):
    """List all collections in the database."""
    client = chromadb.PersistentClient(
        path=chroma_db_path,
        settings=Settings(anonymized_telemetry=False)
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
        path=chroma_db_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error: Collection '{collection_name}' not found")
        print(f"Available collections: {[c.name for c in client.list_collections()]}")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"Collection: {collection_name}")
    print(f"{'='*80}")
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
        for i, (doc_id, doc, meta) in enumerate(zip(
            sample['ids'],
            sample['documents'],
            sample['metadatas']
        ), 1):
            print(f"\n  [{i}] ID: {doc_id}")
            print(f"      File: {meta.get('filename', 'N/A')}")
            print(f"      Pages: {json.loads(meta.get('page_numbers', '[]'))}")
            print(f"      Text: {doc[:150]}...")
    
    print("\n" + "="*80)


def delete_collection(chroma_db_path: str, collection_name: str):
    """Delete a collection from the database."""
    client = chromadb.PersistentClient(
        path=chroma_db_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        
        # Confirm deletion
        response = input(f"\n⚠️  Delete collection '{collection_name}' with {count} chunks? (yes/no): ")
        if response.lower() != 'yes':
            print("Deletion cancelled")
            return
        
        client.delete_collection(name=collection_name)
        print(f"✓ Collection '{collection_name}' deleted successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage ChromaDB collections"
    )
    parser.add_argument("chroma_db_path", help="Path to ChromaDB database")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true",
                      help="List all collections")
    group.add_argument("--info", metavar="COLLECTION",
                      help="Show detailed info for a collection")
    group.add_argument("--delete", metavar="COLLECTION",
                      help="Delete a collection")
    
    args = parser.parse_args()
    
    if args.list:
        list_collections(args.chroma_db_path)
    elif args.info:
        collection_info(args.chroma_db_path, args.info)
    elif args.delete:
        delete_collection(args.chroma_db_path, args.delete)


if __name__ == "__main__":
    main()
