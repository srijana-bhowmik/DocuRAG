import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="DocuRAG",
    page_icon="📚",
    layout="wide"
) 

st.markdown("""
<style> 
.stApp {
    background-color: #0b0f19;
    color: #f1f5f9;
} 
/* Main title */
.title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
} 
.subtitle {
    color: #94a3b8;
    font-size: 17px;
    margin-bottom: 30px;
} 
/* Cards */
.card {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
} 
/* Upload area */
.upload-card {
    background-color: #111827;
    border: 1px solid #374151;
    border-radius: 16px;
    padding: 25px;
} 
/* Chat messages */
.user-message {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
} 
.bot-message {
    background-color: #111827;
    border: 1px solid #1f2937;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0 20px 0;
} 
.source {
    color: #94a3b8;
    font-size: 13px;
} 
/* Chat input */
[data-testid="stChatInput"] textarea {
    color: #111827 !important;
    background-color: #f8fafc !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
}

/* Chat input container */
[data-testid="stChatInput"] {
    background-color: #f8fafc !important;
    border-radius: 12px;
}

/* Send button */
[data-testid="stChatInput"] button {
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

[data-testid="stMetric"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 14px;
    font-size: 13px;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-size: 13px;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

#embedding model
@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ) 
embeddings = load_embeddings()

 #chat model
@st.cache_resource
def load_llm():

    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.7,
        max_tokens=512
    ) 
llm = load_llm()

#prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful assistant that answers questions based only
        on the provided context.

        Use only the provided context to answer the question.

        If the context does not contain the answer, say:
        "I couldn't find the answer in the provided document."
        """
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion: {question}"
    )
])

#sidebar
with st.sidebar:

    st.markdown("## 📚 DocuRAG")

    st.markdown(
        "### Chat with your documents"
    ) 
    st.markdown("---") 
    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    ) 
    st.markdown("---") 
    st.markdown("### ⚙️ How do I work?") 
    st.code("📄 Upload PDF ") 
    st.caption("↓")
    st.code("✂️ Split into chunks") 
    st.caption("↓")
    st.code("🧠 Generate embeddings") 
    st.caption("↓")
    st.code("🗄️ Store in Chroma") 
    st.caption("↓")
    st.code("🔎 Retrieve relevant chunks") 
    st.caption("↓")
    st.code("🤖 Generate answer")  

#main area ui 
st.markdown(
    '<div class="title">📚 DocuRAG</div>',
    unsafe_allow_html=True
) 
st.markdown(
    '<div class="subtitle">'
    'Ask questions about any PDF'
    '</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
if uploaded_file is None:

    st.markdown(
        '<div class="subtitle">'
        'Upload a PDF to get started.'
        '</div>',
        unsafe_allow_html=True
    )
    st.stop()


#save uploaded file
with tempfile.NamedTemporaryFile(
    delete=False,
    suffix=".pdf"
) as temp_file: 
    temp_file.write(uploaded_file.getvalue())
    pdf_path = temp_file.name

#load pdf,split into chunks,create embeddings for each chunk,store in vector db
with st.spinner("📖 Processing your PDF..."):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="pdf_collection"
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "lambda_mult": 0.5
        }
    )

os.remove(pdf_path)

#document info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "📄 Document",
        uploaded_file.name
    )
with col2:
    st.metric(
        "📑 Pages",
        len(docs)
    )
with col3:
    st.metric(
        "🧩 Chunks",
        len(chunks)
    )

st.markdown("---") 

st.subheader("🧩 Document Chunks")

for i, chunk in enumerate(chunks):

    with st.expander(f"Chunk {i + 1}  •  Page {chunk.metadata.get('page', 'N/A')}"):

        st.write(chunk.page_content)

# --------------------------------------------------
#chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="user-message">
            👤 <b>You</b><br><br>
            {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="bot-message">
            🤖 <b>DocuRAG</b><br><br>
            {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

#input query
query = st.chat_input(
    "Ask something about your PDF..."
)

if query: 
    st.session_state.messages.append({
        "role": "user",
        "content": query
    }) 
    with st.spinner("🔎 Searching your document..."):
        results = retriever.invoke(query)
    context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    final_prompt = prompt.invoke({  "context": context, "question": query})

    with st.spinner("🤖 Generating answer..."):
        response = llm.invoke(final_prompt)
    answer = response.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    }) 

    st.rerun()