import os
import time
import statistics
import json
from secrets_loader import get_google_api_key

# LangChain Imports
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter # Changed Splitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

# Configuration
os.environ["GOOGLE_API_KEY"] = get_google_api_key()
COST_PER_1M_INPUT = 0.35
COST_PER_1M_OUTPUT = 0.70
GT_FILE = "/root/.openclaw/workspace/RAG_GROUND_TRUTH.json"

class RAGEvaluator:
    def __init__(self):
        self.results = []
        self.latencies = []
        
        # Setup RAG Pipeline
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        persist_directory = "./chroma_db_semantic_v3"
        
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print("✅ Loading existing vector store...")
            self.vectorstore = Chroma(persist_directory=persist_directory, embedding_function=self.embeddings)
        else:
            print("⚠️ Recreating vector store (one-time setup)...")
            loader = TextLoader("/root/.openclaw/workspace/downloads/clean_transcript.txt")
            docs = loader.load()
            # TUNE: Switched to fixed-size chunking (500 chars, 50 overlap) to improve signal-to-noise (Relevancy)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = text_splitter.split_documents(docs)
            
            # ADDING METADATA FOR PRECISION/RECALL CALCULATION
            indexed_splits = []
            for i, doc in enumerate(splits):
                doc.metadata['id'] = f"chunk_idx_{i}"
                indexed_splits.append(doc)
                
            self.vectorstore = Chroma.from_documents(documents=indexed_splits, embedding=self.embeddings, persist_directory=persist_directory)

        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0, convert_system_message_to_human=True)
        self.judge_llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0) # Judge

        # RAG Chain
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a helpful assistant. Use the following context to answer the question.
            If the answer is not in the context, say "The context does not mention this."
            
            Context:
            {context}
            
            Question: {input}
            """)
        ])
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 20}) # Enhanced recall
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Load Ground Truth Data
        with open(GT_FILE, 'r') as f:
            self.ground_truth = json.load(f)

    def calculate_semantic_similarity(self, text1, text2):
        """Calculates cosine similarity between two texts using the configured embeddings."""
        if not text1 or not text2:
            return 0.0
        try:
            embeddings = self.embeddings.embed_documents([text1, text2])
            # Simple dot product for normalized embeddings = cosine similarity
            sim = sum(e1 * e2 for e1, e2 in zip(embeddings[0], embeddings[1]))
            return sim
        except Exception as e:
            print(f"⚠️ Semantic Similarity Failed: {e}")
            return 0.0

    def evaluate_query(self, gt_entry):
        query = gt_entry['query']
        time.sleep(2)  # Rate Limit Protection
        print(f"\n🧪 Testing: '{query}'")
        start_time = time.time()
        
        # 1. Run RAG
        result = self.retrieval_chain.invoke({"input": query})
        end_time = time.time()
        latency = end_time - start_time
        
        answer = result['answer']
        retrieved_docs = result['context']
        retrieved_content = "\n".join([doc.page_content for doc in retrieved_docs])
        
        # --- METRIC CALCULATION (LLM-as-a-Judge) ---
        scores = self.run_judge(query, answer, retrieved_content)
        
        # --- METRIC CALCULATION (Semantic/Correctness) ---
        gt_answer = gt_entry.get('ground_truth_answer', '')
        semantic_similarity = self.calculate_semantic_similarity(answer, gt_answer)
        
        # --- METRIC CALCULATION (Context Metrics) ---
        context_recall_proxy = scores['recall'] 
        
        # Context Precision: How much of retrieved context is relevant? 
        retrieved_ids = {doc.metadata.get('id') for doc in retrieved_docs if doc.metadata.get('id')}
        truth_ids = set(gt_entry.get('ground_truth_chunk_ids', [])) 
        
        if truth_ids:
            relevant_retrieved = len(retrieved_ids.intersection(truth_ids))
            context_precision = relevant_retrieved / len(retrieved_ids) if len(retrieved_ids) > 0 else 1.0
        else:
            context_precision = 1.0
        
        # Answer Correctness: Is the answer factually correct vs ground truth?
        answer_correctness = self.judge_answer_correctness(query, answer, gt_answer)

        # --- METRIC 9: Context Relevancy ---
        context_relevancy = self.judge_context_relevancy(query, retrieved_content)

        # 3. Calculate Cost
        input_tokens = len(query + retrieved_content) / 4 # Est.
        output_tokens = len(answer) / 4 # Est.
        cost = (input_tokens/1e6 * COST_PER_1M_INPUT) + (output_tokens/1e6 * COST_PER_1M_OUTPUT)
        
        self.results.append({
            "query": query,
            "answer": answer,
            "latency": latency,
            # LLM Judge Metrics (3)
            "faithfulness": scores['faithfulness'],
            "relevance": scores['relevance'],
            "context_recall_proxy": context_recall_proxy,
            # Semantic/Correctness Metrics (3)
            "answer_correctness": answer_correctness,
            "semantic_similarity": semantic_similarity,
            # Context Metrics (2)
            "context_precision": context_precision,
            "context_relevancy": context_relevancy,
            # Efficiency Metrics (2)
            "cost": cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        })
        self.latencies.append(latency)
        
        print(f"   ⏱️ Latency: {latency:.2f}s")
        print(f"   💰 Cost: ${cost:.6f}")
        print(f"   ✅ Faithfulness: {scores['faithfulness']}/1")
        print(f"   🎯 Relevance: {scores['relevance']}/1")
        print(f"   ➗ Context Precision: {context_precision:.2f}/1")
        print(f"   ⭐ Semantic Sim: {semantic_similarity:.3f}/1")
        print(f"   💯 Correctness: {answer_correctness:.2f}/1")
        print(f"   💡 Context Relevancy: {context_relevancy:.2f}/1")
        return self.results[-1]

    def run_judge(self, query, answer, context):
        # Judge Prompt for Faithfulness, Relevance, Recall Proxy
        judge_prompt = f"""
        You are an AI Evaluator. Evaluate the following RAG interaction.
        
        Query: {query}
        Context Snippet (First 4000 chars): {context[:4000]}...
        Answer: {answer}
        
        Return a JSON object with 3 keys (0 or 1):
        - "faithfulness": 1 if the answer is derived purely from context, 0 if hallucinated.
        - "relevance": 1 if the answer directly addresses the query, 0 if irrelevant.
        - "recall": 1 if the context snippet appears to contain the information needed to answer the query, 0 if context was clearly missing info.
        
        JSON only:
        """
        try:
            response = self.judge_llm.invoke(judge_prompt, config=RunnableConfig(configurable={"system_instruction": "You are a concise JSON evaluation engine."}))
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ Judge Failed (3-Metric): {e}")
            return {"faithfulness": 0, "relevance": 0, "recall": 0}
            
    def judge_answer_correctness(self, query, answer, gt_answer):
        """LLM-as-a-Judge to compare generated answer vs ground truth answer."""
        judge_prompt = f"""
        Compare the 'Generated Answer' to the 'Ground Truth Answer' based on the 'Query'.
        
        Query: {query}
        Generated Answer: {answer}
        Ground Truth Answer: {gt_answer}
        
        Score the 'Generated Answer' on a scale of 0 to 1 based on factual correctness and thematic alignment with the 'Ground Truth Answer'. Do not penalize for different but correct phrasing.
        
        Return only the float score. Do not include any text, JSON, or explanation.
        """
        try:
            response = self.judge_llm.invoke(judge_prompt, config=RunnableConfig(configurable={"system_instruction": "You are a concise float output engine."}))
            content = response.content.strip()
            return float(content)
        except Exception as e:
            print(f"⚠️ Judge Failed (Correctness): {e}")
            return 0.0

    def judge_context_relevancy(self, query, context):
        """LLM-as-a-Judge to score context relevancy (Signal-to-Noise)."""
        judge_prompt = f"""
        Context: {context[:4000]}...
        Query: {query}
        
        Score the provided Context on a scale of 0.0 (pure noise) to 1.0 (every sentence is highly relevant to the Query).
        
        Return only the float score. Do not include any text, JSON, or explanation.
        """
        try:
            response = self.judge_llm.invoke(judge_prompt, config=RunnableConfig(configurable={"system_instruction": "You are a concise float output engine."}))
            content = response.content.strip()
            return float(content)
        except Exception as e:
            print(f"⚠️ Judge Failed (Relevancy): {e}")
            return 0.0

    def print_summary(self):
        if not self.results: return
        
        count = len(self.results)
        avg_latency = statistics.mean(self.latencies)
        p50 = statistics.median(self.latencies)
        p95 = sorted(self.latencies)[int(len(self.latencies) * 0.95)] if len(self.latencies) > 1 else self.latencies[0]
        
        total_cost = sum(r['cost'] for r in self.results)
        
        # Aggregated Metrics (Total 9)
        avg_faithfulness = statistics.mean(r['faithfulness'] for r in self.results)
        avg_relevance = statistics.mean(r['relevance'] for r in self.results)
        avg_context_precision = statistics.mean(r['context_precision'] for r in self.results)
        avg_context_recall_proxy = statistics.mean(r['context_recall_proxy'] for r in self.results)
        avg_answer_correctness = statistics.mean(r['answer_correctness'] for r in self.results)
        avg_semantic_similarity = statistics.mean(r['semantic_similarity'] for r in self.results)
        avg_context_relevancy = statistics.mean(r['context_relevancy'] for r in self.results)

        print(f"\n========================================")
        print(f"📊 **RAG Comprehensive Performance Report**")
        print(f"========================================")
        print(f"Queries Run:      {count}")
        print(f"Total Cost:       ${total_cost:.6f}")
        print(f"\n--- PERFORMANCE ---")
        print(f"Latency (Avg):    {avg_latency:.2f}s")
        print(f"Latency (P95):    {p95:.2f}s")
        print(f"\n--- QUALITY ---")
        print(f"1. Faithfulness:         {avg_faithfulness*100:.1f}%")
        print(f"2. Answer Relevance:     {avg_relevance*100:.1f}%")
        print(f"3. Context Precision:    {avg_context_precision*100:.1f}%")
        print(f"4. Context Recall Proxy: {avg_context_recall_proxy*100:.1f}%")
        print(f"5. Answer Correctness:   {avg_answer_correctness*100:.1f}%")
        print(f"6. Semantic Similarity:  {avg_semantic_similarity:.3f} (Max 1.0)")
        print(f"9. Context Relevancy:    {avg_context_relevancy*100:.1f}%")
        print(f"\n--- EFFICIENCY ---")
        print(f"7. Latency (Avg):        {avg_latency:.2f}s")
        print(f"8. Cost:                 ${total_cost:.6f}")
        print(f"========================================")


def main():
    # Ensure the ground truth file exists before loading
    if not os.path.exists(GT_FILE):
        print(f"FATAL: Ground Truth file not found at {GT_FILE}. Cannot run full evaluation.")
        return
        
    evaluator = RAGEvaluator()
    
    print("🚀 Starting RAG Evaluation Suite (Full 9 Metrics Mode)...")
    for gt_entry in evaluator.ground_truth:
        evaluator.evaluate_query(gt_entry)
        
    evaluator.print_summary()

if __name__ == "__main__":
    main()