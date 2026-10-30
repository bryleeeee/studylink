# StudyLink

A platform where students upload research, get an automatic summary on the front page, and find related work through semantic search. Study recruitment with profile-based matching is planned as a second feature. See the [project scope doc] for the full plan, phases, and data model.

## Structure

```
studylink/
  backend/   FastAPI + SQLAlchemy + Alembic, Postgres (Supabase) with pgvector
  frontend/  Next.js (TypeScript)
```

## Phase 1 setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Supabase project (free tier is enough to start)

### 1. Supabase project

1. Create a project at https://supabase.com.
2. Copy the connection string from Project Settings > Database > Connection string (URI, use the "Session pooler" or direct connection, not the pgbouncer transaction pooler, since Alembic needs a direct connection for DDL).
3. Tables are created by Alembic (`alembic upgrade head`, step 2 below) — don't run anything in the SQL editor first, it will create `users`, `profiles`, `documents`, `document_embeddings`, and enable the `vector` extension.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # fill in DATABASE_URL from Supabase
alembic upgrade head       # creates tables + enables pgvector
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs once running.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

App at http://localhost:3000.

## Notes

- The backend writes its own SQL queries (SQLAlchemy Core/ORM), rather than relying on Supabase's auto-generated REST API or client libraries. Supabase here is just hosted Postgres, auth, and file storage.
- pgvector is enabled in the first migration. Embedding dimension is set to 384 for a small sentence-transformers model to start (`all-MiniLM-L6-v2`); change the column dimension in a new migration if a different model is chosen later.
