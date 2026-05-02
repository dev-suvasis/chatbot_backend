import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

# ---------- LOAD ENV ----------
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

INDEX_NAME = "rag-saas"

# ---------- EMBEDDINGS ----------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ✅ BETTER CHUNKING
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)

# ---------- PINECONE ----------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ---------- LLM ----------
chat_model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    max_tokens=512,
    api_key=GROQ_API_KEY,
)

# ---------- HELPER ----------
def get_vectorstore(user_id: str):
    return PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=user_id
    )

# ---------- ADD DOCUMENTS ----------
def add_documents_to_db(documents: list[Document], user_id: str):
    try:
        split_docs = text_splitter.split_documents(documents)

        print(f"📄 Split docs count: {len(split_docs)}")

        for doc in split_docs:
            doc.metadata = {
                "source": "file",
                "user_id": user_id
            }

        vectorstore = get_vectorstore(user_id)
        vectorstore.add_documents(split_docs)

        print(f"✅ Stored documents for user: {user_id}")

    except Exception as e:
        print("❌ Error storing documents:", str(e))
        raise e


# ---------- CHAT ----------
def get_response(query: str, user_id: str) -> dict:
    try:
        vectorstore = get_vectorstore(user_id)

        # 🔍 Retrieve with scores
        results = vectorstore.similarity_search_with_score(query, k=5)

        print(f"\n🔍 Query: {query}")
        print(f"🔍 Retrieved: {len(results)} results")

        for doc, score in results:
            print(f"➡️ Score: {score:.4f} | Text: {doc.page_content[:80]}")

        # ✅ Take top 2 most relevant chunks only
        top_docs = [doc for doc, _ in results[:2]]

        if not top_docs:
            return {
                "answer": "I don't know based on the provided knowledge base.",
                "source": "kb",
                "context_preview": ""
            }

        # Build context
        context = "\n\n".join([doc.page_content for doc in top_docs])

        # ✅ Improved prompt
        prompt = f"""
        You are an AI assistant.

        Answer clearly and concisely using the context.

        - If answer exists, respond in 1-2 sentences.
        - If implied, explain briefly.
        - Do NOT hallucinate.

        Context:
        {context}

        Question:
        {query}

        Answer:
        """

        response = chat_model.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

        return {
            "answer": answer,
            "source": "kb",
            "context_preview": context[:300]
        }

    except Exception as e:
        print("❌ Error in get_response:", str(e))
        return {
            "answer": "Something went wrong.",
            "source": "error",
            "context_preview": ""
        }