# Deployment Guide for Brahma AI

Brahma AI can be deployed to any server that supports Docker or Python 3.11+.

## 🚀 Option 1: One-Click Deploy (Render / Railway / HuggingFace)

Since this app now uses **Google Gemini** (Cloud AI), you can deploy it to free/cheap cloud providers without needing a heavy GPU server.

### Steps:
1.  **Create a GitHub Repository** and push this code to it.
2.  **Sign up** on [Render.com](https://render.com) or [Streamlit Cloud](https://streamlit.io/cloud).
3.  **Connect your Repo**.
4.  **Set Environment Variables**:
    *   No special variables are strictly needed, but `DOCS_PATH` can be set if you change folder structure.
5.  **Deploy!**

**Note:** In this mode, you MUST select "Google Gemini" as the provider in the app sidebar and enter your API key each time, OR you can set the `GOOGLE_API_KEY` environment variable in your cloud provider to pre-fill it.

## 🐳 Option 2: Docker (VPS / AWS / DigitalOcean)

If you want the full persistent experience (including local knowledge base preservation):

1.  **Build the Image**:
    ```bash
    docker build -t brahma-ai .
    ```

2.  **Run the Container**:
    ```bash
    docker run -d -p 8501:8501 -v $(pwd):/app brahma-ai
    ```
    *   The `-v $(pwd):/app` part is crucial: it mounts your current folder (with PDFs and Vector DB) into the container so your data persists!

3.  **Access**:
    Open `http://YOUR_SERVER_IP:8501`

## 🧠 About Ollama (Local AI) in Cloud
Running **Ollama** in the cloud requires a server with a respectable CPU or GPU.
*   If deploying to a standard VPS, install Ollama on the HOST machine first.
*   Then, update `rag_engine.py` to point to the host's Ollama instance (usually `http://host.docker.internal:11434`), or just use the **Google Gemini** hybrid mode which is much lighter and faster for cloud servers.
