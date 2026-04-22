from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
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


# ---------- SINGLE CHAT ENDPOINT ----------
@app.post("/chat")
async def chat(
    query: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        # ---------- HANDLE FILE (OPTIONAL) ----------
        if file:
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
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

                # ✅ Add to in-memory DB (NO persistence)
                add_documents_to_db(documents)

        # ---------- GET RESPONSE ----------
        result = get_response(query)

        return {
            "answer": result["answer"],
            "source": result["source"]
        }

    except Exception as e:
        return {"error": str(e)}