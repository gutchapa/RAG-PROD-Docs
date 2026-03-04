# RAG Evaluation Metrics

The system tracks these 9 key metrics to ensure high quality retrieval and generation.

## 1. Faithfulness (Groundedness)
**Definition:** Measures if the generated answer is derived *only* from the retrieved context.
- **Goal:** Minimize hallucinations.
- **Target:** > 0.90
- **Implementation:** LLM-based check (Answer vs Context).

## 2. Answer Relevance
**Definition:** Measures how pertinent the generated answer is to the user's question.
- **Goal:** Direct, actionable answers.
- **Target:** > 0.85
- **Implementation:** LLM-based check (Answer vs Question).

## 3. Context Precision
**Definition:** Evaluates if the *relevant* chunks are ranked highly in the retrieval list.
- **Goal:** Top result should be the answer.
- **Target:** > 0.80 (Mean Average Precision @ K).
- **Implementation:** Needs Ground Truth (chunk IDs).

## 4. Context Recall
**Definition:** Measures if the retrieved context contains *all* the information needed to answer the question.
- **Goal:** Retrieve 100% of the facts.
- **Target:** > 0.90
- **Implementation:** Needs Ground Truth (facts).

## 5. Context Relevancy
**Definition:** Measures the signal-to-noise ratio in the retrieved context. Ideally, retrieved text contains *only* relevant info.
- **Goal:** Minimize irrelevant text to save tokens/cost.
- **Target:** > 0.70
- **Implementation:** LLM-based (Relevant Sentences / Total Sentences).

## 6. Answer Correctness (Factual Accuracy)
**Definition:** Measures the factual accuracy of the generated answer against a ground truth answer.
- **Goal:** 100% accuracy.
- **Target:** > 0.95
- **Implementation:** LLM-based comparison (Generated vs Ground Truth).

## 7. Answer Semantic Similarity
**Definition:** Measures the vector similarity between the generated answer and the ground truth answer.
- **Goal:** High semantic overlap (even if phrasing differs).
- **Target:** > 0.85 (Cosine Similarity).
- **Implementation:** Embedding model comparison.

## 8. Cost (Efficiency)
**Definition:** Total token usage (Input + Output) converted to estimated USD.
- **Goal:** Minimize cost per query while maintaining quality.
- **Target:** < $0.01 per query.
- **Implementation:** Token counting (Input + Output * Pricing).

## 9. Latency (Performance)
**Definition:** Total time taken for Retrieval + Generation.
- **Goal:** Fast user experience.
- **Target:** < 3 seconds (p95).
- **Implementation:** Python `time.time()`.
