# Document Search Use Case

**When to use:** Build a local document Q&A system, search structured content with metadata preservation, or implement two-stage retrieval with reranking.

## Quick Start

```bash
# ASK USER for collection name first
python scripts/5_search_documents.py .rag/chromadb/ "your query" --collection <NAME>
```

## Two-Stage Retrieval

The search uses vector search followed by cross-encoder reranking for improved relevance.

**Process:**
1. **Stage 1**: Vector search retrieves top-20 candidates (fast, ~10-50ms)
2. **Stage 2**: Cross-encoder reranks candidates (precise, ~200-500ms)
3. Returns top-K results with metadata (page numbers, headings, etc.)

## Usage

```bash
python scripts/5_search_documents.py <chroma_db_path> "<query>" --collection <name> [--top-k 5] [--rerank-candidates 20] [--filter-filename <filename>]
```

**REQUIRED:** `--collection <name>` must be explicitly specified. No default exists.

### Examples

```bash
# Basic search
python scripts/5_search_documents.py .rag/chromadb/ "payment terms" --collection vw_reports

# Search with filename filter
python scripts/5_search_documents.py .rag/chromadb/ "Fördergeld" --collection vw_reports --filter-filename antragstellung.pdf

# Adjust top-k results
python scripts/5_search_documents.py .rag/chromadb/ "deadline" --collection vw_reports --top-k 10
```

## Reranker Options

- `BAAI/bge-reranker-base`: Fast, 278M params
- `BAAI/bge-reranker-v2-m3`: Multilingual, 560M params (default)
- `BAAI/bge-reranker-large`: Best quality, 560M params

## Query Expansion

Query expansion is handled by the agent using LLM-based expansion. See [use-case-query-expansion.md](use-case-query-expansion.md) for details.

## Output Format

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

## Performance Expectations

**Retrieval:**
- Vector Search: 10-50ms (for 10k chunks)
- Reranking (20 candidates): 200-500ms
- **Total Latency**: 300-600ms/query
