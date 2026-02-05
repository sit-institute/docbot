#!/usr/bin/env python3
"""
Step 3: Generate embeddings for chunks using sentence-transformers.

GPU-accelerated batch embedding generation.
Output: NPZ files with embeddings and metadata.

Usage:
    python 3_generate_embeddings.py <chunks_dir> <output_dir> [--model MODEL] [--batch-size SIZE]

Example:
    python 3_generate_embeddings.py ./chunks/ ./embeddings/ --model BAAI/bge-base-en-v1.5 --batch-size 32
"""

import sys
import os
import json
import numpy as np
import argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm


def generate_embeddings(
    chunks_dir: str, output_dir: str, model_name: str, batch_size: int
):
    """
    Generate embeddings for all chunks using sentence-transformers.

    Args:
        chunks_dir: Directory containing chunk JSON files
        output_dir: Directory to save embedding NPZ files
        model_name: Name of sentence-transformers model
        batch_size: Batch size for encoding
    """
    chunks_path = Path(chunks_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Check GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load embedding model
    print(f"Loading embedding model: {model_name}")
    embedder = SentenceTransformer(model_name, device=device)
    embedding_dim = embedder.get_sentence_embedding_dimension()
    print(f"Embedding dimension: {embedding_dim}")

    # Find all chunk JSON files
    json_files = list(chunks_path.glob("*_chunks.json"))

    if not json_files:
        print(f"No chunk JSON files found in {chunks_dir}")
        return

    print(f"Found {len(json_files)} chunk files")

    # Process each file
    total_chunks = 0
    for json_file in tqdm(json_files, desc="Generating embeddings"):
        try:
            # Load chunks
            with open(json_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            if not chunks:
                tqdm.write(f"  ⚠ {json_file.name}: No chunks found, skipping")
                continue

            # Extract texts
            texts = [chunk["text"] for chunk in chunks]

            # Generate embeddings (GPU-accelerated batch processing)
            embeddings = embedder.encode(
                texts,
                batch_size=batch_size,
                convert_to_tensor=True,
                normalize_embeddings=True,  # For cosine similarity
                show_progress_bar=False,
            )

            # Convert to numpy
            embeddings_np = embeddings.cpu().numpy()

            # Save embeddings and metadata
            output_file = output_path / f"{json_file.stem}_embeddings.npz"
            np.savez_compressed(
                output_file,
                embeddings=embeddings_np,
                metadata=json.dumps([chunk["metadata"] for chunk in chunks]),
                texts=json.dumps(texts),
                model_name=model_name,
                embedding_dim=embedding_dim,
            )

            total_chunks += len(chunks)
            tqdm.write(
                f"  ✓ {json_file.name}: {len(chunks)} embeddings ({embeddings_np.shape})"
            )

        except Exception as e:
            tqdm.write(f"  ✗ Error processing {json_file.name}: {e}")

    print(f"\nTotal embeddings generated: {total_chunks}")
    print(f"Embeddings saved to: {output_path}")
    print(
        f"Next step: python 4_index_to_chromadb.py {output_dir} ./chroma_db/ --collection my_collection"
    )


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for chunks")
    parser.add_argument("chunks_dir", help="Directory containing chunk JSON files")
    parser.add_argument("output_dir", help="Directory to save embedding NPZ files")
    parser.add_argument(
        "--model",
        default="BAAI/bge-base-en-v1.5",
        help="sentence-transformers model name (default: BAAI/bge-base-en-v1.5)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for encoding (default: 64, reduce to 32 if OOM errors occur)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.chunks_dir):
        print(f"Error: Chunks directory not found: {args.chunks_dir}")
        sys.exit(1)

    generate_embeddings(args.chunks_dir, args.output_dir, args.model, args.batch_size)


if __name__ == "__main__":
    main()
