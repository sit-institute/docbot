# Model Comparison and Benchmarks

Performance benchmarks and comparison of embedding and reranking models.

## Embedding Models

### Overview

| Model | Dimensions | Speed (GPU) | Quality | Use Case |
|-------|-----------|-------------|---------|----------|
| all-MiniLM-L6-v2 | 384 | 20-50ms/chunk | Good | Fast retrieval, resource-constrained |
| BAAI/bge-base-en-v1.5 | 768 | 50-100ms/chunk | Excellent | Balanced quality/speed (recommended) |
| BAAI/bge-large-en-v1.5 | 1024 | 100-200ms/chunk | Best | Maximum quality |
| nomic-embed-text | 768 | 60-120ms/chunk | Excellent | Long context (8k tokens) |
| text-embedding-3-small | 1536 | API-only | Excellent | OpenAI API alternative |

### Detailed Specifications

#### all-MiniLM-L6-v2
- **Parameters**: 22M
- **Max Sequence Length**: 256 tokens
- **MTEB Score**: 56.3
- **Pros**: Extremely fast, small memory footprint, good for CPU
- **Cons**: Lower quality than larger models, shorter context
- **Best for**: Prototyping, CPU-only environments, speed-critical apps

#### BAAI/bge-base-en-v1.5 (Recommended)
- **Parameters**: 109M
- **Max Sequence Length**: 512 tokens
- **MTEB Score**: 63.1
- **Pros**: Excellent quality/speed tradeoff, widely adopted
- **Cons**: None significant
- **Best for**: Production RAG systems, general-purpose retrieval

#### BAAI/bge-large-en-v1.5
- **Parameters**: 335M
- **Max Sequence Length**: 512 tokens
- **MTEB Score**: 64.2
- **Pros**: Highest quality retrieval
- **Cons**: Slower, higher memory usage
- **Best for**: Quality-critical applications, offline batch processing

#### nomic-embed-text
- **Parameters**: 137M
- **Max Sequence Length**: 8192 tokens
- **MTEB Score**: 62.4
- **Pros**: Very long context support, competitive quality
- **Cons**: Slower than bge-base
- **Best for**: Long documents, full-chapter retrieval

### Performance Benchmarks (RTX 3080)

**Batch Size: 32 chunks**

| Model | Time/Batch | Throughput | VRAM Usage |
|-------|-----------|------------|------------|
| all-MiniLM-L6-v2 | 640ms | 50 chunks/s | 1.2 GB |
| bge-base-en-v1.5 | 1.6s | 20 chunks/s | 2.8 GB |
| bge-large-en-v1.5 | 3.2s | 10 chunks/s | 4.5 GB |
| nomic-embed-text | 1.9s | 17 chunks/s | 3.1 GB |

**Single Document Indexing (100 chunks):**
- all-MiniLM-L6-v2: ~2s
- bge-base-en-v1.5: ~5s
- bge-large-en-v1.5: ~10s
- nomic-embed-text: ~6s

## Reranker Models

### Overview

| Model | Parameters | Speed (GPU) | Quality | Use Case |
|-------|-----------|-------------|---------|----------|
| bge-reranker-base | 278M | 200ms/100 pairs | Good | Fast reranking |
| bge-reranker-v2-m3 | 560M | 400ms/100 pairs | Excellent | Multilingual (recommended) |
| bge-reranker-large | 560M | 500ms/100 pairs | Best | Maximum quality |
| ms-marco-MiniLM-L6-v2 | 22M | 100ms/100 pairs | Fair | Legacy, fast |

### Detailed Specifications

#### BAAI/bge-reranker-base
- **Architecture**: Cross-encoder (BERT-based)
- **Max Sequence Length**: 512 tokens
- **Training**: MS MARCO, NQ, Trivia QA
- **Pros**: Fast, efficient, good quality
- **Cons**: English-only
- **Best for**: English documents, speed-critical reranking

#### BAAI/bge-reranker-v2-m3 (Recommended)
- **Architecture**: Cross-encoder (XLM-RoBERTa)
- **Max Sequence Length**: 512 tokens
- **Languages**: 100+ languages
- **Training**: Multilingual datasets
- **Pros**: Excellent quality, multilingual support
- **Cons**: Slower than base model
- **Best for**: Production systems, multilingual content

