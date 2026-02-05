# Collection Management Use Case

**When to use:** List available collections, get collection information, delete collections, or manage documents within a collection.

## Quick Start

```bash
# List all collections
python scripts/6_collection_manager.py .rag/chromadb/ --list
```

## Usage

```bash
# List all collections
python scripts/6_collection_manager.py .rag/chromadb/ --list

# Get collection info
python scripts/6_collection_manager.py .rag/chromadb/ --info <collection_name>

# Delete collection
python scripts/6_collection_manager.py .rag/chromadb/ --delete <collection_name>

# Delete specific documents by ID
python scripts/6_collection_manager.py .rag/chromadb/ --delete-ids <id1> <id2> ... --collection <name>

# Delete all documents from a source file
python scripts/6_collection_manager.py .rag/chromadb/ --delete-source <filename> --collection <name>
```

## Examples

```bash
# Delete collection
python scripts/6_collection_manager.py .rag/chromadb/ --delete old_collection

# Delete documents by ID (requires --collection)
python scripts/6_collection_manager.py .rag/chromadb/ --delete-ids doc_001 doc_002 doc_003 --collection vw_reports

# Delete all documents from a source file (requires --collection)
python scripts/6_collection_manager.py .rag/chromadb/ --delete-source report_2024.pdf --collection vw_reports
```

## Important Notes

- Collection names are **required** for `--info`, `--delete`, `--delete-ids`, and `--delete-source` operations
- Use `--list` first to see available collections
- Deletion is permanent - there is no undo
