"""UI web con Streamlit para el RAG POC."""

import sys
from pathlib import Path
import tempfile

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.chunking import process_file
from src.vectorstore import ingest_chunks, get_stats
from src.rag import query_rag
from src.config import LEMONADE_MODEL_DEV, LEMONADE_MODEL_PROD

st.set_page_config(page_title="RAG POC", page_icon="🔍", layout="wide")
st.title("RAG POC — Lemonade + bge-m3 + ChromaDB")

# Sidebar: ingesta de documentos
with st.sidebar:
    st.header("Ingesta de documentos")

    uploaded_files = st.file_uploader(
        "Sube documentos (PDF, DOCX, TXT, MD, código)",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "md", "py", "js", "ts", "java", "go", "rs", "c", "cpp", "h"],
    )

    if uploaded_files and st.button("Ingestar documentos"):
        total = 0
        for uploaded in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            with st.spinner(f"Procesando {uploaded.name}..."):
                chunks = process_file(tmp_path)
                count = ingest_chunks(chunks)
                total += count
                st.success(f"{uploaded.name}: {count} chunks")

            Path(tmp_path).unlink()

        st.info(f"Total ingestado: {total} chunks")

    st.divider()
    st.header("Estado del vector store")
    stats = get_stats()
    st.metric("Chunks almacenados", stats["total_chunks"])

    st.divider()
    model = st.selectbox("Modelo LLM", [LEMONADE_MODEL_DEV, LEMONADE_MODEL_PROD])
    top_k = st.slider("Chunks a recuperar (top_k)", 1, 20, 5)

# Main: chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en documentos y generando respuesta..."):
            result = query_rag(prompt, top_k=top_k, model=model)

        st.markdown(result["answer"])

        if result["sources"]:
            with st.expander(f"Fuentes ({len(result['sources'])} chunks recuperados)"):
                for src in result["sources"]:
                    st.markdown(f"**{src['source']}** (chunk {src['chunk_index']}, distancia: {src['distance']:.4f})")
                    st.text(src["preview"])
                    st.divider()

        if result["usage"]:
            st.caption(
                f"Modelo: {result['model']} | "
                f"Tokens: {result['usage']['prompt_tokens']} prompt + "
                f"{result['usage']['completion_tokens']} completion = "
                f"{result['usage']['total_tokens']} total"
            )

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
