# Document Indexing Use Case

**When to use:** Index PDF/DOCX documents for semantic search, build a document knowledge base, or create a production-ready RAG pipeline without external APIs.

## Quick Start

```bash
# Step 1: Parse PDFs with Docling
python scripts/1_parse_documents.py documents/ .rag/parsed/

# Step 2: Create hierarchical chunks with metadata
python scripts/2_chunk_documents.py .rag/parsed/ .rag/chunks/

# Step 3: Generate GPU-accelerated embeddings
python scripts/3_generate_embeddings.py .rag/chunks/ .rag/embeddings/

# Step 4: Store in ChromaDB (ASK USER for collection name first)
python scripts/4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/ --collection <NAME>
```

## Detailed Steps

### 1. Document Parsing

Parse PDFs/DOCX with Docling's layout analysis engine.

**Usage:**
```bash
python scripts/1_parse_documents.py <input_dir> <output_dir>
```

**Output:** Serialized DoclingDocument objects (.pkl) with:
- Layout structure (headers, paragraphs, tables, lists)
- Metadata per element (page_no, bbox coordinates, label)
- Dual-format tables (Markdown + CSV)

**Example:**
```bash
python scripts/1_parse_documents.py documents/ .rag/parsed/
# Creates: .rag/parsed/document1.pkl, .rag/parsed/document2.pkl, etc.
```

### 2. Document Chunking

Apply HybridChunker (hierarchical + token-aware) to parsed documents.

**Usage:**
```bash
python scripts/2_chunk_documents.py <parsed_dir> <output_dir> [--max-tokens 512]
```

**Features:**
- Respects document hierarchy (sections, headings)
- Token-aware splitting (configurable max_tokens)
- Metadata preservation (page numbers, headings, bboxes)
- Smart list merging

**Output:** JSON files with chunk arrays, each containing:
```json
{
  "text": "Chunk content...",
  "metadata": {
    "page_numbers": [2, 3],
    "headings": ["1. Introduction", "1.1 Background"],
    "filename": "document.pdf",
    "chunk_index": 0,
    "has_table": false,
    "bboxes": [{"l": 53.29, "t": 287.14, "r": 295.56, "b": 212.37}]
  }
}
```

### 3. Embedding Generation

GPU-accelerated batch embedding generation with sentence-transformers.

**Usage:**
```bash
python scripts/3_generate_embeddings.py <chunks_dir> <output_dir> [--model BAAI/bge-base-en-v1.5] [--batch-size 32]
```

**Model Options:**
- `all-MiniLM-L6-v2`: 384 dim, fast (~20-50ms/chunk), CPU-friendly
- `BAAI/bge-base-en-v1.5`: 768 dim, better quality (default)
- `nomic-embed-text`: 768 dim, long context support

**Output:** NPZ files containing:
- `embeddings`: NumPy array of vectors
- `metadata`: Preserved chunk metadata

**GPU Optimization:**
- Auto-detects CUDA
- Batch processing for efficiency
- Normalized embeddings for cosine similarity

### 4. ChromaDB Indexing

Store embeddings and metadata in ChromaDB collections.

**Usage:**
```bash
python scripts/4_index_to_chromadb.py <embeddings_dir> <chroma_db_path> --collection <name>
```

**REQUIRED:** `--collection <name>` must be explicitly specified. No default exists.

**Features:**
- Persistent local storage (SQLite + vectors)
- Collection-based organization
- Metadata filtering support
- Automatic ID generation

**Example:**
```bash
python scripts/4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/ --collection vw_reports_2025
# Creates collection "vw_reports_2025" in .rag/chromadb/
```

## Performance Expectations

**Hardware: RTX 3080 (10GB VRAM)**

**Indexing:**
- PDF Parsing (Docling): ~2-5s/page
- Chunking (HybridChunker): ~0.1s/document
- Embedding (bge-base, batch=32): ~20ms/chunk
- ChromaDB Indexing: ~5ms/chunk
- **Total**: ~100-200 pages/minute for 50-100 document batches
