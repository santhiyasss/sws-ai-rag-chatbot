# SWS AI RAG Chatbot

An internal HR policy chatbot built with Retrieval-Augmented Generation (RAG). Employees can ask questions about company policies — leave, benefits, WFH, resignation, IT security, and more — and get accurate, source-cited answers grounded exclusively in company documents.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — `llama-3.1-8b-instant` |
| Embeddings | HuggingFace — `all-MiniLM-L6-v2` |
| Vector DB | ChromaDB (local persistent store) |
| Backend | FastAPI (Python) |
| Frontend | React + Vite |

---

## Project Structure

```
sws-ai-rag-chatbot/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── ingest.py                # Run this to ingest PDFs into ChromaDB
│   ├── requirements.txt
│   ├── documents/               # Place your PDF policy files here
│   │   ├── SWS-AI-leave-policy.pdf
│   │   ├── SWS-AI-hr-policy.pdf
│   │   └── ... (10 PDFs total)
│   └── app/
│       ├── api/
│       │   └── chat.py          # /api/chat POST endpoint
│       ├── core/
│       │   └── config.py        # Environment variable settings
│       └── services/
│           ├── ingestion.py     # PDF loading, chunking, embedding
│           ├── retriever.py     # ChromaDB similarity search
│           └── rag_chain.py     # Groq LLM + prompt + RAG chain
└── frontend/
    ├── index.html
    ├── package.json
    └── src/
        ├── App.jsx              # Main chat UI component
        └── App.css
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

---

### 1. Clone the Repository

```bash
git clone https://github.com/santhiyasss/sws-ai-rag-chatbot.git
cd sws-ai-rag-chatbot
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

### 3. Set Environment Variables

Create a `.env` file inside the `backend/` folder:

```bash
# backend/.env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_PERSIST_DIR=./vectorstore
DOCUMENTS_DIR=./documents
EMBEDDING_MODEL=all-MiniLM-L6-v2
COLLECTION_NAME=sws_ai_policies
TOP_K=4
```

> Get your free Groq API key at https://console.groq.com

---

### 4. Ingest Documents into Vector Store

Place your PDF policy documents inside `backend/documents/`, then run:

```bash
cd backend
python ingest.py
```

This will:
- Extract text from all PDFs using PyMuPDF
- Split text into chunks (500 tokens, 50 overlap)
- Embed chunks using `all-MiniLM-L6-v2`
- Save the vector store to `backend/vectorstore/`

You should see output like:
```
Loaded: SWS-AI-leave-policy.pdf (5 pages)
...
Total chunks created: 312
Vector store saved to: ./vectorstore
```

---

### 5. Run the Backend API

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API will be live at: `http://localhost:8000`

Test it:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the annual leave policy?"}'
```

---

### 6. Run the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at: `http://localhost:5173`

---

## Architecture & Design Decisions

### Embedding Model — `all-MiniLM-L6-v2`

Chosen for its balance of speed and semantic quality. It's a lightweight sentence-transformer model (80MB) that runs locally with no API cost, produces 384-dimensional embeddings, and performs well on HR/policy domain text. Since all documents are internal English-language policy PDFs, a general-purpose sentence transformer is sufficient without fine-tuning.

### Vector Database — ChromaDB

ChromaDB was chosen for its zero-infrastructure setup — it persists to a local directory with no separate server required. This is ideal for a company-internal tool where simplicity and portability matter. The vector store is built once during ingestion and reloaded on each API startup.

### Chunking Strategy

PDFs are loaded page-by-page using PyMuPDF (fitz), then split using `RecursiveCharacterTextSplitter` with:
- **Chunk size: 500 characters** — small enough to be semantically focused, large enough to contain a complete policy clause
- **Chunk overlap: 50 characters** — prevents context loss at chunk boundaries
- **Separators: `["\n\n", "\n", ".", " ", ""]`** — respects paragraph and sentence boundaries before hard-splitting

This strategy preserves the natural structure of policy documents (sections, clauses, bullet points) rather than splitting mid-sentence.

### Retrieval — Top K = 4

At query time, the user's question is embedded and the top 4 most similar chunks are retrieved from ChromaDB using cosine similarity. Four chunks provide enough context for multi-part policy questions (e.g. "What is leave encashment and how do I apply?") without exceeding the LLM's effective context window or introducing noise from irrelevant chunks.

### LLM — Groq `llama-3.1-8b-instant`

Groq's inference API provides extremely low latency (typically under 1 second) on the Llama 3.1 8B model — critical for a real-time chat interface. The model is instructed via a strict system prompt to answer **only from the retrieved context** and explicitly say "I don't have that information" when the answer is not in the documents. Temperature is set to 0 for deterministic, factual responses.

### Prompt Design

```
You are an HR assistant for SWS AI. Answer employee questions using ONLY 
the provided company policy documents.

Rules:
- Answer only from the context below. Be concise and specific.
- If the answer is not in the documents, say exactly: 
  "I don't have that information in the company documents."
- Never make up policies or numbers.

Context:
{context}
```

The system prompt enforces strict grounding — no hallucination, no general knowledge, only what's in the PDFs. The retrieved chunks are injected as `{context}` and the user's question as `{question}`.

---

## API Reference

### `POST /api/chat`

**Request:**
```json
{
  "question": "How many annual leave days do I get?"
}
```

**Response:**
```json
{
  "answer": "Employees are entitled to 18 days of earned leave per year, accrued at 1.5 days per month.",
  "sources": ["SWS-AI-leave-policy.pdf"]
}
```

---

## Documents Ingested

| File | Topic |
|---|---|
| SWS-AI-leave-policy.pdf | Annual, sick, casual leave rules |
| SWS-AI-hr-policy.pdf | General HR policies |
| SWS-AI-benefits-compensation.pdf | Salary, benefits, perks |
| SWS-AI-code-of-conduct.pdf | Workplace conduct |
| SWS-AI-company-overview.pdf | Company background |
| SWS-AI-it-security-policy.pdf | IT and data security |
| SWS-AI-onboarding-guide.pdf | New employee onboarding |
| SWS-AI-performance-review.pdf | Appraisal process |
| SWS-AI-resignation-policy.pdf | Exit and notice period |
| SWS-AI-wfh-policy.pdf | Work from home guidelines |