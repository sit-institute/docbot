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

| Use Case | When to Use | Guide |
|----------|-------------|-------|
| **Document Indexing** | Index PDFs for semantic search, build RAG pipeline | [use-case-indexing.md](references/use-case-indexing.md) |
| **Document Search** | Q&A system, two-stage retrieval with reranking | [use-case-searching.md](references/use-case-searching.md) |
| **Collection Management** | List, inspect, or delete collections | [use-case-collection-management.md](references/use-case-collection-management.md) |
| **Query Expansion** | Improve search recall with LLM-based expansion | [use-case-query-expansion.md](references/use-case-query-expansion.md) |

## Quick Start

### Index Documents

```bash
# 1. Parse
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
- `.rag/parsed/` - Docling parsed documents
- `.rag/chunks/` - Hierarchical chunks with metadata
- `.rag/embeddings/` - Vector embeddings
- `.rag/chromadb/` - ChromaDB persistent storage

Add `.rag/` to `.gitignore`.

## Collection Naming

**CRITICAL:** No default collection name. Users MUST specify one.

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

| Topic | File |
|-------|------|
| Metadata Schema | [metadata_schema.md](references/metadata_schema.md) |
| ChromaDB API | [chromadb_api.md](references/chromadb_api.md) |
| Model Comparison | [model_comparison.md](references/model_comparison.md) |
| Evaluation | See `.github/skills/local-rag-pipeline/scripts/eval/` |
