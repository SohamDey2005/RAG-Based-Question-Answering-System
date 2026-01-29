from fastapi import FastAPI, UploadFile, File, Request
from pydantic import BaseModel
import shutil
import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

from rag_utils import build_vectorstore, retrieve
from openrouter_llm import generate_answer

# ---------------- RATE LIMITER ----------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="RAG QA System with Rate Limiting")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please slow down."}
    )

# ---------------- MODELS ----------------
class QuestionRequest(BaseModel):
    question: str

# ---------------- ENDPOINTS ----------------
@app.post("/upload")
@limiter.limit("5/minute")
async def upload(request: Request, file: UploadFile = File(...)):
    path = f"data/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    build_vectorstore()
    return {"message": "Document uploaded and indexed successfully"}

@app.post("/ask")
@limiter.limit("10/minute")
def ask(request: Request, req: QuestionRequest):
    chunks = retrieve(req.question)

    if not chunks:
        return {"answer": "No relevant context found."}

    context = "\n\n".join(chunks)

    try:
        answer = generate_answer(context, req.question)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
