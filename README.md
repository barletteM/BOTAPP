# Glowdom Multi-Bot Reception Assistant

Full-stack starter for a multi-bot inquiry and reception assistant for Glowdom Apps.

## Bots

- Limkokwing University Bot
- IRCA-GLOWDOM AFRICA Bot
- Windhoek Municipality Bot

Each bot has separate profile data, FAQs, documents, chat sessions, and knowledge chunks. Chat retrieval is always filtered by `bot_id`, so one bot cannot answer from another bot's knowledge base.

## Stack

- FastAPI backend
- PostgreSQL with pgvector
- React and Vite frontend
- OpenAI chat completions and embeddings
- SQLAlchemy models for bot profiles, documents, FAQs, chat history, admin users, and knowledge update history

## Project Structure

```text
backend/
  app/
    api/              FastAPI routes
    core/             settings and auth
    db/               SQLAlchemy session/base
    models/           database models
    schemas/          request/response schemas
    services/         document parsing, RAG, embeddings
    main.py           API entrypoint
    seed.py           creates tables, admin user, and default bots
frontend/
  src/
    api.ts            API client
    main.tsx          pages and components
    styles.css        app styling
infra/
  init.sql            enables pgvector
docker-compose.yml   local PostgreSQL
```

## Setup

1. Start PostgreSQL:

```bash
docker compose up -d postgres
```

2. Configure the backend:

```bash
cd backend
cp .env.example .env
```

Set `OPENAI_API_KEY` in `backend/.env`. Without a key, the app still runs, but answers use simple local retrieval instead of OpenAI generation.

3. Install and seed backend:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

Default admin:

```text
Email: admin@glowdom.local
Password: ChangeMe123!
```

Change this password and `JWT_SECRET` before production use.

4. Run frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

### Local Demo Without Docker

If PostgreSQL or Docker is not available, run the backend with SQLite for a local demo:

```bash
cd backend
set DATABASE_URL=sqlite:///./glowdom_reception.db
python -m app.seed
uvicorn app.main:app --reload
```

SQLite demo mode uses the same API and per-bot data separation, but production RAG vector search should use PostgreSQL with pgvector.

## Knowledge Management

Admins can manage each bot separately:

- Upload PDF, DOCX, TXT, and CSV files
- Paste website/manual text
- Add a new version to an existing knowledge document
- Add FAQs
- Edit office hours, location, contact details, website, and bot instructions
- View chat history

Every knowledge upload creates immutable `knowledge_documents`, `knowledge_versions`, and `knowledge_chunks` rows. New information is added safely without deleting old update records.

## RAG Behavior

The chat service:

1. Loads the selected bot by slug.
2. Retrieves only FAQs and current knowledge chunks for that bot's `bot_id`.
3. Sends only that approved context to OpenAI.
4. Uses this fallback when context is missing or insufficient:

```text
I do not have confirmed information about that. Please contact the office directly.
```

## Adding More Bots

Add a new `BotProfile` row with a unique `slug`. Existing routes are generic by bot slug, so no frontend or backend rewrite is needed.

## Production Notes

- Use a strong `JWT_SECRET`.
- Replace the default admin password.
- Put the API behind HTTPS.
- Add Alembic migrations before production schema changes.
- Configure backups for PostgreSQL and uploaded files.
- Add role-based admin permissions if multiple departments will maintain different bots.
