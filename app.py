import streamlit as st
import os
import time
import base64
from rag_engine import RAGEngine

# Page config
st.set_page_config(
    page_title="Brahma AI Assistant",
    page_icon="brahma_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

AI_ICON = "brahma_logo.png"

# Custom CSS for premium look
st.markdown("""
    <style>
    @keyframes spin-glow {
        0% { transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 5px #4CAF50); }
        50% { transform: rotate(180deg) scale(1.1); filter: drop-shadow(0 0 20px #4CAF50); }
        100% { transform: rotate(360deg) scale(1); filter: drop-shadow(0 0 5px #4CAF50); }
    }
    @keyframes fly-to-chat {
        0% { transform: scale(1) translate(0, 0); opacity: 1; filter: drop-shadow(0 0 20px #4CAF50); }
        100% { transform: scale(0.2) translate(-500px, 200px); opacity: 0; filter: blur(10px); }
    }
    .rotating-logo {
        animation: spin-glow 2s ease-in-out infinite;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 120px;
        margin-bottom: 20px;
    }
    .fly-effect {
        animation: fly-to-chat 0.7s ease-in forwards;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 120px;
        margin-bottom: 20px;
    }
    .title-container {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .title-logo {
        width: 50px;
        filter: drop-shadow(0 0 5px #4CAF50);
    }
    .main {
        background-color: #0f1116;
        color: #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 0 15px #4CAF50;
    }
    .sidebar .sidebar-content {
        background-color: #1a1c23;
    }
    h1 {
        color: #4CAF50;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
    }
    .chat-bubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    .feature-badge {
        background-color: #1a1c23;
        border: 1px solid #333;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.75em;
        margin: 5px;
        display: inline-block;
        color: #888;
    }
    .feature-badge.coming-soon {
        border-color: #4CAF50;
        color: #4CAF50;
    }
    .user-bubble {
        background-color: #2b2d31;
        align-self: flex-end;
        margin-left: auto;
    }
    .ai-bubble {
        background-color: #1e1e1e;
        border-left: 4px solid #4CAF50;
    }
    /* Improve avatar size and style */
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 60px !important;
        height: 60px !important;
        border: 2px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "provider" not in st.session_state:
    st.session_state.provider = "Google Gemini"  # Default to Gemini for cloud deployment
if "api_key" not in st.session_state:
    # Try to load from environment variable, fallback to hardcoded key
    st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyC7SnUQsVjGF_h3O0tJhDI6HTvQM0kH7jY")
# Ensure engine is always initialized
if "engine" not in st.session_state:
    st.session_state.engine = RAGEngine(provider=st.session_state.provider, api_key=st.session_state.api_key)
    st.session_state.indexed = st.session_state.engine.get_existing_vector_store()

# Encode logo for rotating effect
if "logo_base64" not in st.session_state:
    with open(AI_ICON, "rb") as f:
        st.session_state.logo_base64 = base64.b64encode(f.read()).decode()

# Sidebar
with st.sidebar:
    st.image(AI_ICON, width=150)
    st.title("⚙️ Controls")
    st.markdown("---")
    
    st.subheader("📜 Chat History")
    if not st.session_state.messages:
        st.info("No recent chats.")
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                # Show first 25 chars as preview
                preview = msg["content"][:25] + "..." if len(msg["content"]) > 25 else msg["content"]
                if st.button(f"💬 {preview}", key=f"hist_{i}"):
                    # Logic could go here to jump to message, but for now we list
                    pass

    st.markdown("---")
    st.subheader("🤖 AI Settings")
    
    # Provider Selection
    new_provider = st.selectbox(
        "AI Provider", 
        ["Ollama", "Google Gemini"], 
        index=0 if st.session_state.provider == "Ollama" else 1
    )
    
    # API Key Input (only if Gemini)
    new_api_key = st.session_state.api_key
    if new_provider == "Google Gemini":
        new_api_key = st.text_input(
            "Gemini API Key", 
            value=st.session_state.api_key, 
            type="password",
            help="Get your key at aistudio.google.com"
        )
        if not new_api_key:
            st.warning("⚠️ API Key required for Gemini")

    # Check for changes and update engine
    if new_provider != st.session_state.provider or new_api_key != st.session_state.api_key:
        st.session_state.provider = new_provider
        st.session_state.api_key = new_api_key
        # Re-initialize engine with new settings
        st.session_state.engine = RAGEngine(provider=new_provider, api_key=new_api_key)
        st.success(f"Switched to {new_provider}!")
        time.sleep(1) # Give user time to see message
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Add Knowledge")
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF, Word, TXT, etc.)", 
        accept_multiple_files=True,
        type=['pdf', 'docx', 'doc', 'txt', 'pptx', 'csv'],
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(".", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} files!")
        if st.button("🚀 Process & Train Brahma"):
            with st.spinner("Brahma is learning from your data..."):
                try:
                    num_chunks = st.session_state.engine.load_and_index_documents()
                    st.session_state.indexed = True
                    st.success(f"Successfully trained on {num_chunks} new pieces of knowledge!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error training: {str(e)}")

    st.markdown("---")
    st.subheader("📚 Knowledge Base")
    extensions = [".pdf", ".docx", ".doc", ".txt", ".pptx", ".csv"]
    all_docs = [f for f in os.listdir(".") if any(f.endswith(ext) for ext in extensions)]
    st.write(f"Found **{len(all_docs)}** documents in workspace.")
    
    if st.button("🔄 Re-index Documents"):
        with st.spinner("Processing documents... this may take a minute."):
            try:
                num_chunks = st.session_state.engine.load_and_index_documents()
                st.session_state.indexed = True
                st.success(f"Indexed {num_chunks} text chunks!")
            except Exception as e:
                st.error(f"Error indexing: {str(e)}")

    st.markdown("---")
    if st.session_state.provider == "Ollama":
        st.info("🔒 This app runs 100% locally. Your data never leaves this machine.")
    else:
        st.warning("☁️ Hybrid Mode: Your documents stay local, but relevant text snippets are sent to Google Gemini for answering.")

# Main UI
st.markdown(f"""
    <div class="title-container">
        <img src="data:image/png;base64,{st.session_state.logo_base64}" class="title-logo">
        <h1>Brahma AI Assistant</h1>
    </div>
""", unsafe_allow_html=True)

# Future Features Row
st.markdown("---")
cols = st.columns(4)
with cols[0]:
    st.markdown("<div class='feature-badge coming-soon'>⚡ Ultra-Fast</div>", unsafe_allow_html=True)
with cols[1]:
    st.markdown("<div class='feature-badge'>🎙️ Voice Mode</div>", unsafe_allow_html=True)
with cols[2]:
    st.markdown("<div class='feature-badge'>📸 Vision AI</div>", unsafe_allow_html=True)
with cols[3]:
    st.markdown("<div class='feature-badge'>📂 Auto-Doc</div>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    avatar = AI_ICON if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask Brahma anything..."):
    # Clear session state messages for the display part if needed, but we append
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=AI_ICON):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Show rotating logo during search with JS timer
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown(f"""
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{st.session_state.get("logo_base64", "")}" class="rotating-logo">
                        <div style="color: #4CAF50; font-family: 'Courier New', monospace; font-size: 1.1em; margin-top: -10px; margin-bottom: 20px;">
                            <span id="thinking_status">Thinking ({st.session_state.provider})...</span> <span id="timer_val" style="font-weight: bold;">0.0s</span>
                        </div>
                    </div>
                    <script>
                        var start = Date.now();
                        var timerSpan = document.getElementById('timer_val');
                        if(window.brahmaInterval) clearInterval(window.brahmaInterval);
                        window.brahmaInterval = setInterval(function() {{
                            if(!document.getElementById('timer_val')) {{
                                clearInterval(window.brahmaInterval);
                                return;
                            }}
                            var delta = ((Date.now() - start) / 1000).toFixed(3);
                            if(timerSpan) timerSpan.innerHTML = delta + "s";
                        }}, 30);
                    </script>
                    """, unsafe_allow_html=True)
                
                start_ts = time.time()
                response = st.session_state.engine.query(prompt, model_name="llama3")
                end_ts = time.time()
                elapsed_time = f"{end_ts - start_ts:.2f}s"
            
            # Completion Effect: Move to chat
            # Clear interval script first to be clean
            loading_placeholder.markdown(f"""
                <script>if(window.brahmaInterval) clearInterval(window.brahmaInterval);</script>
                <img src="data:image/png;base64,{st.session_state.get("logo_base64", "")}" class="fly-effect">
                """, unsafe_allow_html=True)
            import time
            time.sleep(0.6)
            loading_placeholder.empty()
            
            if isinstance(response, str):
                st.error(response)
            else:
                answer = response["result"]
                sources = response.get("source_documents", [])
                
                # Format sources beautifully
                source_details = "\n\n---\n**🔍 Cited Sources:**\n"
                seen_sources = set()
                for doc in sources:
                    filename = os.path.basename(doc.metadata.get('source', 'unknown'))
                    page = doc.metadata.get('page', 'N/A')
                    # If page is 0-indexed, make it 1-indexed for the user
                    if isinstance(page, int): page += 1
                    
                    entry = f"- 📄 **{filename}** (Page **{page}**)"
                    if entry not in seen_sources:
                        source_details += entry + "\n"
                        seen_sources.add(entry)
                
                # Add time badge
                time_badge = f"\n<div style='text-align: right; color: #666; font-size: 0.8em; margin-top: 10px;'>⏱️ Response time: <b>{elapsed_time}</b></div>"
                
                full_response = answer + source_details + time_badge
                
                # Performance hack: Stream the answer to feel faster
                import time
                placeholder = ""
                for word in full_response.split():
                    placeholder += word + " "
                    response_placeholder.markdown(placeholder + "▌")
                    time.sleep(0.02)
                response_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            st.error(f"AI Error: {str(e)}")
            if "ConnectionError" in str(e):
                st.warning("⚠️ Is Ollama running? Please start Ollama on your machine.")
