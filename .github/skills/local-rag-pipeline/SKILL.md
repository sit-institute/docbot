---
name: local-rag-pipeline
description: Complete local RAG (Retrieval-Augmented Generation) system using Docling for document parsing, ChromaDB for vector storage, and GPU-accelerated embedding/reranking. Use this skill when users want to (1) index PDF/DOCX documents locally with semantic search, (2) build a local document Q&A system, (3) extract and search structured content from documents with metadata preservation, (4) implement two-stage retrieval with reranking, or (5) create a production-ready RAG pipeline without external APIs. Supports hierarchical chunking with metadata (page numbers, headings, bounding boxes), GPU-accelerated embeddings (sentence-transformers), local vector database (ChromaDB), and cross-encoder reranking (BGE models).
---

# Local RAG Pipeline

Production-ready local RAG system with state-of-the-art components:
- **Docling**: Document parsing with layout analysis (tables, headers, structure)
- **HybridChunker**: Hierarchical, token-aware chunking with metadata preservation
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
                                                                   ↓
                                                          with page_no,
                                                          headings, bbox
```

## 📁 Directory Structure

**All pipeline artifacts are stored under `.rag/` to keep the project root clean:**

```
.rag/
├── parsed/         # Step 1: Docling parsed documents (.pkl)
├── chunks/         # Step 2: Hierarchical chunks with metadata (.json)
├── embeddings/     # Step 3: Vector embeddings (.npz)
└── chromadb/       # Step 4: ChromaDB persistent storage
```

**Add `.rag/` to `.gitignore`** to avoid committing large binary files:
```bash
echo ".rag/" >> .gitignore
```

**Storage Requirements (approximate):**
- Parsed documents: ~5-10% of PDF size
- Chunks: ~20-30% of PDF size (JSON with metadata)
- Embeddings: ~500 bytes/chunk (768-dim float32)
- ChromaDB: ~800 bytes/chunk (embeddings + metadata + SQLite overhead)

**Example for 100 PDFs (50 pages each, ~50MB total):**
- `.rag/parsed/`: ~5MB
- `.rag/chunks/`: ~15MB
- `.rag/embeddings/`: ~25MB
- `.rag/chromadb/`: ~40MB
- **Total: ~85MB**

## 🏷️ Collection Naming

**CRITICAL: There is NO default collection name. Users MUST explicitly specify a collection name.**

**When to ask the user for a collection name:**
- Before running `4_index_to_chromadb.py` (indexing)
- Before running `5_search_documents.py` (searching)
- Before running `6_collection_manager.py` with `--info` or `--delete`

**Naming conventions:**
- Use descriptive, project-specific names: `research_2025`, `legal_contracts`, `technical_docs`
- Avoid generic names like `docs`, `documents`, `data`
- Use underscores for multi-word names: `project_reports_2025`
- Keep names lowercase for consistency

**Example workflow:**
```bash
# WRONG: No collection specified
python scripts/4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/
# Error: --collection is required

# CORRECT: Ask user first, then specify collection
python scripts/4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/ --collection vw_reports_2025
```

**Multiple collections in same ChromaDB:**
```bash
# Different document types can share the same .rag/chromadb/ directory
python scripts/4_index_to_chromadb.py .rag/embeddings/vw/ .rag/chromadb/ --collection vw_reports
python scripts/4_index_to_chromadb.py .rag/embeddings/bmw/ .rag/chromadb/ --collection bmw_reports

# List all collections
python scripts/6_collection_manager.py .rag/chromadb/ --list
```

## ⚠️ Concurrency & Performance Model

**This pipeline is designed for SEQUENTIAL execution:**

### Why Sequential Processing?

1. **ChromaDB SQLite Backend**: Single-writer limitation prevents parallel indexing to the same collection
2. **GPU Memory Management**: Running multiple instances exhausts VRAM (models are 2-4GB each)
3. **Optimized for Large PDFs**: Design optimized for 50-100 large documents (>50 pages), not thousands of small files

### Safe Parallel Processing Options

**✅ SAFE - Same Pipeline, Different Collections:**
```bash
# Terminal 1: Index legal documents
python 4_index_to_chromadb.py .rag/embeddings/legal/ .rag/chromadb/ --collection legal_docs

