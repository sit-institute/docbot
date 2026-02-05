---
name: local-rag-pipeline
description: Complete local RAG system using Docling for parsing, ChromaDB for storage, and GPU-accelerated embeddings/reranking. Supports hierarchical chunking, metadata preservation, and two-stage retrieval.
---

# Local RAG Pipeline

Production-ready local RAG system with state-of-the-art components:
- **Docling**: Document parsing with layout analysis
- **HybridChunker**: Hierarchical, token-aware chunking with metadata
- **ChromaDB**: Local vector database with collections
- **sentence-transformers**: GPU-accelerated embeddings
- **BGE Reranker**: Cross-encoder reranking for improved relevance

## Pipeline Architecture

```
PDF/DOCX → Docling Parser → HybridChunker → Embeddings (GPU) → ChromaDB
                ↓                ↓              ↓              ↓
         Layout Analysis   Token-Aware    768-dim vectors  Persistent
         + Metadata       + Hierarchical   (bge-base)      Storage
```

**Query Flow:**
```
Query → Embedding → Vector Search (top-20) → Reranking (GPU) → Top-5 Results
```

## Use Cases

| Use Case                  | When to Use                                                     | Guide                                                                             |
| ------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Document Indexing**     | Index PDFs for semantic search, build RAG pipeline              | [use-case-indexing.md](references/use-case-indexing.md)                           |
| **Document Search**       | Q&A system, two-stage retrieval with reranking, query expansion | [use-case-searching.md](references/use-case-searching.md)                         |
| **Collection Management** | List, inspect, or delete collections                            | [use-case-collection-management.md](references/use-case-collection-management.md) |

## Quick Start

### Index Documents

```bash
# 1. Parse (creates .rag/parsed/<doc>/docling.pkl, contents.md, tables/*.csv)
python scripts/1_parse_documents.py documents/ .rag/parsed/

# 2. Chunk
python scripts/2_chunk_documents.py .rag/parsed/ .rag/chunks/

# 3. Embed
python scripts/3_generate_embeddings.py .rag/chunks/ .rag/embeddings/

# 4. Index (ASK USER for collection name)
python scripts/4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/ --collection <NAME>
```

### Search Documents

```bash
# ASK USER for collection name first
python scripts/5_search_documents.py .rag/chromadb/ "your query" --collection <NAME>
```

## Directory Structure

All artifacts under `.rag/`:
- `.rag/parsed/` - Docling parsed documents (.pkl) + Markdown/CSV exports
- `.rag/chunks/` - Hierarchical chunks with metadata
- `.rag/embeddings/` - Vector embeddings
- `.rag/chromadb/` - ChromaDB persistent storage

### `.rag/parsed/` Contents

Each document gets its own subdirectory:

```
.rag/parsed/
├── 2025.11_VW/
│   ├── docling.pkl          # DoclingDocument (for chunking pipeline)
│   ├── contents.md          # Full document as Markdown (for LLMs)
│   └── tables/
│       ├── page-3-table-1.csv
│       └── page-4-table-2.csv
```

**Why Markdown + CSV Exports?**

The `.md` and `.csv` files enable LLMs to:
- Generate summaries without the RAG pipeline
- Access full document context
- Process tables as structured data

**Example:**
```bash
python scripts/1_parse_documents.py documents/ .rag/parsed/
# Creates per-document directories with .pkl, .md, and tables/*.csv
```

## Collection Naming

**CRITICAL:** No default collection name. Users MUST specify one. You may suggest a name based on project/document context.

**When to ask user:**
- Before `4_index_to_chromadb.py` (indexing)
- Before `5_search_documents.py` (searching)
- Before `6_collection_manager.py` with `--info` or `--delete`

## Concurrency Model

**Sequential execution required:**
- ChromaDB SQLite backend: single-writer limitation
- GPU memory: models are 2-4GB each
- Optimized for 50-100 large documents

**Safe parallel options:**
- Same pipeline, different collections (different terminals)
- Process all documents in one batch

## Setup

```bash
# Quick check
python scripts/setup_check.py --quick

# Install dependencies
python scripts/setup_check.py --install
```

## Reference Documentation

| Topic           | File                                                |
| --------------- | --------------------------------------------------- |
| Metadata Schema | [metadata_schema.md](references/metadata_schema.md) |
| ChromaDB API    | [chromadb_api.md](references/chromadb_api.md)       |
