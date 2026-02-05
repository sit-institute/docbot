# ChromaDB API Reference

Complete reference for ChromaDB operations in the RAG pipeline.

## Client Initialization

### Persistent Client (Recommended)
```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

**Parameters:**
- `path`: Directory for database storage (created if doesn't exist)
- `anonymized_telemetry`: Disable telemetry (default: False)
- `allow_reset`: Allow database reset operations (default: False)

### In-Memory Client (Testing Only)
```python
client = chromadb.Client()
```
- Data lost when process ends
- Useful for unit tests

## Collection Operations

### Create or Get Collection
```python
collection = client.get_or_create_collection(
    name="my_documents",
    metadata={
        "description": "Technical documentation",
        "embedding_model": "BAAI/bge-base-en-v1.5",
        "embedding_dim": 768,
        "created_date": "2024-01-15"
    }
)
```

**Name constraints:**
- 3-63 characters
- Alphanumeric, hyphens, underscores only
- Must start/end with alphanumeric

**Metadata:**
- Optional key-value pairs
- Useful for tracking model versions, creation dates
- Not used for querying (use document metadata instead)

### Get Existing Collection
```python
collection = client.get_collection(name="my_documents")
```
- Raises exception if collection doesn't exist

### List Collections
```python
collections = client.list_collections()
for coll in collections:
    print(f"{coll.name}: {coll.count()} documents")
```

### Delete Collection
```python
client.delete_collection(name="my_documents")
```
- Permanent deletion
- No confirmation prompt

## Document Operations

### Add Documents
```python
collection.add(
    ids=["doc1", "doc2", "doc3"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]],
    documents=["Text content 1", "Text content 2", "Text content 3"],
    metadatas=[
        {"filename": "file1.pdf", "page": 1},
        {"filename": "file1.pdf", "page": 2},
        {"filename": "file2.pdf", "page": 1}
    ]
)
```

**Parameters:**
- `ids`: Unique identifiers (required)
- `embeddings`: Vector embeddings (required)
- `documents`: Text content (optional, for display)
- `metadatas`: Metadata dicts (optional, for filtering)

**ID constraints:**
- Must be unique within collection
- String type
- Recommended format: `{doc_name}_chunk_{index}`

**Metadata constraints:**
- Values must be: str, int, float, bool
- Lists/dicts stored as JSON strings
- No nested structures directly

### Update Documents
```python
collection.update(
    ids=["doc1"],
    embeddings=[[0.15, 0.25, ...]],
    documents=["Updated text"],
    metadatas=[{"filename": "file1_v2.pdf"}]
)
```
- Updates existing documents by ID
- All fields optional (only update what's provided)

### Upsert Documents
```python
collection.upsert(
    ids=["doc1", "doc4"],
    embeddings=[[0.1, 0.2, ...], [0.7, 0.8, ...]],
    documents=["Text 1", "Text 4"],
    metadatas=[{"filename": "f1.pdf"}, {"filename": "f4.pdf"}]
)
```
- Insert if ID doesn't exist
- Update if ID exists

### Delete Documents
```python
# Delete by IDs
collection.delete(ids=["doc1", "doc2"])

# Delete by filter
collection.delete(where={"filename": "old_file.pdf"})

# Delete all
collection.delete(where={})  # Careful!
```

### Get Documents
```python
# Get specific IDs
results = collection.get(
    ids=["doc1", "doc2"],
    include=["documents", "embeddings", "metadatas"]
)

# Get with filter
results = collection.get(
    where={"filename": "file1.pdf"},
    limit=10,
    include=["documents", "metadatas"]
)