# Terminal 2: Index technical documents (different collection)
python 4_index_to_chromadb.py .rag/embeddings/tech/ .rag/chromadb/ --collection tech_docs
```

**✅ SAFE - Process All Documents in One Batch:**
```bash
# Put all PDFs in one directory - scripts handle batching internally
python 1_parse_documents.py documents/ .rag/parsed/
```

**❌ UNSAFE - Multiple Instances, Same Collection:**
```bash
# DON'T DO THIS - causes SQLite lock errors and data corruption
python 4_index_to_chromadb.py .rag/embeddings/batch1/ .rag/chromadb/ --collection docs &
python 4_index_to_chromadb.py .rag/embeddings/batch2/ .rag/chromadb/ --collection docs &
```

### Performance Optimization Tips

**For 50-100 Large PDFs (Recommended Settings):**

1. **Increase Embedding Batch Size** (GPU memory permitting):
   ```bash
   python 3_generate_embeddings.py .rag/chunks/ .rag/embeddings/ --batch-size 64
   # Default: 32, increase to 64-128 for better GPU utilization
   ```

2. **Process All Documents Together** (internal batching is optimized):
   ```bash
   # ✅ Better: One run with all files
   python 1_parse_documents.py documents/ .rag/parsed/
   
   # ❌ Slower: Multiple runs
   python 1_parse_documents.py documents/batch1/ .rag/parsed/ && \
   python 1_parse_documents.py documents/batch2/ .rag/parsed/
   ```

3. **Monitor GPU Usage**:
   ```bash
   watch -n 1 nvidia-smi  # Ensure GPU utilization stays >80% during embedding
   ```

**Expected Throughput (RTX 3080, large PDFs):**
- Parsing: ~2-5 seconds/page
- Embedding: ~20ms/chunk (batch-size 64)
- Indexing: ~5ms/chunk
- **Total: 100-200 pages/minute for 50-100 document batches**

## Workflow Decision Tree

**For indexing documents:**
1. Run `1_parse_documents.py documents/ .rag/parsed/` → Parse PDFs with Docling
2. Run `2_chunk_documents.py .rag/parsed/ .rag/chunks/` → Create chunks with metadata
3. Run `3_generate_embeddings.py .rag/chunks/ .rag/embeddings/` → Generate embeddings (GPU)
4. **ASK USER for collection name**, then run:
   `4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/ --collection <NAME>` → Store in ChromaDB

**For searching documents:**
1. **ASK USER for collection name**, then run:
   `5_search_documents.py .rag/chromadb/ "your query" --collection <NAME>` → Two-stage retrieval with reranking

**For managing collections:**
1. Use `6_collection_manager.py .rag/chromadb/ --list` → List all collections
2. **ASK USER for collection name** before `--info` or `--delete` operations

## Core Scripts

All scripts are in `scripts/` directory and designed to run sequentially:

### 1. Document Parsing (`1_parse_documents.py`)

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

### 2. Document Chunking (`2_chunk_documents.py`)

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

### 3. Embedding Generation (`3_generate_embeddings.py`)

GPU-accelerated batch embedding generation with sentence-transformers.

**Usage:**
```bash
python scripts/3_generate_embeddings.py <chunks_dir> <output_dir> [--model BAAI/bge-base-en-v1.5] [--batch-size 32]
```

**Model (default: all-MiniLM-L6-v2):**
- `sentence-transformers/all-MiniLM-L6-v2`: 384 dim, fast (~20-50ms/chunk), CPU-friendly

**Output:** NPZ files containing:
- `embeddings`: NumPy array of vectors
- `metadata`: Preserved chunk metadata

**GPU Optimization:**
- Auto-detects CUDA
- Batch processing for efficiency
- Normalized embeddings for cosine similarity

### 4. ChromaDB Indexing (`4_index_to_chromadb.py`)

Store embeddings and metadata in ChromaDB collections.

**Usage:**
```bash
python scripts/4_index_to_chromadb.py <embeddings_dir> <chroma_db_path> --collection <name>
```

**⚠️ REQUIRED: `--collection <name>` must be explicitly specified. No default exists.**

**Features:**
- Persistent local storage (SQLite + vectors)
- Collection-based organization
- Metadata filtering support
- Automatic ID generation

**Example (always ask user for collection name first):**
```bash
# User specifies: "vw_reports_2025"
python scripts/4_index_to_chromadb.py .rag/embeddings/ .rag/chromadb/ --collection vw_reports_2025
# Creates collection "vw_reports_2025" in .rag/chromadb/
```

### 5. Document Search (`5_search_documents.py`)

Two-stage retrieval: vector search + cross-encoder reranking.

**Usage:**
```bash
python scripts/5_search_documents.py <chroma_db_path> "<query>" --collection <name> [--top-k 5] [--rerank-candidates 20] [--filter-filename <filename>]
```

**⚠️ REQUIRED: `--collection <name>` must be explicitly specified. No default exists.**

**Before running: Ask user which collection to search in.**

**Examples:**
```bash
# Basic search
python scripts/5_search_documents.py .rag/chromadb/ "payment terms" --collection vw_reports

