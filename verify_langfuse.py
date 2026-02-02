import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

try:
    from src.core import langfuse
    print("Successfully imported src.core.langfuse")
except ImportError as e:
    print(f"Failed to import src.core.langfuse: {e}")
    sys.exit(1)

public_key = langfuse.LANGFUSE_PUBLIC_KEY
secret_key = langfuse.LANGFUSE_SECRET_KEY
host = langfuse.LANGFUSE_HOST

print(f"LANGFUSE_PUBLIC_KEY: {'Found' if public_key else 'Not Found'}")
print(f"LANGFUSE_SECRET_KEY: {'Found' if secret_key else 'Not Found'}")
print(f"LANGFUSE_HOST: {host}")

if public_key and secret_key:
    print("SUCCESS: Environment variables loaded correctly.")
else:
    print("FAILURE: Environment variables missing.")
