import os
import time
import statistics
import json
from secrets_loader import get_google_api_key

# LangChain Imports
from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

# Configuration
os.environ["GOOGLE_API_KEY"] = get_google_api_key()
COST_PER_1M_INPUT = 0.35
COST_PER_1M_OUTPUT = 0.70

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
            text_splitter = SemanticChunker(self.embeddings, breakpoint_threshold_type="percentile")
            splits = text_splitter.split_documents(docs)
            self.vectorstore = Chroma.from_documents(documents=splits, embedding=self.embeddings, persist_directory=persist_directory)

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
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10}) # Enhanced recall
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)

    def evaluate_query(self, query):
        time.sleep(2)  # Rate Limit Protection
        print(f"\n🧪 Testing: '{query}'")
        start_time = time.time()
        
        # 1. Run RAG
        result = self.retrieval_chain.invoke({"input": query})
        end_time = time.time()
        latency = end_time - start_time
        
        answer = result['answer']
        context = "\n".join([doc.page_content for doc in result['context']])
        
        # 2. LLM-as-a-Judge Evaluation
        scores = self.run_judge(query, answer, context)
        
        # 3. Calculate Metrics
        input_tokens = len(query + context) / 4 # Est.
        output_tokens = len(answer) / 4 # Est.
        cost = (input_tokens/1e6 * COST_PER_1M_INPUT) + (output_tokens/1e6 * COST_PER_1M_OUTPUT)
        
        metrics = {
            "query": query,
            "answer": answer,
            "latency": latency,
            "faithfulness": scores['faithfulness'],
            "relevance": scores['relevance'],
            "context_recall": scores['recall'],
            "cost": cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
        
        self.results.append(metrics)
        self.latencies.append(latency)
        
        print(f"   ⏱️ Latency: {latency:.2f}s")
        print(f"   💰 Cost: ${cost:.6f}")
        print(f"   ✅ Faithfulness: {scores['faithfulness']}/1")
        print(f"   🎯 Relevance: {scores['relevance']}/1")
        print(f"   🔍 Recall: {scores['recall']}/1")
        return metrics

    def run_judge(self, query, answer, context):
        # Judge Prompt
        judge_prompt = f"""
        You are an AI Evaluator. Evaluate the following RAG interaction.
        
        Query: {query}
        Context: {context[:4000]}... (truncated)
        Answer: {answer}
        
        Return a JSON object with 3 keys (0 or 1):
        - "faithfulness": 1 if the answer is derived purely from context, 0 if hallucinated.
        - "relevance": 1 if the answer directly addresses the query, 0 if irrelevant.
        - "recall": 1 if the context contained the answer (even if the model failed), 0 if context was missing info.
        
        JSON only:
        """
        try:
            response = self.judge_llm.invoke(judge_prompt)
            # Simple parsing (robustness needed for prod)
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ Judge Failed: {e}")
            return {"faithfulness": 0, "relevance": 0, "recall": 0}

    def print_summary(self):
        if not self.results: return
        
        avg_latency = statistics.mean(self.latencies)
        p50 = statistics.median(self.latencies)
        p95 = sorted(self.latencies)[int(len(self.latencies) * 0.95)] if len(self.latencies) > 1 else self.latencies[0]
        
        total_cost = sum(r['cost'] for r in self.results)
        avg_faithfulness = statistics.mean(r['faithfulness'] for r in self.results)
        avg_relevance = statistics.mean(r['relevance'] for r in self.results)
        
        print(f"\n📊 **RAG Performance Report**")
        print(f"--------------------------------")
        print(f"Queries Run:      {len(self.results)}")
        print(f"Total Cost:       ${total_cost:.6f}")
        print(f"Latency (Avg):    {avg_latency:.2f}s")
        print(f"Latency (P50):    {p50:.2f}s")
        print(f"Latency (P95):    {p95:.2f}s")
        print(f"Faithfulness:     {avg_faithfulness*100:.1f}%")
        print(f"Relevance:        {avg_relevance*100:.1f}%")
        print(f"--------------------------------")

def main():
    evaluator = RAGEvaluator()
    
    # Define Test Suite
    test_queries = [
        "What specific metric did they mention regarding the fine-tuning project's improvement percentage?",
        "Compare the latency trade-offs mentioned between the Local Model project and the Real-Time Multimodal app. Which one prioritized speed more?",
        "What did the speaker say about using OpenAI's GPT-4 for this project?"
    ]
    
    print("🚀 Starting RAG Evaluation Suite...")
    for q in test_queries:
        evaluator.evaluate_query(q)
        
    evaluator.print_summary()

if __name__ == "__main__":
    main()
