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
python 4_index_to_chromadb.py ./embeddings/legal/ ./chroma_db/ --collection legal_docs

# Terminal 2: Index technical documents (different collection)
python 4_index_to_chromadb.py ./embeddings/tech/ ./chroma_db/ --collection tech_docs
```

**✅ SAFE - Process All Documents in One Batch:**
```bash
# Put all PDFs in one directory - scripts handle batching internally
python 1_parse_documents.py ./all_pdfs/ ./parsed_docs/
```

**❌ UNSAFE - Multiple Instances, Same Collection:**
```bash
# DON'T DO THIS - causes SQLite lock errors and data corruption
python 4_index_to_chromadb.py ./batch1/ ./chroma_db/ --collection docs &
python 4_index_to_chromadb.py ./batch2/ ./chroma_db/ --collection docs &
```

### Performance Optimization Tips

**For 50-100 Large PDFs (Recommended Settings):**

1. **Increase Embedding Batch Size** (GPU memory permitting):
   ```bash
   python 3_generate_embeddings.py ./chunks/ ./embeddings/ --batch-size 64
   # Default: 32, increase to 64-128 for better GPU utilization
   ```

2. **Process All Documents Together** (internal batching is optimized):
   ```bash
   # ✅ Better: One run with all files
   python 1_parse_documents.py ./all_100_pdfs/ ./parsed/
   
   # ❌ Slower: Multiple runs
   python 1_parse_documents.py ./batch1/ ./parsed/ && \
   python 1_parse_documents.py ./batch2/ ./parsed/
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
1. Run `1_parse_documents.py` → Parse PDFs with Docling
2. Run `2_chunk_documents.py` → Create chunks with metadata
3. Run `3_generate_embeddings.py` → Generate embeddings (GPU)
4. Run `4_index_to_chromadb.py` → Store in ChromaDB

**For searching documents:**
1. Run `5_search_documents.py` → Two-stage retrieval with reranking

**For managing collections:**
1. Use `6_collection_manager.py` → List, delete, or inspect collections

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
python scripts/1_parse_documents.py ./my_pdfs/ ./parsed_docs/
# Creates: ./parsed_docs/document1.pkl, ./parsed_docs/document2.pkl, etc.
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

**Model Options:**
- `all-MiniLM-L6-v2`: 384 dim, fast (~20-50ms/chunk)
- `BAAI/bge-base-en-v1.5`: 768 dim, better quality (default)
- `nomic-embed-text`: 768 dim, long context support

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

**Features:**
- Persistent local storage (SQLite + vectors)
- Collection-based organization
- Metadata filtering support
- Automatic ID generation

**Example:**
```bash
python scripts/4_index_to_chromadb.py ./embeddings/ ./chroma_db/ --collection legal_docs
# Creates collection "legal_docs" in ./chroma_db/
```

### 5. Document Search (`5_search_documents.py`)

Two-stage retrieval: vector search + cross-encoder reranking.

**Usage:**
```bash
python scripts/5_search_documents.py <chroma_db_path> "<query>" --collection <name> [--top-k 5] [--rerank-candidates 20]
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
python scripts/6_collection_manager.py <chroma_db_path> --list

# Get collection info
python scripts/6_collection_manager.py <chroma_db_path> --info <collection_name>

# Delete collection
python scripts/6_collection_manager.py <chroma_db_path> --delete <collection_name>
```

## Setup and Installation

**Step 1: Install dependencies**
```bash
pip install -r scripts/requirements.txt --break-system-packages
```

**Step 2: Verify GPU setup**
```bash
python scripts/setup_check.py
```

**Output shows:**
- CUDA availability
- GPU device info
- Installed library versions
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
    tokenizer="gpt-4"        # Tokenizer for counting
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
- **model_comparison.md**: Embedding and reranking model benchmarks
- **chromadb_api.md**: Full ChromaDB API reference and examples
