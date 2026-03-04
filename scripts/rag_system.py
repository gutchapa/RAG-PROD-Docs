import os
import sys
# Standard imports for LangChain 0.2/0.3
from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_chroma import Chroma  <-- Removed
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Note: In 0.3, Chroma moved to langchain-chroma package usually, 
# but if not installed, fallback to community.
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

# Set your API key
# Best Practice: Read from environment variable, do not hardcode!
if not os.environ.get("GOOGLE_API_KEY"):
    print("❌ Error: GOOGLE_API_KEY environment variable not set.")
    print("Usage: GOOGLE_API_KEY='your_key' python3 rag_system.py")
    sys.exit(1)

def main():
    print("--- 📚 RAG System Starting (Semantic Mode - Modern) ---")
    
    # 1. Load Data
    try:
        loader = TextLoader("/root/.openclaw/workspace/downloads/clean_transcript.txt")
        docs = loader.load()
        print(f"Loaded {len(docs)} document(s).")
    except Exception as e:
        print(f"Error loading document: {e}")
        return

    # 2. Split Text (SEMANTIC CHUNKING!) 🧠
    print("Initializing Semantic Chunker (this uses embeddings)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Using 'percentile' threshold to find meaningful breaks
    text_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile"
    )
    
    try:
        splits = text_splitter.split_documents(docs)
        print(f"Split into {len(splits)} semantic chunks.")
    except Exception as e:
        print(f"Error splitting text: {e}")
        return

    # 3. Store (ChromaDB)
    print("Creating vector store...")
    try:
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings,
            persist_directory="./chroma_db_semantic_v3"
        )
        print("Vector store created successfully.")
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return

    # 4. Retrieval & Chat
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash", 
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Modern Prompt Template (No System Role, just Human to avoid errors)
    prompt = ChatPromptTemplate.from_messages([
        ("human", """You are a helpful assistant. Use the following context to answer the question.
        
        Context:
        {context}
        
        Question: {input}
        """)
    ])

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 5. Interactive Loop
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
