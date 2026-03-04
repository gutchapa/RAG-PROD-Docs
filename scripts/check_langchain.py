import langchain.chains
print(dir(langchain.chains))
try:
    from langchain.chains import create_retrieval_chain
    print("SUCCESS: create_retrieval_chain found")
except ImportError as e:
    print(f"FAILURE: {e}")
