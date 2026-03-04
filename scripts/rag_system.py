import os
import sys
from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Set your API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCtbCBCwXvLoBunF7AhI-2oGs0uzO8Sddo"

def main():
    print("--- 📚 RAG System Starting (Semantic Mode) ---")
    
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
    
    text_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile" # Splits when semantic difference > X percentile
    )
    
    splits = text_splitter.split_documents(docs)
    print(f"Split into {len(splits)} semantic chunks.")

    # 3. Store (ChromaDB)
    print("Creating vector store...")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings,
        persist_directory="./chroma_db_semantic"
    )
    print("Vector store created successfully.")

    # 4. Retrieval & Chat
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash", 
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Custom Prompt
    template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context:
    {context}

    Question: {question}
    Answer:"""
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # Note: Using legacy RetrievalQA for broader compatibility with imports
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )

    # 5. Interactive Loop
    print("\n--- 🤖 Semantic RAG Ready! (Type 'exit' to quit) ---")
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(f"Query: {query}")
        result = qa_chain({"query": query})
        print(f"\nAnswer: {result['result']}")
        return

    while True:
        try:
            query = input("\nYou: ")
            if query.lower() in ['exit', 'quit']:
                break
            result = qa_chain({"query": query})
            print(f"Gemini: {result['result']}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
