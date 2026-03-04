import time
import os
import sys
from secrets_loader import get_google_api_key

# Set API Key securely
os.environ["GOOGLE_API_KEY"] = get_google_api_key()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_community.chat_models import ChatOllama
    from langchain_core.messages import HumanMessage
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    sys.exit(1)

def benchmark_model(name, llm, prompt_text):
    print(f"\n--- Testing {name} ---")
    start_time = time.time()
    try:
        response = llm.invoke([HumanMessage(content=prompt_text)])
        end_time = time.time()
        latency = end_time - start_time
        
        print(f"✅ Success!")
        print(f"⏱️ Latency: {latency:.4f} seconds")
        print(f"📝 Response: {response.content}")
        return latency
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

def main():
    print("🏎️  AI Model Benchmark: Local (Ollama) vs Cloud (Gemini) 🏎️")
    print("----------------------------------------------------------")

    prompt = "Explain the concept of 'Retrieval Augmented Generation' in one short sentence."
    print(f"Query: {prompt}")

    # 1. Cloud Model (Gemini)
    gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    # 2. Local Model (Ollama - Phi-3 Mini)
    # Note: Requires 'ollama run phi3:mini' to be active or model pulled
    ollama = ChatOllama(model="phi3:mini", temperature=0)

    results = {}

    # Run Benchmark
    results['Gemini 2.0 Flash'] = benchmark_model("Gemini 2.0 Flash (Cloud)", gemini, prompt)
    results['Phi-3 Mini (Local)'] = benchmark_model("Phi-3 Mini (Local CPU)", ollama, prompt)

    # Summary
    print("\n\n📊 Benchmark Results 📊")
    print("-----------------------")
    for name, lat in results.items():
        if lat:
            print(f"{name}: {lat:.4f}s")
        else:
            print(f"{name}: FAILED")

if __name__ == "__main__":
    main()
