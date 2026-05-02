from langchain_core.documents import Document
from rag import add_documents_to_db, get_response

user_id = "test_user"

# Add document
docs = [
    Document(page_content="FastAPI is a modern Python web framework.")
]

add_documents_to_db(docs, user_id)

# Query
response = get_response("What is FastAPI?", user_id)

print(response)