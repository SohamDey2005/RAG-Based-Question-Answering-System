import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

DATA_DIR = "data"
VECTOR_DIR = "vectorstore"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def load_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages])
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def build_vectorstore():
    texts = []
    for file in os.listdir(DATA_DIR):
        text = load_text(os.path.join(DATA_DIR, file))
        texts.extend(chunk_text(text))

    if not texts:
        return

    embeddings = model.encode(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, f"{VECTOR_DIR}/index.faiss")
    with open(f"{VECTOR_DIR}/chunks.pkl", "wb") as f:
        pickle.dump(texts, f)

def retrieve(query, k=4):
    index = faiss.read_index(f"{VECTOR_DIR}/index.faiss")
    with open(f"{VECTOR_DIR}/chunks.pkl", "rb") as f:
        texts = pickle.load(f)

    q_emb = model.encode([query])
    _, idxs = index.search(q_emb, k)
    return [texts[i] for i in idxs[0]]