# Get all (use with caution)
results = collection.get(include=["documents", "metadatas"])
```

**Include options:**
- `"documents"`: Text content
- `"embeddings"`: Vector embeddings
- `"metadatas"`: Metadata dicts
- `"distances"`: Distances from query (only in queries)

### Peek Documents
```python
# Get first N documents
results = collection.peek(limit=5)
```
- Quick way to inspect collection
- Returns first N documents by insertion order

### Count Documents
```python
count = collection.count()
print(f"Collection has {count} documents")
```

## Query Operations

### Basic Query
```python
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3, ...]],
    n_results=10
)
```

**Returns:**
```python
{
    'ids': [['doc1', 'doc5', 'doc3', ...]],
    'distances': [[0.15, 0.23, 0.31, ...]],
    'documents': [['Text 1', 'Text 5', 'Text 3', ...]],
    'metadatas': [[{...}, {...}, {...}, ...]]
}
```

### Query with Metadata Filtering
```python
results = collection.query(
    query_embeddings=[[0.1, 0.2, ...]],
    n_results=20,
    where={
        "filename": {"$eq": "contract.pdf"},
        "page": {"$gte": 5, "$lte": 10}
    }
)
```

### Query with Document Filtering
```python
results = collection.query(
    query_embeddings=[[0.1, 0.2, ...]],
    n_results=10,
    where_document={
        "$contains": "payment terms"
    }
)
```

## Metadata Filtering Operators

### Comparison Operators
- `$eq`: Equal to
- `$ne`: Not equal to
- `$gt`: Greater than
- `$gte`: Greater than or equal
- `$lt`: Less than
- `$lte`: Less than or equal

**Examples:**
```python
# Exact match
where={"filename": {"$eq": "document.pdf"}}

# Numeric range
where={"page": {"$gte": 5, "$lte": 10}}

# Not equal
where={"status": {"$ne": "archived"}}
```

### Logical Operators
- `$and`: All conditions must match
- `$or`: Any condition must match

**Examples:**
```python
# AND (implicit)
where={
    "filename": {"$eq": "doc.pdf"},
    "page": {"$gte": 5}
}

# Explicit AND
where={
    "$and": [
        {"filename": {"$eq": "doc.pdf"}},
        {"page": {"$gte": 5}}
    ]
}

# OR
where={
    "$or": [
        {"filename": {"$eq": "doc1.pdf"}},
        {"filename": {"$eq": "doc2.pdf"}}
    ]
}
```

### Membership Operators
- `$in`: Value in list
- `$nin`: Value not in list

**Examples:**
```python
# In list
where={"category": {"$in": ["legal", "finance"]}}

# Not in list
where={"status": {"$nin": ["draft", "archived"]}}
```

## Document Content Filtering

### Text Search Operators
- `$contains`: Document contains substring
- `$not_contains`: Document doesn't contain substring

**Examples:**
```python
# Contains
where_document={"$contains": "payment"}

# Complex document filter
where_document={
    "$and": [
        {"$contains": "payment"},
        {"$not_contains": "draft"}
    ]
}
```

**Limitations:**
- Case-sensitive by default
- No fuzzy matching
- No regex support
- Full-text search on document field only

## Advanced Usage

### Batch Queries
```python
# Query multiple embeddings at once
results = collection.query(
    query_embeddings=[
        [0.1, 0.2, ...],  # Query 1
        [0.5, 0.6, ...],  # Query 2
        [0.9, 0.8, ...]   # Query 3
    ],
    n_results=5
)

# Returns nested lists
results['ids']  # [[results for q1], [results for q2], [results for q3]]
```

### Custom Distance Functions
```python
# L2 (Euclidean) distance (default)
collection = client.get_or_create_collection(
    name="my_docs",
    metadata={"hnsw:space": "l2"}
)

# Cosine similarity
collection = client.get_or_create_collection(
    name="my_docs",
    metadata={"hnsw:space": "cosine"}
)

