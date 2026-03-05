import os
import time
import statistics
import json
import re
from secrets_loader import get_google_api_key

# LangChain Imports
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

# Configuration
os.environ["GOOGLE_API_KEY"] = get_google_api_key()
GT_FILE = "/root/.openclaw/workspace/RAG_GROUND_TRUTH.json"

class RAGEvaluator:
    def __init__(self):
        print("DEBUG: Initializing HYBRID RAGEvaluator...")
        self.results = []
        self.latencies = []
        
        # Setup RAG Pipeline
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        persist_directory = "/root/.openclaw/workspace/chroma_db_semantic_v3"
        
        try:
            from langchain_chroma import Chroma
        except ImportError:
            from langchain_community.vectorstores import Chroma
            
        self.vectorstore = Chroma(persist_directory=persist_directory, embedding_function=self.embeddings)
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0, convert_system_message_to_human=True)
        self.judge_llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0)

        # Updated Prompt for cleaner answers
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a helpful assistant. Use the following context to answer the question.
            If the answer is not in the context, say "The context does not mention this."
            
            Context:
            {context}
            
            Question: {input}
            """)
        ])
        
        self.document_chain = create_stuff_documents_chain(self.llm, prompt)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 20})

        # Load Ground Truth Data
        with open(GT_FILE, 'r') as f:
            self.ground_truth = json.load(f)
        print("DEBUG: RAGEvaluator initialized.")

    def calculate_semantic_similarity(self, text1, text2):
        """Calculates cosine similarity between two texts."""
        if not text1 or not text2:
            return 0.0
        try:
            embeddings = self.embeddings.embed_documents([text1, text2])
            sim = sum(e1 * e2 for e1, e2 in zip(embeddings[0], embeddings[1]))
            return sim
        except Exception as e:
            print(f"⚠️ Semantic Similarity Failed: {e}")
            return 0.0

    def evaluate_query(self, gt_entry):
        query = gt_entry['query']
        time.sleep(2)  # Rate Limit Protection
        print(f"\n🧪 Testing: '{query[:60]}...'")
        start_time = time.time()
        
        # 1. Manual Pipeline Execution (Fixed Dictionary Error)
        retrieved_docs = self.retriever.invoke(query)
        answer = self.document_chain.invoke({
            "input": query,
            "context": retrieved_docs
        })
        
        end_time = time.time()
        latency = end_time - start_time
        
        # 2. Hybrid Evaluation Logic
        gt_answer = gt_entry.get('ground_truth_answer', '')
        sem_sim = self.calculate_semantic_similarity(answer, gt_answer)
        
        # LLM Judge with JSON output for robust parsing
        judge_score, reasoning = self.run_advanced_judge(query, answer, gt_answer)
        
        # HYBRID SCORE: Balances word overlap (Vector) with Logical intent (Judge)
        hybrid_correctness = (sem_sim * 0.4) + (judge_score * 0.6)
        
        # Context Precision Calculation
        retrieved_ids = {doc.metadata.get('id') for doc in retrieved_docs if doc.metadata.get('id')}
        truth_ids = set(gt_entry.get('ground_truth_chunk_ids', [])) 
        
        if truth_ids:
            relevant_retrieved = len(retrieved_ids.intersection(truth_ids))
            context_precision = relevant_retrieved / len(retrieved_ids) if len(retrieved_ids) > 0 else 0.0
        else:
            context_precision = 1.0
        
        self.results.append({
            "query": query,
            "answer": answer,
            "latency": latency,
            "sem_sim": sem_sim,
            "judge_score": judge_score,
            "hybrid": hybrid_correctness,
            "context_precision": context_precision,
            "reasoning": reasoning
        })
        self.latencies.append(latency)
        
        print(f"   ⏱️ Latency: {latency:.2f}s")
        print(f"   ⭐ Semantic Similarity: {sem_sim:.3f}")
        print(f"   ⚖️ LLM Judge Score:     {judge_score:.2f}")
        print(f"   📝 Judge Reasoning:     {reasoning}")
        print(f"   🚀 HYBRID CORRECTNESS:  {hybrid_correctness*100:.1f}%")
        return self.results[-1]

    def run_advanced_judge(self, query, answer, gt):
        """Refined Judge using JSON output."""
        prompt = f"""
        Role: Expert Fact-Checker
        Task: Compare the Generated Answer to the Ground Truth logically.
        
        Query: {query}
        Generated Answer: {answer}
        Ground Truth Answer: {gt}
        
        Criteria:
        - Score 1.0 if they share the same meaning/facts.
        - Score 0.0 if they contradict or the fact is wrong.
        - Partial credit (0.1-0.9) if some facts are correct but incomplete.
        
        Return JSON ONLY: {{"score": float, "reasoning": "one sentence explanation"}}
        """
        try:
            response = self.judge_llm.invoke(prompt).content
            # Clean JSON formatting
            clean_res = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_res)
            return float(data.get("score", 0.0)), data.get("reasoning", "N/A")
        except Exception as e:
            return 0.0, f"Judge/Parsing Error: {str(e)}"

    def print_summary(self):
        if not self.results: return
        count = len(self.results)
        avg_latency = statistics.mean(self.latencies)
        
        print(f"\n========================================")
        print(f"📊 **RAG HYBRID CORRELATION REPORT**")
        print(f"========================================")
        print(f"Queries Run:      {count}")
        print(f"Avg Latency:      {avg_latency:.2f}s")
        print(f"\n--- CORE QUALITY METRICS ---")
        print(f"1. Avg Semantic Sim:     {statistics.mean(r['sem_sim'] for r in self.results):.3f}")
        print(f"2. Avg LLM Judge Score:  {statistics.mean(r['judge_score'] for r in self.results):.2f}")
        print(f"3. HYBRID CORRECTNESS:   {statistics.mean(r['hybrid'] for r in self.results)*100:.1f}%")
        print(f"4. Avg Context Precision: {statistics.mean(r['context_precision'] for r in self.results)*100:.1f}%")
        print(f"========================================")

def main():
    if not os.path.exists(GT_FILE):
        print(f"FATAL: Ground Truth file not found at {GT_FILE}")
        return
        
    evaluator = RAGEvaluator()
    print("🚀 Starting RAG HYBRID Evaluation (Similarity + Logical Correlation)...")
    for gt_entry in evaluator.ground_truth:
        evaluator.evaluate_query(gt_entry)
        
    evaluator.print_summary()

if __name__ == "__main__":
    main()
