import os
import time
import statistics
import json
from secrets_loader import get_google_api_key

# LangChain Imports - Updated for your environment
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
import shutil
import langfuse
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, AnswerCorrectness, ContextPrecision

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
        print("DEBUG: Initializing RAGEvaluator...")
        self.results = []
        self.latencies = []
        
        # Setup RAG Pipeline
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        persist_directory = "/root/.openclaw/workspace/chroma_db_semantic_v3"
        
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print("✅ Loading existing vector store...")
            self.vectorstore = Chroma(persist_directory=persist_directory, embedding_function=self.embeddings)
        else:
            print("⚠️ Recreating vector store (one-time setup)...")
            loader = TextLoader("/root/.openclaw/workspace/downloads/clean_transcript.txt")
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = text_splitter.split_documents(docs)
            
            indexed_splits = []
            for i, doc in enumerate(splits):
                doc.metadata['id'] = f"chunk_idx_{i}"
                indexed_splits.append(doc)
                
            self.vectorstore = Chroma.from_documents(documents=indexed_splits, embedding=self.embeddings, persist_directory=persist_directory)

        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0, convert_system_message_to_human=True)
        self.judge_llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0)

        # RAG Chain
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a helpful assistant. Use the following context to answer the question.
            If the answer is not in the context, say "The context does not mention this."
            
            Context:
            {context}
            
            Question: {input}
            """)
        ])
        
        # Use simple document chain
        self.document_chain = create_stuff_documents_chain(self.llm, prompt)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 20})

        # Load Ground Truth Data
        with open(GT_FILE, 'r') as f:
            self.ground_truth = json.load(f)
        print("DEBUG: RAGEvaluator initialized.")

    def calculate_semantic_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
        try:
            embeddings = self.embeddings.embed_documents([text1, text2])
            sim = sum(e1 * e2 for e1, e2 in zip(embeddings[0], embeddings[1]))
            return sim
        except Exception as e:
            print(f"⚠️ Semantic Similarity Failed: {e}")
            return 0.0

    def evaluate_query(self, gt_entry, run_config=None):
        query = gt_entry['query']
        time.sleep(2)
        print(f"\n🧪 Testing: '{query}'")
        start_time = time.time()
        
        print("DEBUG: Step 1 - Retrieving documents...")
        # CRITICAL: Passing string directly to retriever to avoid dictionary errors
        retrieved_docs = self.retriever.invoke(query)
        retrieved_content = "\n".join([doc.page_content for doc in retrieved_docs])
        print(f"DEBUG: Step 1 complete. Retrieved {len(retrieved_docs)} docs.")
        
        print("DEBUG: Step 2 - Generating answer...")
        # CRITICAL: Passing correct dictionary to document chain
        answer = self.document_chain.invoke({
            "input": query,
            "context": retrieved_docs
        }, config=run_config)
        print("DEBUG: Step 2 complete.")
        
        end_time = time.time()
        latency = end_time - start_time
        
        print("DEBUG: Step 3 - Running judge metrics...")
        scores = self.run_judge(query, answer, retrieved_content, run_config)
        print("DEBUG: Step 3 complete.")
        
        gt_answer = gt_entry.get('ground_truth_answer', '')
        semantic_similarity = self.calculate_semantic_similarity(answer, gt_answer)
        
        context_recall_proxy = scores['recall'] 
        retrieved_ids = {doc.metadata.get('id') for doc in retrieved_docs if doc.metadata.get('id')}
        truth_ids = set(gt_entry.get('ground_truth_chunk_ids', [])) 
        
        if truth_ids:
            relevant_retrieved = len(retrieved_ids.intersection(truth_ids))
            context_precision = relevant_retrieved / len(retrieved_ids) if len(retrieved_ids) > 0 else 1.0
        else:
            context_precision = 1.0
        
        answer_correctness = self.judge_answer_correctness(query, answer, gt_answer, run_config)
        context_relevancy = self.judge_context_relevancy(query, retrieved_content, run_config)

        input_tokens = len(query + retrieved_content) / 4
        output_tokens = len(answer) / 4
        cost = (input_tokens/1e6 * COST_PER_1M_INPUT) + (output_tokens/1e6 * COST_PER_1M_OUTPUT)
        
        self.results.append({
            "query": query,
            "answer": answer,
            "latency": latency,
            "faithfulness": scores['faithfulness'],
            "relevance": scores['relevance'],
            "context_recall_proxy": context_recall_proxy,
            "answer_correctness": answer_correctness,
            "semantic_similarity": semantic_similarity,
            "context_precision": context_precision,
            "context_relevancy": context_relevancy,
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

    def run_judge(self, query, answer, context, run_config=None):
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
            response = self.judge_llm.invoke(judge_prompt, config=run_config)
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ Judge Failed (3-Metric): {e}")
            return {"faithfulness": 0, "relevance": 0, "recall": 0}
            
    def judge_answer_correctness(self, query, answer, gt_answer, run_config=None):
        judge_prompt = f"""
        Compare the 'Generated Answer' to the 'Ground Truth Answer' based on the 'Query'.
        
        Query: {query}
        Generated Answer: {answer}
        Ground Truth Answer: {gt_answer}
        
        Score the 'Generated Answer' on a scale of 0 to 1 based on factual correctness and thematic alignment with the 'Ground Truth Answer'. Do not penalize for different but correct phrasing.
        
        Return only the float score. Do not include any text, JSON, or explanation.
        """
        try:
            response = self.judge_llm.invoke(judge_prompt, config=run_config)
            content = response.content.strip()
            return float(content)
        except Exception as e:
            print(f"⚠️ Judge Failed (Correctness): {e}")
            return 0.0

    def judge_context_relevancy(self, query, context, run_config=None):
        judge_prompt = f"""
        Context: {context[:4000]}...
        Query: {query}
        
        Score the provided Context on a scale of 0.0 (pure noise) to 1.0 (every sentence is highly relevant to the Query).
        
        Return only the float score. Do not include any text, JSON, or explanation.
        """
        try:
            response = self.judge_llm.invoke(judge_prompt, config=run_config)
            content = response.content.strip()
            return float(content)
        except Exception as e:
            print(f"⚠️ Judge Failed (Relevancy): {e}")
            return 0.0

    def print_summary(self):
        if not self.results: return
        
        count = len(self.results)
        avg_latency = statistics.mean(self.latencies)
        total_cost = sum(r['cost'] for r in self.results)
        
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
    if not os.path.exists(GT_FILE):
        print(f"FATAL: Ground Truth file not found at {GT_FILE}. Cannot run full evaluation.")
        return
        
    try:
        if os.environ.get("LANGFUSE_HOST") and os.environ.get("LANGFUSE_SECRET_KEY"):
            langfuse.init(host=os.environ["LANGFUSE_HOST"], secret_key=os.environ["LANGFUSE_SECRET_KEY"])
            print("✅ Langfuse tracing initialized.")
        else:
            print("⚠️ Langfuse keys not found in environment. Tracing skipped.")
    except Exception as e:
        print(f"⚠️ Failed to initialize Langfuse: {e}")

    run_name = f"RAG_Eval_Suite_{time.strftime('%Y%m%d_%H%M%S')}"
    run_config = RunnableConfig(
        tags=["ragas_custom_evaluation", "gemini_flash"],
        configurable={
            "run_name": run_name,
        }
    )
    
    evaluator = RAGEvaluator()
    
    print("🚀 Starting RAG Evaluation Suite (Full 9 Metrics Mode)...")
    for gt_entry in evaluator.ground_truth:
        evaluator.evaluate_query(gt_entry, run_config)
        
    evaluator.print_summary()
    
    if hasattr(langfuse, 'is_initialized') and langfuse.is_initialized():
        langfuse.shutdown()
        print("✅ Langfuse tracing finished and shutdown.")

if __name__ == "__main__":
    main()
