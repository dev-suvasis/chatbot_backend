from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document

import os
from dotenv import load_dotenv

# ---------- LOAD ENV ----------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found")

# ---------- EMBEDDINGS ----------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------- IN-MEMORY VECTOR DB (NO PERSISTENCE) ----------
db = Chroma(
    embedding_function=embeddings
)

# ---------- TEXT SPLITTER ----------
text_splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# ---------- WEB SEARCH ----------
search = DuckDuckGoSearchRun()

# ---------- LLM ----------
chat_model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    max_tokens=512,
    api_key=groq_api_key,
)

# ---------- ADD DOCUMENTS (FROM API) ----------
def add_documents_to_db(documents):
    docs = text_splitter.split_documents(documents)
    db.add_documents(docs)

# ---------- MAIN RESPONSE FUNCTION ----------
def get_response(query: str) -> dict:

    # Step 1: similarity check
    results_with_score = db.similarity_search_with_score(query, k=1)

    use_web = False
    source = "local"
    context = ""

    if not results_with_score:
        use_web = True
    else:
        _, score = results_with_score[0]

        if score is None or score > 0.6:
            use_web = True

    # Step 2: context selection
    if use_web:
        web_result = search.run(query)
        context = f"Web Result:\n{web_result}"
        source = "web"
    else:
        results = db.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in results])

    # Step 3: prompt
    prompt = f"""
    You are a helpful AI assistant.

    Use the provided context to answer the question.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    # Step 4: LLM call
    response = chat_model.invoke([HumanMessage(content=prompt)])
    answer = response.content

    return {
        "answer": answer,
        "source": source
    }