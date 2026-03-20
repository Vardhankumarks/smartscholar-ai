import os
import streamlit as st


def get_api_key(provider):
    """Retrieve API key from Streamlit secrets or environment variables."""
    key_map = {
        "openai": "OPENAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    env_var = key_map.get(provider, "")
    try:
        return st.secrets.get(env_var, os.getenv(env_var, ""))
    except Exception:
        return os.getenv(env_var, "")


LLM_MODELS = {
    "google": {
        "name": "Google Gemini",
        "model": "gemini-2.0-flash",
        "supports_embeddings": True,
    },
    "groq": {
        "name": "Groq (Llama 3.3 70B)",
        "model": "llama-3.3-70b-versatile",
        "supports_embeddings": False,
    },
    "openai": {
        "name": "OpenAI (GPT-3.5 Turbo)",
        "model": "gpt-3.5-turbo",
        "supports_embeddings": True,
    },
}

EMBEDDING_PROVIDERS = {
    "google": {
        "name": "Google (embedding-001)",
        "model": "models/embedding-001",
        "dimension": 768,
    },
    "openai": {
        "name": "OpenAI (text-embedding-3-small)",
        "model": "text-embedding-3-small",
        "dimension": 1536,
    },
}

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 4
SIMILARITY_THRESHOLD = 0.25

MAX_SEARCH_RESULTS = 5

RESPONSE_MODES = {
    "Concise": (
        "You are SmartScholar AI, an intelligent research assistant. "
        "Provide brief, to-the-point responses in 2-3 sentences. "
        "Focus only on the most important information. Be precise and clear."
    ),
    "Detailed": (
        "You are SmartScholar AI, an intelligent research assistant. "
        "Provide comprehensive, in-depth responses with explanations, examples, "
        "and relevant context. Structure your answer with clear sections when appropriate. "
        "Be thorough and educational."
    ),
}
