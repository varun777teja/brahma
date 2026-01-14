import sys
import subprocess

def check_imports():
    packages = [
        "streamlit", 
        "langchain", 
        "chromadb", 
        "pypdf", 
        "sentence_transformers", 
        "ollama",
        "langchain_google_genai"
    ]
    all_ok = True
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
            print(f"[OK] {pkg} is installed.")
        except ImportError:
            print(f"[ERROR] {pkg} is NOT installed.")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("Verifying setup...")
    if check_imports():
        print("\nAll Python dependencies are ready!")
        print("To start the app, run: streamlit run app.py")
    else:
        print("\nSome dependencies are missing. Please wait for the installation to finish.")
