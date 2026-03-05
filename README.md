# RAG Project Documentation

This repository contains the Retrieval-Augmented Generation (RAG) prototype developed for testing the performance and cost efficiency of local LLMs against a proprietary transcript dataset.

## 1. RAG Stack
*   **Orchestration:** LangChain
*   **Vector Store:** ChromaDB (Persistence directory: `./chroma_db_semantic_v3`)
*   **Embedding Model:** `models/gemini-embedding-001`
*   **LLM:** `models/gemini-2.0-flash`

## 2. Data Source
*   **Corpus:** `/root/.openclaw/workspace/downloads/clean_transcript.txt`
*   **Ground Truth:** `/root/.openclaw/workspace/RAG_GROUND_TRUTH.json`

## 3. Evaluation Methodology
The system was evaluated using a custom **LLM-as-a-Judge** approach across 9 metrics.

### Chunking Strategy (Current Stable)
*   **Strategy:** Recursive Character Text Splitting
*   **Size/Overlap:** 500 characters / 50 overlap.

### Metrics Summary (Last Successful Run)
| Metric | Result | Notes |
|---|---|---|
| Faithfulness | 100.0% | Answer derived purely from context. |
| Answer Relevance | 66.7% | Moderate relevance due to context size/chunking. |
| Context Precision | 0.67 / 1.0 | Only 67% of retrieved chunks were relevant to the ground truth ID set. |
| Context Relevancy | 0.82 / 1.0 | Good signal-to-noise ratio in retrieved context. |

## 4. Production Roadmap (Currently Blocked)
The evaluation suite was intended to be upgraded to use **Ragas** for standardized metrics and **Langfuse** for tracing. This upgrade is blocked by dependency conflicts between LangChain versions required by Ragas and the current environment setup.

**Action Required to Unblock:** Resolve LangChain versioning conflicts within the `rag_env` virtual environment.