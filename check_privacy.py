import os
import subprocess
import shutil

def check_setup():
    print("--- Private AI Health Check ---")
    
    # 1. Check Ollama
    ollama_exec = shutil.which("ollama")
    if ollama_exec:
        print(f"[OK] Ollama is installed at: {ollama_exec}")
    else:
        print("[MISSING] Ollama is NOT installed.")
        print("    -> Privacy requires a local engine. Download it here: https://ollama.com/download")
    
    # 2. Check Python Environment
    try:
        import langchain
        print(f"[OK] LangChain is installed")
    except ImportError:
        print("[MISSING] LangChain is missing. Run: pip install langchain")

    # 3. Check Torch (The usual cause of errors)
    try:
        import torch
        print("[OK] Torch is working correctly.")
    except Exception as e:
        print(f"[ERROR] Torch Error: {str(e)}")
        print("    -> Note: Our updated app uses Ollama for embeddings to AVOID this error.")

    print("\n--- Next Steps for Privacy ---")
    print("1. Install Ollama from https://ollama.com")
    print("2. Run 'ollama run llama3' in your terminal.")
    print("3. Run 'ollama pull nomic-embed-text' for document reading.")
    print("4. Restart this app.")

if __name__ == "__main__":
    check_setup()
