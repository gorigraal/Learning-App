# Learning-App Backend

## Setup

1. Copiaza `.env.example` in `.env` si completeaza cheile (ANTHROPIC_API_KEY, OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY).
2. In Supabase, mergi la SQL Editor si ruleaza scriptul din `app/db/schema.sql` (activeaza pgvector, creeaza tabelele si functia de search).
3. Porneste serverul:

```bash
uvicorn app.main:app --reload
```

4. Documentatia interactiva e disponibila la `http://localhost:8000/docs`.

## Structura

```
app/
├── main.py              # entrypoint FastAPI
├── config.py             # citeste .env, settings
├── routers/
│   ├── chat.py           # POST /api/chat
│   └── materials.py      # POST /api/materials/upload
├── services/
│   ├── ingestion.py       # extragere text din PDF/Word/PNG + chunking
│   ├── embeddings.py      # generare embeddings (OpenAI)
│   ├── retrieval.py       # similarity search in Supabase
│   └── llm.py             # apel Claude API + system prompt socratic
├── models/
│   └── schemas.py         # Pydantic models
└── db/
    ├── supabase_client.py
    └── schema.sql          # script SQL de rulat manual in Supabase
```

## Endpoint-uri

- `POST /api/materials/upload` - upload fisier (PDF/DOCX/PNG) + subject, extrage text, genereaza embeddings, salveaza in Supabase.
- `POST /api/chat` - trimite o intrebare + subject + istoric conversatie, primeste raspuns ghidat socratic.

## De facut inainte de productie

- Adauga autentificare (Supabase Auth) pe ambele endpoint-uri.
- Adauga rate limiting per user (limite freemium).
- Adauga validare a marimii fisierelor incarcate.
- Configureaza CORS cu domeniul real de productie.
