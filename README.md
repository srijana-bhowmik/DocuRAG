# 📚 DocuRAG

A dark-themed **Retrieval-Augmented Generation (RAG)** application that allows users to upload a PDF and ask questions about its contents.

The application processes the uploaded document, splits it into chunks, converts the chunks into embeddings using a local Hugging Face embedding model, stores them in Chroma, retrieves relevant chunks using MMR, and uses a Groq-hosted LLM to generate the final answer.

---

## 🛠️ Tech Stack
Python
Streamlit — user interface
LangChain — RAG pipeline
Hugging Face — local embedding model
Sentence Transformers — all-MiniLM-L6-v2
Chroma — vector database
Groq — LLM inference
PyPDF — PDF document loading

DocuRAG/
│
├── UImain.py          # Streamlit user interface
├── rag.py             # RAG-related functionality
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
│
├── .env               # API keys (not committed)
├── main.py            # Local development file (not committed)
└── chromaDB/          # Local vector database (not committed)

--- 

## ✨ Features

- 📄 Upload any PDF document
- ✂️ Split documents into smaller chunks
- 🧠 Generate embeddings locally using Hugging Face
- 🗄️ Store document embeddings in Chroma
- 🔎 Retrieve relevant chunks using MMR
- 🤖 Generate answers using a Groq LLM
- 💬 Interactive chat interface
- 🧩 View document chunks
- 📑 Display document information such as pages and chunks
- 🌙 Dark-themed Streamlit UI

--- 

##  🚀 Installation

### 1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DocuRAG
### 2. Create a virtual environment
python -m venv .venv

Activate it:

macOS / Linux

source .venv/bin/activate

Windows

.venv\Scripts\activate
### 3. Install dependencies
pip install -r requirements.txt
🔑 Environment Variables

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key

The .env file is intentionally excluded from GitHub.

### ▶️ Run the Application

Start the Streamlit application with:

streamlit run UImain.py

Then open the local Streamlit URL shown in your terminal.

----

## 🏗️ Architecture

```text
                ┌──────────────┐
                │  Upload PDF  │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │ PyPDFLoader  │
                └──────┬───────┘
                       │
                       ▼
              ┌───────────────────┐
              │  Text Chunking    │
              │ RecursiveSplitter │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Hugging Face      │
              │ Embeddings        │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Chroma Vector DB  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ MMR Retriever     │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Context + Query   │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Groq LLM          │
              └─────────┬─────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   Answer    │
                 └─────────────┘


