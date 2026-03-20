import streamlit as st

from config.config import (
    LLM_MODELS,
    EMBEDDING_PROVIDERS,
    RESPONSE_MODES,
    get_api_key,
)
from models.llm import LLMProvider
from models.embeddings import EmbeddingModel
from utils.rag import RAGEngine
from utils.web_search import web_search, format_search_results
from utils.document_processor import extract_text, chunk_text

# ── Page Configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartScholar AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Styling ──────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
    }
    .main-header p {
        color: #6b7280;
        font-size: 1.1rem;
    }
    .source-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-doc {
        background: #dbeafe;
        color: #1e40af;
    }
    .badge-web {
        background: #dcfce7;
        color: #166534;
    }
    .stat-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 8px;
    }
    .stChatMessage {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session State Initialization ────────────────────────────────────────────


def init_session_state():
    defaults = {
        "messages": [],
        "rag_engine": None,
        "llm": None,
        "embedding_model": None,
        "processed_files": set(),
        "llm_provider": None,
        "embedding_provider": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    # LLM Provider
    st.markdown("### LLM Provider")
    provider_options = {k: v["name"] for k, v in LLM_MODELS.items()}
    selected_provider = st.selectbox(
        "Choose your LLM",
        options=list(provider_options.keys()),
        format_func=lambda x: provider_options[x],
        key="provider_select",
    )

    # API Key for LLM
    default_key = get_api_key(selected_provider)
    api_key = st.text_input(
        f"{provider_options[selected_provider]} API Key",
        value=default_key,
        type="password",
        key="api_key_input",
    )

    # Initialize / reinitialize LLM when provider or key changes
    if api_key and (
        st.session_state.llm is None
        or st.session_state.llm_provider != selected_provider
    ):
        try:
            st.session_state.llm = LLMProvider(selected_provider, api_key)
            st.session_state.llm_provider = selected_provider
        except Exception as e:
            st.error(f"Failed to connect to LLM: {e}")

    st.divider()

    # ── Response Mode ────────────────────────────────────────────────────
    st.markdown("### 💬 Response Mode")
    response_mode = st.radio(
        "Choose response style",
        options=list(RESPONSE_MODES.keys()),
        horizontal=True,
        key="response_mode",
        help="Concise: quick 2-3 sentence answers. Detailed: in-depth explanations.",
    )

    st.divider()

    # ── Web Search Toggle ────────────────────────────────────────────────
    st.markdown("### 🌐 Web Search")
    enable_web_search = st.toggle(
        "Enable live web search",
        value=False,
        key="web_search_toggle",
        help="When enabled, the assistant will search the web for up-to-date information.",
    )

    st.divider()

    # ── Document Upload (RAG) ────────────────────────────────────────────
    st.markdown("### 📄 Knowledge Base")

    # Embedding provider for RAG
    available_embed_providers = {}
    if api_key and LLM_MODELS[selected_provider]["supports_embeddings"]:
        available_embed_providers[selected_provider] = EMBEDDING_PROVIDERS[selected_provider]["name"]
    for ep in EMBEDDING_PROVIDERS:
        if ep != selected_provider:
            ep_key = get_api_key(ep)
            if ep_key:
                available_embed_providers[ep] = EMBEDDING_PROVIDERS[ep]["name"]

    if available_embed_providers:
        embed_provider = st.selectbox(
            "Embedding Provider (for RAG)",
            options=list(available_embed_providers.keys()),
            format_func=lambda x: available_embed_providers[x],
            key="embed_provider_select",
        )

        embed_api_key = api_key if embed_provider == selected_provider else get_api_key(embed_provider)

        if st.session_state.embedding_model is None or st.session_state.embedding_provider != embed_provider:
            try:
                st.session_state.embedding_model = EmbeddingModel(embed_provider, embed_api_key)
                st.session_state.embedding_provider = embed_provider
                st.session_state.rag_engine = RAGEngine(st.session_state.embedding_model)
                st.session_state.processed_files = set()
            except Exception as e:
                st.error(f"Embedding model error: {e}")

        uploaded_files = st.file_uploader(
            "Upload documents",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt"],
            key="file_uploader",
            help="Upload PDF, DOCX, or TXT files to build your knowledge base.",
        )

        if uploaded_files and st.session_state.rag_engine is not None:
            new_files = [
                f for f in uploaded_files if f.name not in st.session_state.processed_files
            ]
            if new_files:
                with st.spinner(f"Processing {len(new_files)} document(s)..."):
                    for file in new_files:
                        try:
                            text = extract_text(file, file.name)
                            chunks = chunk_text(text)
                            st.session_state.rag_engine.add_documents(chunks, source_name=file.name)
                            st.session_state.processed_files.add(file.name)
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {e}")

        if st.session_state.rag_engine and st.session_state.rag_engine.chunk_count > 0:
            st.markdown(
                f"""
                <div class="stat-card">
                    📚 <strong>{st.session_state.rag_engine.document_count}</strong> document(s)<br>
                    🧩 <strong>{st.session_state.rag_engine.chunk_count}</strong> chunks indexed
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
                st.session_state.rag_engine.clear()
                st.session_state.processed_files = set()
                st.rerun()
    else:
        st.info(
            "RAG requires an embedding-capable API key (Google or OpenAI). "
            "Your current LLM provider doesn't support embeddings — "
            "set a Google or OpenAI key in environment variables to enable RAG."
        )

    st.divider()

    if st.button("🔄 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main Chat Area ──────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="main-header">
        <h1>🎓 SmartScholar AI</h1>
        <p>Your AI-powered research &amp; study assistant — ask questions about your documents or anything else</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Feature indicators
cols = st.columns(3)
with cols[0]:
    rag_status = "✅" if (st.session_state.rag_engine and st.session_state.rag_engine.chunk_count > 0) else "⬜"
    st.markdown(f"{rag_status} **RAG** — Document Q&A")
with cols[1]:
    web_status = "✅" if enable_web_search else "⬜"
    st.markdown(f"{web_status} **Web Search** — Live results")
with cols[2]:
    st.markdown(f"📝 **Mode** — {response_mode}")

st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📋 Sources used"):
                for src in message["sources"]:
                    if src["type"] == "document":
                        st.markdown(
                            f'<span class="source-badge badge-doc">📄 {src["name"]}</span> '
                            f"(relevance: {src['score']:.0%})",
                            unsafe_allow_html=True,
                        )
                        st.caption(src["preview"])
                    elif src["type"] == "web":
                        st.markdown(
                            f'<span class="source-badge badge-web">🌐 Web</span> '
                            f"**{src['title']}**",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"{src['body'][:150]}...")
                        st.markdown(f"[🔗 {src['url']}]({src['url']})")

# Chat input
if prompt := st.chat_input("Ask me anything about your documents or any topic..."):
    if not api_key:
        st.error("Please enter an API key in the sidebar to get started.")
        st.stop()

    if st.session_state.llm is None:
        try:
            st.session_state.llm = LLMProvider(selected_provider, api_key)
            st.session_state.llm_provider = selected_provider
        except Exception as e:
            st.error(f"Failed to initialize LLM: {e}")
            st.stop()

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        context_parts = []
        sources = []

        # ── RAG retrieval ────────────────────────────────────────────
        if st.session_state.rag_engine and st.session_state.rag_engine.chunk_count > 0:
            try:
                rag_results = st.session_state.rag_engine.search(prompt)
                if rag_results:
                    doc_context = "Relevant information from uploaded documents:\n\n"
                    for r in rag_results:
                        doc_context += f"[Source: {r['source']}]\n{r['text']}\n\n"
                        sources.append({
                            "type": "document",
                            "name": r["source"],
                            "score": r["score"],
                            "preview": r["text"][:200] + "...",
                        })
                    context_parts.append(doc_context)
            except Exception as e:
                st.warning(f"RAG search encountered an issue: {e}")

        # ── Web search ───────────────────────────────────────────────
        if enable_web_search:
            try:
                with st.spinner("Searching the web..."):
                    search_results = web_search(prompt)
                if search_results:
                    web_context = format_search_results(search_results)
                    context_parts.append(web_context)
                    for r in search_results:
                        sources.append({
                            "type": "web",
                            "title": r["title"],
                            "body": r["body"],
                            "url": r["url"],
                        })
            except Exception as e:
                st.warning(f"Web search encountered an issue: {e}")

        # ── Build augmented prompt ───────────────────────────────────
        if context_parts:
            context_block = "\n\n".join(context_parts)
            augmented_prompt = (
                f"Use the following context to help answer the question. "
                f"Cite sources when using information from the context. "
                f"If the context isn't relevant, use your own knowledge.\n\n"
                f"--- Context ---\n{context_block}\n--- End Context ---\n\n"
                f"Question: {prompt}"
            )
        else:
            augmented_prompt = prompt

        # Build message list for the LLM (keep last 20 turns for context window)
        history = []
        recent_messages = st.session_state.messages[:-1][-20:]
        for m in recent_messages:
            history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": augmented_prompt})

        system_prompt = RESPONSE_MODES[response_mode]

        try:
            response = st.write_stream(
                st.session_state.llm.generate_stream(history, system_prompt)
            )
        except Exception as e:
            response = f"Sorry, I encountered an error generating a response: {e}"
            st.error(response)

        # Show sources
        if sources:
            with st.expander("📋 Sources used"):
                for src in sources:
                    if src["type"] == "document":
                        st.markdown(
                            f'<span class="source-badge badge-doc">📄 {src["name"]}</span> '
                            f"(relevance: {src['score']:.0%})",
                            unsafe_allow_html=True,
                        )
                        st.caption(src["preview"])
                    elif src["type"] == "web":
                        st.markdown(
                            f'<span class="source-badge badge-web">🌐 Web</span> '
                            f"**{src['title']}**",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"{src['body'][:150]}...")
                        st.markdown(f"[🔗 {src['url']}]({src['url']})")

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": sources,
        })
