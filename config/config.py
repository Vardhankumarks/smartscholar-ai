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
        "models": {
            "gemini-2.5-flash": "Gemini 2.5 Flash (recommended)",
            "gemini-2.5-flash-lite": "Gemini 2.5 Flash-Lite (fastest)",
            "gemini-2.5-pro": "Gemini 2.5 Pro (most capable)",
        },
        "default_model": "gemini-2.5-flash",
        "supports_embeddings": True,
    },
    "groq": {
        "name": "Groq (Free & Fast)",
        "models": {
            "llama-3.3-70b-versatile": "Llama 3.3 70B (recommended)",
            "llama-3.1-8b-instant": "Llama 3.1 8B (fastest)",
            "mixtral-8x7b-32768": "Mixtral 8x7B",
        },
        "default_model": "llama-3.3-70b-versatile",
        "supports_embeddings": False,
    },
    "openai": {
        "name": "OpenAI",
        "models": {
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "gpt-4o-mini": "GPT-4o Mini",
        },
        "default_model": "gpt-3.5-turbo",
        "supports_embeddings": True,
    },
}

EMBEDDING_PROVIDERS = {
    "google": {
        "name": "Google (gemini-embedding-001)",
        "model": "gemini-embedding-001",
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