# Inner product
collection = client.get_or_create_collection(
    name="my_docs",
    metadata={"hnsw:space": "ip"}
)
```

**Recommended:** Use "cosine" with normalized embeddings (default for sentence-transformers)

### Index Configuration (HNSW)
```python
collection = client.get_or_create_collection(
    name="my_docs",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200,  # Build quality (higher = better, slower)
        "hnsw:search_ef": 50,         # Search quality (higher = better, slower)
        "hnsw:M": 16                   # Connections per node (16-64 typical)
    }
)
```

**Guidelines:**
- Default settings work well for most use cases
- Increase `construction_ef` for better quality (slower indexing)
- Increase `search_ef` for better recall (slower search)
- `M=16`: good default, `M=64`: high quality/memory

## Performance Optimization

### Batch Size
```python
# Add documents in batches
batch_size = 1000
for i in range(0, len(all_ids), batch_size):
    batch_ids = all_ids[i:i+batch_size]
    batch_embeddings = all_embeddings[i:i+batch_size]
    batch_docs = all_documents[i:i+batch_size]
    batch_meta = all_metadatas[i:i+batch_size]
    
    collection.add(
        ids=batch_ids,
        embeddings=batch_embeddings,
        documents=batch_docs,
        metadatas=batch_meta
    )
```

### Transaction Batching
ChromaDB automatically batches operations internally, but explicit batching helps with:
- Memory management
- Error handling
- Progress tracking

### Query Optimization
```python
# Pre-filter with metadata (faster)
results = collection.query(
    query_embeddings=query_emb,
    n_results=20,
    where={"filename": {"$eq": "specific.pdf"}}  # Reduces search space
)

# Post-filter with document content (slower)
results = collection.query(
    query_embeddings=query_emb,
    n_results=100,  # Get more candidates
    where_document={"$contains": "keyword"}  # Scans all results
)
```

**Rule:** Use metadata filtering (`where`) over document filtering (`where_document`) when possible

## Common Patterns

### RAG Pattern (Our Pipeline)
```python
# 1. Index
collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadata)

# 2. Retrieve candidates
candidates = collection.query(query_embeddings=q_emb, n_results=20)

# 3. Rerank externally (cross-encoder)
reranked = rerank(query, candidates['documents'][0])

# 4. Return top-k
return reranked[:5]
```

### Multi-tenancy Pattern
```python
# One collection per user/tenant
collection = client.get_or_create_collection(name=f"user_{user_id}_docs")

# Or use metadata filtering
collection.add(
    ids=ids,
    embeddings=embeddings,
    metadatas=[{"user_id": user_id} for _ in ids]
)

results = collection.query(
    query_embeddings=q_emb,
    where={"user_id": user_id}
)
```

### Versioned Documents
```python
# Add version to metadata
collection.add(
    ids=[f"doc1_v{version}"],
    embeddings=embeddings,
    metadatas=[{"doc_id": "doc1", "version": version, "is_latest": True}]
)

# Update old version
collection.update(
    ids=[f"doc1_v{old_version}"],
    metadatas=[{"is_latest": False}]
)

# Query latest only
results = collection.query(
    query_embeddings=q_emb,
    where={"is_latest": True}
)
```

## Error Handling

### Common Errors
```python
# Collection not found
try:
    collection = client.get_collection("nonexistent")
except ValueError as e:
    print(f"Collection not found: {e}")

# Duplicate ID
try:
    collection.add(ids=["doc1"], embeddings=[[...]])
    collection.add(ids=["doc1"], embeddings=[[...]])  # Error!
except Exception as e:
    print(f"Duplicate ID: {e}")
    # Use upsert() or update() instead

# Dimension mismatch
try:
    collection.add(
        ids=["doc1"],
        embeddings=[[0.1, 0.2]]  # 2 dimensions
    )
    collection.add(
        ids=["doc2"],
        embeddings=[[0.1, 0.2, 0.3]]  # 3 dimensions - Error!
    )
except Exception as e:
    print(f"Dimension mismatch: {e}")
```

### Safe Operations
```python
# Check collection exists
if collection_name in [c.name for c in client.list_collections()]:
    collection = client.get_collection(collection_name)
else:
    collection = client.create_collection(collection_name)

# Validate embeddings dimension
expected_dim = 768
if len(embedding) != expected_dim:
    raise ValueError(f"Expected {expected_dim} dimensions, got {len(embedding)}")
```
