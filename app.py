import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from minsearch import Index
from minsearch import VectorSearch
from sentence_transformers import SentenceTransformer
from utils.rag_helper import RAGBase

load_dotenv()

st.set_page_config(page_title="Study Goblin", page_icon="📚", layout="wide")

st.title("Study Goblin")
st.write("Ask questions about your ingested study material and get grounded answers.")

if "rag_base" not in st.session_state:
    data_path = os.path.join("data", "processed", "chunks.json")

    if not os.path.exists(data_path):
        st.warning("No processed chunks found yet. Run the ingestion flow first.")
        st.stop()

    with open(data_path, "r", encoding="utf-8") as f:
        doc_chunks = json.load(f)

    if not doc_chunks:
        st.warning("The processed chunks file is empty.")
        st.stop()

    text_index = Index(text_keys=["content"], language="en")
    text_index.fit([
        {"content": chunk.get("content", ""), "metadata": chunk.get("metadata", {})}
        for chunk in doc_chunks
    ])

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    vector_index = VectorSearch()
    vectors = [embedder.encode(chunk.get("content", "")) for chunk in doc_chunks]
    vector_index.fit(vectors, doc_chunks)

    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Set GROQ_API_KEY or OPENAI_API_KEY in your environment before starting the app.")
        st.stop()

    client = OpenAI(api_key=api_key)
    st.session_state.rag_base = RAGBase(text_index, client, vector_index, embedder)

question = st.text_input("Ask a question", placeholder="What is the chapter about?")

if st.button("Get answer") and question:
    with st.spinner("Searching the knowledge base..."):
        result = st.session_state.rag_base.rag(question)

    st.subheader("Answer")
    st.write(result.get("answer", ""))

    st.subheader("Retrieved context")
    for chunk in doc_chunks:
        if chunk.get("content", ""):
            st.write(chunk.get("content", "")[:600])
            st.divider()
