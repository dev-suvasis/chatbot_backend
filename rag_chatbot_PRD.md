# 📄 Product Requirements Document (PRD)
## RAG-Based Multi-Tenant SaaS Chatbot

---

## 1. 🧠 Overview

This project is a multi-tenant SaaS chatbot platform powered by Retrieval-Augmented Generation (RAG).

Users can upload their own documents, and the system will create a private knowledge base for each user. The chatbot answers queries strictly based on the user's uploaded data.

---

## 2. 🎯 Objectives

- Build a scalable AI SaaS product
- Enable users to create private knowledge bases
- Ensure responses are grounded (no hallucination)
- Provide API access for integration

---

## 3. 👤 User Roles

### 3.1 End User
- Signs up / logs in
- Uploads documents
- Queries chatbot

### 3.2 Developer (API User)
- Uses API key to access chatbot
- Integrates chatbot into apps/websites

---

## 4. ⚙️ Core Features

### 4.1 Authentication
- User signup
- User login
- JWT-based authentication
- API key generation per user

### 4.2 Document Upload
- Upload PDF / TXT files
- Store raw files in Cloudinary
- Extract text from files

### 4.3 Knowledge Base Creation
- Split text into chunks
- Convert chunks into embeddings
- Store embeddings in Pinecone
- Namespace isolation per user

### 4.4 Chat System
- Query user-specific knowledge base
- Retrieve relevant chunks
- Generate response using LLM
- No web search (strict KB only)

### 4.5 Multi-Tenancy
- Each user has isolated namespace in Pinecone
- Each user has separate data in MongoDB

---

## 5. 🏗️ System Architecture

### Backend
- FastAPI

### Frontend
- Next.js

### Databases & Services
- MongoDB → Users & metadata
- Pinecone → Vector database
- Cloudinary → File storage

### AI Stack
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- LLM: Groq (LLaMA 3.1)

---

## 6. 🔄 Workflow

### Upload Flow
1. User uploads file
2. File stored in Cloudinary
3. Text extracted
4. Text split into chunks
5. Embeddings generated
6. Stored in Pinecone (user namespace)
7. Metadata saved in MongoDB

### Chat Flow
1. User sends query
2. Backend identifies user
3. Query Pinecone namespace
4. Retrieve relevant chunks
5. Pass context to LLM
6. Return response

---

## 7. 📊 Data Models

### User (MongoDB)
```
{
  user_id,
  email,
  password_hash,
  api_key,
  created_at
}
```

### File Metadata (MongoDB)
```
{
  user_id,
  file_url,
  file_name,
  uploaded_at
}
```

### Vector (Pinecone)
```
{
  text,
  user_id,
  source
}
```

---

## 8. 🔐 Security

- Password hashing (bcrypt)
- JWT authentication
- API key validation
- User-based namespace isolation

---

## 9. 🚀 Future Enhancements

- Dashboard UI
- Usage analytics
- Rate limiting
- Billing system (Stripe)
- Role-based access
- Document management UI

---

## 10. ✅ Success Metrics

- Accurate responses from KB
- Fast retrieval time
- Secure user isolation
- Scalable architecture

---

## 11. 📦 Deployment

- Backend: Render / Docker
- Frontend: Vercel
- Database: MongoDB Atlas
- Vector DB: Pinecone Cloud

---

## 12. 🧭 Scope (v1)

Included:
- Auth system
- File upload
- RAG chatbot
- Multi-tenancy

Not included:
- Payments
- Advanced analytics
- Team collaboration

---

## 📌 Conclusion

This project aims to deliver a production-ready RAG SaaS platform where users can securely build and query their own AI-powered knowledge bases.

