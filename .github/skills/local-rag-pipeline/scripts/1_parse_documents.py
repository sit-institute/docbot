#!/usr/bin/env python3
"""
Step 1: Parse documents (PDF/DOCX) using Docling.

Extracts layout structure, tables, and metadata from documents.
Output:
- .pkl: Serialized DoclingDocument objects
- .md: Full Markdown export (for LLM processing)
- .csv: Extracted tables (for LLM processing)

Usage:
    python 1_parse_documents.py <input_dir> <output_dir>

Example:
    python 1_parse_documents.py ./pdfs/ ./parsed_docs/
"""

import sys
import os
import pickle
import csv
from pathlib import Path
from docling.document_converter import DocumentConverter
from tqdm import tqdm


def export_markdown(doc, md_path: Path):
    """Export document as Markdown file."""
    md_text = doc.export_to_markdown()
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)


def export_tables(doc, doc_dir: Path, min_rows: int = 3, min_cols: int = 2):
    """Export all tables as CSV files with page-based filenames.

    Args:
        doc: DoclingDocument object
        doc_dir: Output directory for CSV files
        min_rows: Minimum number of rows (default: 3)
        min_cols: Minimum number of columns (default: 2)
    """
    if not hasattr(doc, "tables") or not doc.tables:
        return 0

    doc_dir.mkdir(parents=True, exist_ok=True)
    table_count = 0

    for i, table in enumerate(doc.tables):
        table_data = table.export_to_dataframe()
        if table_data is None or table_data.empty:
            continue

        rows, cols = table_data.shape
        if rows < min_rows or cols < min_cols:
            continue

        page_num = 0
        if hasattr(table, "prov") and table.prov:
            for prov in table.prov:
                if hasattr(prov, "page_no"):
                    page_num = prov.page_no
                    break

        csv_path = doc_dir / f"page-{page_num}-table-{i + 1}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(table_data.values.tolist())

        table_count += 1

    return table_count


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

            doc_dir = output_path / file_path.stem
            doc_dir.mkdir(parents=True, exist_ok=True)

            # Save DoclingDocument object
            pkl_path = doc_dir / "docling.pkl"
            with open(pkl_path, "wb") as f:
                pickle.dump(doc, f)

            # Export Markdown
            md_path = doc_dir / "contents.md"
            export_markdown(doc, md_path)

            # Export tables as CSV
            table_dir = doc_dir / "tables"
            num_csv = export_tables(doc, table_dir)

            # Print summary
            num_texts = len(doc.texts) if hasattr(doc, "texts") else 0
            num_tables = len(doc.tables) if hasattr(doc, "tables") else 0
            tqdm.write(
                f"  ✓ {file_path.name}: {num_texts} text elements, "
                f"{num_tables} tables, {num_csv} CSV exported"
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
