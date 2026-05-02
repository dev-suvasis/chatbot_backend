from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import tempfile

from rag import get_response, add_documents_to_db

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- ROOT ----------
@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API is running 🚀"}


# ---------- REQUEST MODEL ----------
class ChatRequest(BaseModel):
    message: str


# ---------- CHAT ENDPOINT (JSON) ----------
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = "test_user"  # temporary until auth added

    result = get_response(req.message, user_id)

    return {
        "answer": result["answer"],
        "source": result["source"]
    }


# ---------- FILE UPLOAD ENDPOINT ----------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        user_id = "test_user"  # temporary

        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()

            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(tmp.name)
            elif file.filename.endswith(".txt"):
                loader = TextLoader(tmp.name)
            else:
                return {"error": "Only PDF and TXT supported"}

            documents = loader.load()

            add_documents_to_db(documents, user_id)

        return {"message": "File uploaded and processed successfully"}

    except Exception as e:
        return {"error": str(e)}