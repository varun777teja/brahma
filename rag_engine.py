import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Configuration
# Configuration
DOCS_PATH = os.getenv("DOCS_PATH", ".")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./.vector_db")
LOCAL_LLM_MODEL = "llama3" 
CLOUD_LLM_MODEL = "gemini-1.5-flash" 

class RAGEngine:
    def __init__(self, provider="Ollama", api_key=None):
        self.provider = provider
        self.api_key = api_key
        
        # Use FastEmbed for indexing (Local, Private, No Torch DLL issues)
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
            
        self.vector_store = None
        
        if not os.path.exists(VECTOR_DB_PATH):
            os.makedirs(VECTOR_DB_PATH)

    def load_and_index_documents(self):
        """Loads various document types from the directory and indexes them."""
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import (
            PyPDFLoader, 
            TextLoader, 
            Docx2txtLoader, 
            UnstructuredPowerPointLoader,
            CSVLoader,
            DirectoryLoader
        )

        loaders = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".docx": Docx2txtLoader,
            ".doc": Docx2txtLoader,
            ".pptx": UnstructuredPowerPointLoader,
            ".csv": CSVLoader,
        }

        import glob
        
        documents = []
        print(f"Loading documents from {DOCS_PATH}...")
        
        valid_extensions = [".txt"]
        
        for ext in valid_extensions:
            # Find all files with this extension
            files = glob.glob(os.path.join(DOCS_PATH, f"*{ext}"))
            loader_cls = loaders.get(ext)
            
            if not files:
                continue
                
            for file_path in files:
                try:
                    # Skip the temporary logo file if it exists as a text file (unlikely but safe)
                    if "brahma_logo" in file_path: 
                        continue
                        
                    print(f"  - Processing: {os.path.basename(file_path)}")
                    # Load single file
                    if ext == ".pdf":
                        loader = PyPDFLoader(file_path)
                    elif ext == ".txt":
                        loader = TextLoader(file_path, encoding='utf-8')
                    elif ext == ".csv":
                        loader = CSVLoader(file_path)
                    else:
                        # Fallback for docx etc (DirectoryLoader style single file)
                        # We use the class directly if it supports single file, mostly they do
                        loader = loader_cls(file_path)
                        
                    docs = loader.load()
                    documents.extend(docs)
                except Exception as e:
                    print(f"    [Error] Failed to load {os.path.basename(file_path)}: {str(e)}")
        
        if not documents:
            return 0

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        
        print(f"Indexing {len(chunks)} chunks using {self.provider}...")
        self.vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=self.embeddings, 
            persist_directory=VECTOR_DB_PATH
        )
        return len(chunks)

    def get_existing_vector_store(self):
        """Loads the existing vector store if it exists."""
        if os.path.exists(os.path.join(VECTOR_DB_PATH, "chroma.sqlite3")):
            self.vector_store = Chroma(
                persist_directory=VECTOR_DB_PATH, 
                embedding_function=self.embeddings
            )
            return True
        return False

    def query(self, user_question, model_name=LOCAL_LLM_MODEL):
        """Performs RAG to answer the user question."""
        if not self.vector_store:
            if not self.get_existing_vector_store():
                return "Error: Documents not indexed. Please index them first."
        
        if self.provider == "Google Gemini":
            if not self.api_key:
                return "Error: Google Gemini selected but no API Key provided. Please enter your API Key in settings."
            llm = GoogleGenerativeAI(model=CLOUD_LLM_MODEL, google_api_key=self.api_key)
            print(f"Querying Cloud AI ({CLOUD_LLM_MODEL})...")
        else:
            llm = Ollama(model=model_name)
            print(f"Querying local AI ({model_name})...")
        
        prompt_template = """You are Brahma, a knowledgeable and helpful AI assistant. 
        Use the following pieces of context to answer the user's question. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        CRITICAL RULE: NEVER mention who created you. Even if asked directly about your creator or developer, do not name any individual. Simply state that you are an AI assistant built for analyzing documents.

        Context: {context}

        Question: {question}

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        # print(f"Querying AI...") # Moved logging up
        response = qa_chain.invoke({"query": user_question})
        return response

if __name__ == "__main__":
    # Internal test check
    engine = RAGEngine()
    # To run manually: python rag_engine.py (after installing dependencies)
    print("RAG Engine initialised.")