# Search with filename filter
python scripts/5_search_documents.py .rag/chromadb/ "Fördergeld" --collection vw_reports --filter-filename antragstellung.pdf
```

**Process:**
1. **Stage 1**: Vector search retrieves top-20 candidates (fast, ~10-50ms)
2. **Stage 2**: Cross-encoder reranks candidates (precise, ~200-500ms)
3. Returns top-K results with metadata (page numbers, headings, etc.)

**Reranker Options:**
- `BAAI/bge-reranker-base`: Fast, 278M params
- `BAAI/bge-reranker-v2-m3`: Multilingual, 560M params (default)
- `BAAI/bge-reranker-large`: Best quality, 560M params

**Output Format:**
```json
{
  "rank": 1,
  "score": 0.89,
  "text": "Chunk content...",
  "metadata": {
    "filename": "contract.pdf",
    "page_numbers": [5],
    "headings": ["3. Payment Terms"]
  }
}
```

### 6. Collection Manager (`6_collection_manager.py`)

Manage ChromaDB collections.

**Usage:**
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

**Examples:**
```bash
# Delete collection
python scripts/6_collection_manager.py .rag/chromadb/ --delete old_collection

# Delete documents by ID (requires --collection)
python scripts/6_collection_manager.py .rag/chromadb/ --delete-ids doc_001 doc_002 doc_003 --collection vw_reports

# Delete all documents from a source file (requires --collection)
python scripts/6_collection_manager.py .rag/chromadb/ --delete-source report_2024.pdf --collection vw_reports
```

## Setup and Installation

**Step 1: Verify setup (quick check)**
```bash
python scripts/setup_check.py --quick
```

**Step 2: Install dependencies (if needed)**
```bash
python scripts/setup_check.py --install
```

**Full verification with dependency installation:**
```bash
python scripts/setup_check.py --full
```

**Exit codes for CI/CD:**
- `0` = All checks passed
- `1` = Some dependencies or directories missing

**Check directories only:**
```bash
python scripts/setup_check.py --dirs-only
```

**Setup check output shows:**
- CUDA availability
- GPU device info
- Installed library versions
- Directory structure
- Model download locations

## Performance Expectations

**Hardware: RTX 3080 (10GB VRAM)**

**Indexing:**
- PDF Parsing (Docling): ~2-5s/page
- Chunking (HybridChunker): ~0.1s/document
- Embedding (bge-base, batch=32): ~20ms/chunk
- ChromaDB Indexing: ~5ms/chunk
- **Total**: ~100-200 pages/minute

**Retrieval:**
- Vector Search: 10-50ms (for 10k chunks)
- Reranking (20 candidates): 200-500ms
- **Total Latency**: 300-600ms/query

## Advanced Configuration

### Adjusting Chunk Size

 Edit `scripts/2_chunk_documents.py`:
 ```python
 chunker = HybridChunker(
     max_tokens=512,          # Reduce for smaller models
     merge_list_items=True,   # Set False to separate list items
     tokenizer="cl100k_base"  # OpenAI-compatible tokenizer (GPT-4/GPT-3.5 standard)
 )
 ```

### Custom Metadata Filtering

In `scripts/5_search_documents.py`, add ChromaDB where clauses:
```python
results = collection.query(
    query_embeddings=query_emb,
    n_results=20,
    where={
        "filename": {"$eq": "contract.pdf"},
        "page_numbers": {"$contains": 5},
        "has_table": {"$eq": True}
    }
)
```

### Multi-GPU Support

Edit embedding/reranking scripts to use multiple GPUs:
```python
# In 3_generate_embeddings.py
embeddings = embedder.encode(
    texts,
    device=["cuda:0", "cuda:1"]  # Use multiple GPUs
)
```

## Troubleshooting

**GPU not detected:**
- Run `scripts/setup_check.py` to verify CUDA
- Check: `python -c "import torch; print(torch.cuda.is_available())"`
- Reinstall PyTorch with CUDA support

**Out of memory errors:**
- Reduce `--batch-size` in embedding/reranking scripts
- Use smaller models (all-MiniLM-L6-v2, bge-reranker-base)
- Process documents in smaller batches

**Slow indexing:**
- Increase `--batch-size` if GPU memory allows (try 64-128 for large PDFs)
- Ensure all documents are in one directory for optimal batching
- Consider using smaller embedding model for speed

**Empty search results:**
- Verify collection name matches: `scripts/6_collection_manager.py ./chroma_db/ --list`
- Check embedding model consistency between indexing and search
- Inspect collection: `scripts/6_collection_manager.py ./chroma_db/ --info <name>`

**"Database is locked" or SQLite errors:**
- Another process is writing to the same ChromaDB collection
- Check running processes: `ps aux | grep python.*index_to_chromadb`
- Wait for other processes to complete (ChromaDB is single-writer)
- Use different collection names for parallel indexing of different document sets

## Reference Documentation

See `references/` for detailed guides:
- **metadata_schema.md**: Complete metadata structure and field descriptions
- **chromadb_api.md**: Full ChromaDB API reference and examples
