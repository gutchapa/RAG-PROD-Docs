import os

def load_secret(secret_name):
    """
    Loads a secret from a file (Docker secret pattern) or environment variable.
    Priority:
    1. File: secrets/{secret_name}
    2. Env: {secret_name}
    """
    # 1. Try file
    secret_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets", secret_name)
    if os.path.exists(secret_path):
        try:
            with open(secret_path, "r") as f:
                return f.read().strip()
        except IOError:
            pass

    # 2. Try environment
    return os.environ.get(secret_name)

def get_google_api_key():
    key = load_secret("GOOGLE_API_KEY")
    if not key:
        raise ValueError("❌ Secret GOOGLE_API_KEY not found in secrets/ file or environment variables.")
    return key
