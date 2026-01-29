import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"  

st.set_page_config(page_title="RAG QA System", layout="centered")

st.title("📄 RAG-Based Question Answering")
st.write("Upload a document and ask questions from it.")

# ---------------- FILE UPLOAD ----------------
st.subheader("Upload Document")

uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

if uploaded_file:
    with st.spinner("Uploading & indexing..."):
        files = {"file": uploaded_file}
        res = requests.post(f"{API_URL}/upload", files=files)

        if res.status_code == 200:
            st.success("Document indexed successfully!")
        else:
            st.error(res.text)

# ---------------- QUESTION ASK ----------------
st.subheader("Ask a Question")

question = st.text_input("Enter your question")

if st.button("Get Answer"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating answer..."):
            res = requests.post(
                f"{API_URL}/ask",
                json={"question": question}
            )

            if res.status_code == 200:
                data = res.json()
                if "answer" in data:
                    st.markdown("### ✅ Answer")
                    st.write(data["answer"])
                else:
                    st.error(data.get("error", "Unknown error"))
            else:
                st.error(res.text)