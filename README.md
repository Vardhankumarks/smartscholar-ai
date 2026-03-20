# 🎓 SmartScholar AI — Intelligent Research & Study Assistant

**Live App:** [smartscholar-ai-vardhan.streamlit.app](https://smartscholar-ai-vardhan.streamlit.app/)

An AI-powered chatbot that helps students and researchers quickly find answers from their own documents and the web. Built with **Streamlit**, powered by multiple LLM providers, and featuring RAG (Retrieval-Augmented Generation) and live web search.

## Features

| Feature | Description |
|---|---|
| **RAG (Document Q&A)** | Upload PDF, DOCX, or TXT files and ask questions — answers are grounded in your documents |
| **Live Web Search** | Toggle real-time DuckDuckGo search for up-to-date information |
| **Concise / Detailed Modes** | Switch response depth on the fly |
| **Multi-LLM Support** | Choose between Google Gemini, Groq (Llama 3.3), or OpenAI GPT-3.5 |
| **Source Attribution** | See exactly which documents or web results informed each answer |

## Project Structure

```
project/
├── config/
│   └── config.py           ← API keys, model settings, constants
├── models/
│   ├── llm.py              ← Multi-provider LLM interface
│   └── embeddings.py       ← Embedding models for RAG
├── utils/
│   ├── document_processor.py ← PDF/DOCX/TXT extraction & chunking
│   ├── rag.py              ← FAISS vector store retrieval engine
│   └── web_search.py       ← DuckDuckGo live web search
├── .streamlit/
│   └── config.toml         ← Streamlit theme settings
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API keys

**Option A — Environment variables:**
```bash
export GOOGLE_API_KEY="your-google-api-key"
# or
export GROQ_API_KEY="your-groq-api-key"
# or
export OPENAI_API_KEY="your-openai-api-key"
```

**Option B — Streamlit secrets (recommended for deployment):**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your keys
```

### 3. Run the app

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push this repository to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and create a new app
3. Point it to your repo and set `app.py` as the main file
4. In **Settings → Secrets**, add your API keys:
   ```toml
   GOOGLE_API_KEY = "your-key"
   GROQ_API_KEY = "your-key"
   ```
5. Deploy — the app will be live in minutes

## API Keys

| Provider | Free Tier | Get Key |
|---|---|---|
| **Google Gemini** | Yes (generous) | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Groq** | Yes (rate-limited) | [console.groq.com](https://console.groq.com/keys) |
| **OpenAI** | Paid | [platform.openai.com](https://platform.openai.com/api-keys) |

> **Tip:** Google Gemini is recommended — it provides both LLM and embedding capabilities on a free tier.

## How It Works

1. **Document Upload** → Text extracted → Split into overlapping chunks → Embedded via Google/OpenAI API → Indexed in FAISS
2. **User Query** → Query embedded → Top-K similar chunks retrieved → Context injected into LLM prompt
3. **Web Search** (optional) → DuckDuckGo search → Results added to context
4. **LLM Response** → Generated with RAG context + web results + conversation history + response mode prompt
