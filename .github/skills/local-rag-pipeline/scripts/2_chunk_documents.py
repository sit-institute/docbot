#!/usr/bin/env python3
"""
Step 2: Chunk parsed documents using HybridChunker.

Applies hierarchical, token-aware chunking while preserving metadata.
Output: JSON files with chunks and metadata.

Usage:
    python 2_chunk_documents.py <parsed_dir> <output_dir> [--max-tokens MAX]

Example:
    python 2_chunk_documents.py ./parsed_docs/ ./chunks/ --max-tokens 512
"""

import sys
import os
import json
import pickle
import argparse
from pathlib import Path
from docling.chunking import HybridChunker
from tqdm import tqdm


def extract_metadata(chunk):
    """Extract metadata from a chunk object."""
    metadata = {
        "page_numbers": [],
        "headings": [],
        "filename": "",
        "chunk_index": 0,
        "has_table": False,
        "bboxes": [],
    }

    try:
        # Extract page numbers from provenance
        if hasattr(chunk, "meta") and hasattr(chunk.meta, "doc_items"):
            page_numbers = set()
            for item in chunk.meta.doc_items:
                if hasattr(item, "prov"):
                    for prov in item.prov:
                        if hasattr(prov, "page_no"):
                            page_numbers.add(prov.page_no)
                        if hasattr(prov, "bbox"):
                            bbox = prov.bbox
                            metadata["bboxes"].append(
                                {
                                    "l": bbox.l if hasattr(bbox, "l") else 0,
                                    "t": bbox.t if hasattr(bbox, "t") else 0,
                                    "r": bbox.r if hasattr(bbox, "r") else 0,
                                    "b": bbox.b if hasattr(bbox, "b") else 0,
                                }
                            )

                # Check for tables
                if hasattr(item, "label") and item.label == "table":
                    metadata["has_table"] = True

            metadata["page_numbers"] = sorted(list(page_numbers))

        # Extract headings
        if hasattr(chunk, "meta") and hasattr(chunk.meta, "headings"):
            metadata["headings"] = chunk.meta.headings if chunk.meta.headings else []

        # Extract filename
        if hasattr(chunk, "meta") and hasattr(chunk.meta, "origin"):
            if hasattr(chunk.meta.origin, "filename"):
                metadata["filename"] = chunk.meta.origin.filename

    except Exception as e:
        print(f"Warning: Error extracting metadata: {e}")

    return metadata


def chunk_documents(parsed_dir: str, output_dir: str, max_tokens: int = 512):
    """
    Chunk parsed documents using HybridChunker.

    Args:
        parsed_dir: Directory containing parsed .pkl files
        output_dir: Directory to save chunk JSON files
        max_tokens: Maximum tokens per chunk
    """
    parsed_path = Path(parsed_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize chunker
    print(f"Initializing HybridChunker (max_tokens={max_tokens})...")
    chunker = HybridChunker(
        max_tokens=max_tokens, merge_list_items=True, tokenizer="gpt2"
    )

    # Find all .pkl files
    pkl_files = list(parsed_path.glob("*.pkl"))

    if not pkl_files:
        print(f"No .pkl files found in {parsed_dir}")
        return

    print(f"Found {len(pkl_files)} parsed documents")

    # Process each document
    total_chunks = 0
    for pkl_file in tqdm(pkl_files, desc="Chunking documents"):
        try:
            # Load DoclingDocument
            with open(pkl_file, "rb") as f:
                doc = pickle.load(f)

            # Generate chunks
            chunks = list(chunker.chunk(doc))

            # Extract text and metadata for each chunk
            chunk_data = []
            for idx, chunk in enumerate(chunks):
                metadata = extract_metadata(chunk)
                metadata["chunk_index"] = idx

                chunk_data.append({"text": chunk.text, "metadata": metadata})

            # Save chunks as JSON
            output_file = output_path / f"{pkl_file.stem}_chunks.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(chunk_data, f, indent=2, ensure_ascii=False)

            total_chunks += len(chunks)
            tqdm.write(f"  ✓ {pkl_file.name}: {len(chunks)} chunks")

        except Exception as e:
            tqdm.write(f"  ✗ Error chunking {pkl_file.name}: {e}")

    print(f"\nTotal chunks created: {total_chunks}")
    print(f"Chunks saved to: {output_path}")
    print(f"Next step: python 3_generate_embeddings.py {output_dir} ./embeddings/")


def main():
    parser = argparse.ArgumentParser(
        description="Chunk parsed documents with HybridChunker"
    )
    parser.add_argument("parsed_dir", help="Directory containing .pkl files")
    parser.add_argument("output_dir", help="Directory to save chunk JSON files")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum tokens per chunk (default: 512)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.parsed_dir):
        print(f"Error: Parsed directory not found: {args.parsed_dir}")
        sys.exit(1)

    chunk_documents(args.parsed_dir, args.output_dir, args.max_tokens)


if __name__ == "__main__":
    main()
