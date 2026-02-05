#!/usr/bin/env python3
"""
Step 1: Parse documents (PDF/DOCX) using Docling.

Extracts layout structure, tables, and metadata from documents.
Output: Serialized DoclingDocument objects (.pkl files).

Usage:
    python 1_parse_documents.py <input_dir> <output_dir>

Example:
    python 1_parse_documents.py ./pdfs/ ./parsed_docs/
"""

import sys
import os
import pickle
from pathlib import Path
from docling.document_converter import DocumentConverter
from tqdm import tqdm


def parse_documents(input_dir: str, output_dir: str):
    """
    Parse all PDF/DOCX files in input directory using Docling.

    This function processes documents sequentially for reliability.
    For better performance with many documents, ensure all files are
    in the same input directory for optimal batching.

    Args:
        input_dir: Directory containing PDF/DOCX files
        output_dir: Directory to save parsed DoclingDocument objects
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize Docling converter
    print("Initializing Docling DocumentConverter...")
    converter = DocumentConverter()

    # Find all PDF and DOCX files
    supported_extensions = [".pdf", ".docx", ".doc"]
    files = []
    for ext in supported_extensions:
        files.extend(input_path.glob(f"*{ext}"))

    if not files:
        print(f"No PDF/DOCX files found in {input_dir}")
        return

    print(f"Found {len(files)} documents to parse")

    # Parse each document
    for file_path in tqdm(files, desc="Parsing documents"):
        try:
            # Convert document
            result = converter.convert(str(file_path))
            doc = result.document

            # Save DoclingDocument object
            output_file = output_path / f"{file_path.stem}.pkl"
            with open(output_file, "wb") as f:
                pickle.dump(doc, f)

            # Print summary
            num_texts = len(doc.texts) if hasattr(doc, "texts") else 0
            num_tables = len(doc.tables) if hasattr(doc, "tables") else 0
            tqdm.write(
                f"  ✓ {file_path.name}: {num_texts} text elements, {num_tables} tables"
            )

        except Exception as e:
            tqdm.write(f"  ✗ Error parsing {file_path.name}: {e}")

    print(f"\nParsed documents saved to: {output_path}")
    print(f"Next step: python 2_chunk_documents.py {output_dir} ./chunks/")


def main():
    if len(sys.argv) != 3:
        print("Usage: python 1_parse_documents.py <input_dir> <output_dir>")
        print("\nExample:")
        print("  python 1_parse_documents.py ./pdfs/ ./parsed_docs/")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    parse_documents(input_dir, output_dir)


if __name__ == "__main__":
    main()
