import os
import sys
# Standard imports for LangChain 0.2/0.3
from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from secrets_loader import get_google_api_key

# Note: In 0.3, Chroma moved to langchain-chroma package usually, 
# but if not installed, fallback to community.
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

# Set your API key securely
os.environ["GOOGLE_API_KEY"] = get_google_api_key()

def main():
    print("--- 📚 RAG System Starting (Semantic Mode - Modern) ---")
    
    # Setup Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = None
    persist_directory = "./chroma_db_semantic_v3"

    # 1. Load Existing Vector Store (if available)
    if os.path.exists(persist_directory) and os.path.isdir(persist_directory) and os.listdir(persist_directory):
        print("✅ Loading existing vector store from disk...")
        try:
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        except Exception as e:
            print(f"⚠️ Failed to load existing store: {e}. Recreating...")
            vectorstore = None
    
    # 2. Recreate if needed
    if not vectorstore:
        print("⚠️ No valid store found. Creating new vector store...")
        try:
            loader = TextLoader("/root/.openclaw/workspace/downloads/clean_transcript.txt")
            docs = loader.load()
            print(f"Loaded {len(docs)} document(s).")
            
            print("Initializing Semantic Chunker (this uses embeddings)...")
            text_splitter = SemanticChunker(
                embeddings,
                breakpoint_threshold_type="percentile"
            )
            splits = text_splitter.split_documents(docs)
            print(f"Split into {len(splits)} semantic chunks.")
            
            print("Creating vector store...")
            vectorstore = Chroma.from_documents(
                documents=splits, 
                embedding=embeddings,
                persist_directory=persist_directory
            )
            print("Vector store created successfully.")
        except Exception as e:
            print(f"❌ Critical Error creating vector store: {e}")
            return

    # 3. Retrieval & Chat
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash", 
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Modern Prompt Template (No System Role, just Human to avoid errors)
    prompt = ChatPromptTemplate.from_messages([
        ("human", """You are a helpful assistant. Use the following context to answer the question.
        If the answer is not in the context, say "I don't know" or "The context does not mention this."
        
        Context:
        {context}
        
        Question: {input}
        """)
    ])

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 4. Interactive Loop
    print("\n--- 🤖 Semantic RAG Ready! (Type 'exit' to quit) ---")
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(f"Query: {query}")
        try:
            result = retrieval_chain.invoke({"input": query})
            print(f"\nAnswer: {result['answer']}")
        except Exception as e:
            print(f"Error generating answer: {e}")
        return

    while True:
        try:
            query = input("\nYou: ")
            if query.lower() in ['exit', 'quit']:
                break
            result = retrieval_chain.invoke({"input": query})
            print(f"Gemini: {result['answer']}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