#### BAAI/bge-reranker-large
- **Architecture**: Large cross-encoder
- **Max Sequence Length**: 512 tokens
- **Training**: Extended MS MARCO
- **Pros**: Highest quality reranking
- **Cons**: Slowest, highest VRAM
- **Best for**: Offline processing, maximum accuracy needed

### Performance Benchmarks (RTX 3080)

**Reranking 20 candidates:**

| Model | Time | VRAM Usage | Quality Gain |
|-------|------|------------|--------------|
| bge-reranker-base | 200ms | 1.8 GB | +15% NDCG@10 |
| bge-reranker-v2-m3 | 400ms | 3.2 GB | +22% NDCG@10 |
| bge-reranker-large | 500ms | 3.5 GB | +25% NDCG@10 |

**Quality Metrics (MS MARCO Dev):**
- bge-reranker-base: MRR@10: 0.343
- bge-reranker-v2-m3: MRR@10: 0.378
- bge-reranker-large: MRR@10: 0.392

## Two-Stage Retrieval Performance

**Complete pipeline latency (RTX 3080):**

**Configuration:**
- Collection size: 10,000 chunks
- Retrieve: top-20 candidates
- Rerank: to top-5
- Model: bge-base-en-v1.5 + bge-reranker-v2-m3

**Breakdown:**
1. Query embedding: 10ms
2. Vector search: 20-50ms
3. Reranking (20→5): 400ms
4. **Total**: 430-460ms

**Comparison without reranking:**
- Vector search only: 30-60ms
- Quality: -22% NDCG@5

**Trade-off analysis:**
- 7-15x slower than vector-only
- +22% quality improvement
- Still <500ms (acceptable for most use cases)

## Model Selection Guidelines

### For Speed-Critical Applications
- **Embedding**: all-MiniLM-L6-v2
- **Reranker**: bge-reranker-base or skip reranking
- **Latency**: <200ms
- **Quality**: Acceptable for most queries

### For Balanced Production (Recommended)
- **Embedding**: BAAI/bge-base-en-v1.5
- **Reranker**: BAAI/bge-reranker-v2-m3
- **Latency**: 400-600ms
- **Quality**: Excellent

### For Maximum Quality
- **Embedding**: BAAI/bge-large-en-v1.5
- **Reranker**: BAAI/bge-reranker-large
- **Latency**: 700-1000ms
- **Quality**: Best possible

### For Long Documents
- **Embedding**: nomic-embed-text
- **Reranker**: bge-reranker-v2-m3
- **Latency**: 500-700ms
- **Quality**: Excellent with long context

### For Multilingual Content
- **Embedding**: bge-m3 (not included in default, requires separate install)
- **Reranker**: bge-reranker-v2-m3
- **Latency**: 500-700ms
- **Quality**: Excellent across languages

## Optimization Tips

### Batch Size Tuning
- **GPU Memory**: Increase batch_size until GPU memory is 80% full
- **RTX 3080 (10GB)**: batch_size=32-64 for bge-base
- **RTX 4090 (24GB)**: batch_size=128-256 for bge-base

### Mixed Precision (FP16)
```python
# In embedding/reranking scripts
embedder = SentenceTransformer(model, device='cuda')
embedder.half()  # Use FP16 for 2x speed
```
- **Speed gain**: ~2x
- **Quality loss**: Minimal (<1%)
- **VRAM savings**: 50%

### Multi-GPU
```python
embeddings = embedder.encode(
    texts,
    device=["cuda:0", "cuda:1"]
)
```
- Automatically distributes workload
- Near-linear scaling for large batches

### Model Caching
- Models downloaded to: `~/.cache/torch/sentence_transformers/`
- First run downloads models (~500MB-2GB per model)
- Subsequent runs load from cache (fast)

## Benchmark Reproduction

To reproduce benchmarks on your hardware:

```bash
# Install additional tools
pip install mteb datasets --break-system-packages

# Run MTEB evaluation (slow, ~1-2 hours)
python -c "
from mteb import MTEB
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-base-en-v1.5')
evaluation = MTEB(tasks=['NFCorpus'])
results = evaluation.run(model)
print(results)
"
```
