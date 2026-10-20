# pip install -U PyMuPDF openai langchain langchain-core langchain-openai langchain-chroma langchain-text-splitters unstructured[all-docs] unstructured-inference langchain-unstructured[local] python-magic-bin==0.4.14 langchain-ollama streamlit
# pip install numpy==1.26.4
# 引入套件
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain.embeddings import init_embeddings
from langchain_core.documents import Document
import fitz  # PyMuPDF
from langchain_openai import ChatOpenAI

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# 常數設定
embeddings_model = "qwen3-embedding"
no_of_dimensions = 4096
CHROMA_DIR = "./chroma_db"

# 讀取組態檔
load_dotenv()
LLM_MODEL = os.getenv('MODEL_ID')

# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="RAG Knowledge Assistant",
    page_icon="📚",
    layout="wide",
)

# ---------------------------------------------------------
# Initialize models
# ---------------------------------------------------------
# 使用 Ollama 載入詞嵌入模型
@st.cache_resource
def get_embeddings():
     # 使用 Ollama 載入詞嵌入模型
    return init_embeddings(model=embeddings_model, provider = 'ollama')

# 建立ChatOpenAI物件
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=0,
    )

# 建立Chroma向量資料庫連線
@st.cache_resource
def get_vector_store():
    return Chroma(
        collection_name="rag_documents",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )

# ---------------------------------------------------------
# Load document
# ---------------------------------------------------------
# 定義函數，萃取PDF檔案內容，並轉成文字
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text
    
# 定義函數，載入檔案內容，並轉成文字
def load_document(file_path, file_name):
    extension = file_name.lower().split(".")[-1]
    if extension.lower() == 'pdf':
        content = extract_text_from_pdf(file_path)
        return [Document(page_content=content, metadata={'source':file_name})]
    if extension.lower() in ('txt', 'csv'):
        content = open(file_path).readlines()
        return [Document(page_content=content, metadata={'source':file_name})]
    else:
        loader = UnstructuredLoader(file_path)
    return loader.load()


# 定義函數，分塊
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)


# 定義函數，檢索
def index_documents(files):
    all_chunks = []
    for uploaded_file in files:
        suffix = "." + uploaded_file.name.split(".")[-1]
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:
            tmp.write(uploaded_file.getvalue())
            temp_path = tmp.name
        try:
            documents = load_document(
                temp_path,
                uploaded_file.name
            )
            chunks = split_documents(documents)
            for chunk in chunks:
                chunk.metadata["source"] = uploaded_file.name
            all_chunks.extend(chunks)
        finally:
            os.remove(temp_path)

    if not all_chunks:
        return 0

    vector_store = get_vector_store()
    vector_store.add_documents(all_chunks)
    return len(all_chunks)


# ---------------------------------------------------------
# RAG
# ---------------------------------------------------------
# 定義函數，提問，取得回應
def ask_rag(question, k=5):
    vector_store = get_vector_store()
    documents = vector_store.similarity_search(
        question,
        k=k
    )
    if not documents:
        return "I could not find relevant information.", []
    context_parts = []

    for i, doc in enumerate(documents):
        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        context_parts.append(
            f"[Document {i + 1}]\n"
            f"Source: {source}\n"
            f"{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a helpful RAG assistant.
                Answer the user's question using ONLY the supplied context.
                If the answer cannot be found in the context, say:
                "I don't have enough information in the provided documents."
                Do not invent facts.
                Include source references when possible.
                """.replace('  ', '')
            ),
            (
                "human",
                """
                Context:
                {context}

                Question:
                {question}
                """.replace('  ', '')
            ),
        ]
    )

    chain = prompt | get_llm()

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content, documents


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("📚 RAG Knowledge Assistant")
st.caption(
    "Upload documents and ask questions about them."
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.header("📄 Documents")
    uploaded_files = st.file_uploader(
        "Upload documents",
        # type=["pdf", "txt", "docx", "xlsx", "csv" "md", "html"],
        accept_multiple_files=True,
    )

    if st.button(
        "🔄 Index Documents",
        use_container_width=True,
    ):
        if not uploaded_files:
            st.warning(
                "Please upload at least one document."
            )
        else:
            with st.spinner(
                "Indexing documents..."
            ):

                count = index_documents(
                    uploaded_files
                )

            st.success(
                f"Indexed {count} chunks."
            )

    st.divider()

    st.header("⚙️ Settings")
    top_k = st.slider(
        "Retrieved documents",
        min_value=1,
        max_value=10,
        value=5,
    )


# ---------------------------------------------------------
# Chat
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

# 手機無法通訊.pdf：哪些地區行動電話通話出現異常
question = st.chat_input(
    "Ask a question about your documents..."
)

if question:
    # User message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner(
            "Searching knowledge base..."
        ):
            answer, documents = ask_rag(
                question,
                k=top_k,
            )
        st.markdown(answer)

        # Sources
        if documents:
            with st.expander(
                "📚 Sources"
            ):
                for i, doc in enumerate(
                    documents
                ):
                    source = doc.metadata.get(
                        "source",
                        "Unknown"
                    )
                    st.markdown(
                        f"**{i + 1}. {source}**"
                    )
                    st.caption(
                        doc.page_content[:500]
                        + "..."
                    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )