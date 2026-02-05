# Metadata Schema Reference

Complete reference for metadata structure used throughout the RAG pipeline.

## Chunk Metadata Structure

Each chunk in the pipeline contains the following metadata fields:

```json
{
  "page_numbers": [2, 3],
  "headings": ["1. Introduction", "1.1 Background"],
  "filename": "document.pdf",
  "chunk_index": 0,
  "has_table": false,
  "bboxes": [
    {
      "l": 53.29,
      "t": 287.14,
      "r": 295.56,
      "b": 212.37
    }
  ]
}
```

## Field Descriptions

### page_numbers
- **Type**: `List[int]`
- **Description**: List of page numbers where this chunk appears in the source document
- **Source**: Extracted from Docling provenance data
- **Usage**: Citation, filtering by page
- **Example**: `[2, 3]` for content spanning pages 2-3

### headings
- **Type**: `List[str]`
- **Description**: Hierarchical list of section headings providing context
- **Source**: Extracted from document structure hierarchy
- **Usage**: Displaying context, understanding chunk location
- **Example**: `["1. Introduction", "1.1 Background", "1.1.1 History"]`
- **Note**: Ordered from top-level to most specific

### filename
- **Type**: `str`
- **Description**: Original source document filename
- **Source**: Document origin metadata
- **Usage**: Identifying source, filtering by document
- **Example**: `"contract_2024.pdf"`

### chunk_index
- **Type**: `int`
- **Description**: Sequential index of chunk within document (0-based)
- **Source**: Generated during chunking
- **Usage**: Ordering, referencing specific chunks
- **Example**: `0` for first chunk, `5` for sixth chunk

### has_table
- **Type**: `bool`
- **Description**: Flag indicating if chunk contains table data
- **Source**: Detected from Docling element labels
- **Usage**: Filtering, special handling of tabular content
- **Values**: `true` if any table elements present, `false` otherwise

### bboxes
- **Type**: `List[BoundingBox]`
- **Description**: Bounding box coordinates for chunk location in document
- **Source**: Docling provenance data
- **Usage**: Visualization, highlighting in PDFs
- **Format**: Each bbox contains:
  - `l` (left): Left coordinate
  - `t` (top): Top coordinate
  - `r` (right): Right coordinate
  - `b` (bottom): Bottom coordinate
- **Coordinates**: PDF coordinate system (points from bottom-left)

## ChromaDB Storage

When stored in ChromaDB, some fields are serialized to strings:

```python
{
  "filename": "contract.pdf",
  "page_numbers": "[2, 3]",  # JSON string
  "headings": "[\"1. Introduction\"]",  # JSON string
  "chunk_index": 0,
  "has_table": False
}
```

**Deserialization required for:**
- `page_numbers`: `json.loads(meta["page_numbers"])`
- `headings`: `json.loads(meta["headings"])`

## Filtering Examples

### Filter by document:
```python
results = collection.query(
    query_embeddings=query_emb,
    where={"filename": {"$eq": "contract.pdf"}}
)
```

### Filter by page:
```python
# Note: ChromaDB stores lists as JSON strings
results = collection.query(
    query_embeddings=query_emb,
    where={"page_numbers": {"$contains": 5}}  # Won't work with JSON string
)
```

**Workaround for page filtering:**
Post-filter results after retrieval by deserializing page_numbers.

### Filter by table presence:
```python
results = collection.query(
    query_embeddings=query_emb,
    where={"has_table": {"$eq": True}}
)
```

## Docling Provenance Structure

Original Docling element provenance structure:

```python
{
  "self_ref": "#/texts/28",
  "label": "text",  # or "table", "heading", "list_item"
  "text": "Actual content...",
  "prov": [
    {
      "page_no": 2,
      "bbox": {
        "l": 53.29,
        "t": 287.14,
        "r": 295.56,
        "b": 212.37
      }
    }
  ]
}
```

## Extending Metadata

To add custom metadata fields:

1. **Modify `2_chunk_documents.py`:**
   Add extraction logic in `extract_metadata()` function

2. **Update ChromaDB indexing:**
   Add field to metadata dict in `4_index_to_chromadb.py`

3. **Handle in search:**
   Access new field in results from `5_search_documents.py`

**Example - Adding document type:**

```python
# In extract_metadata()
metadata["doc_type"] = "contract"  # Custom classification

# In ChromaDB indexing
chromadb_meta = {
    # ... existing fields ...
    "doc_type": meta.get("doc_type", "unknown")
}

# In search filtering
where={"doc_type": {"$eq": "contract"}}
```
