-- Ruleaza acest script in Supabase SQL Editor (Project > SQL Editor > New query)

-- 1. Activeaza extensia pgvector
create extension if not exists vector;

-- 2. Tabel pentru materialele incarcate (metadata)
create table if not exists materials (
    id uuid primary key default gen_random_uuid(),
    filename text not null,
    subject text not null,
    uploaded_by uuid,  -- referinta optionala catre un tabel de useri, daca ai auth
    source_type text not null default 'user_uploaded',  -- 'official' | 'user_uploaded'
    user_id uuid,  -- null pentru materiale oficiale
    created_at timestamptz default now()
);

-- 3. Tabel pentru chunk-urile de text + embeddings
create table if not exists materials_chunks (
    id uuid primary key default gen_random_uuid(),
    material_id uuid references materials(id) on delete cascade,
    content text not null,
    embedding vector(1536),
    subject text not null,
    source_type text not null default 'user_uploaded',  -- 'official' | 'user_uploaded'
    user_id uuid,  -- null pentru materiale oficiale
    created_at timestamptz default now()
);

-- 4. Index pentru similarity search rapid
create index if not exists materials_chunks_embedding_idx
    on materials_chunks using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- 5. Index pe subject pentru filtrare rapida
create index if not exists materials_chunks_subject_idx
    on materials_chunks (subject);

-- 6. Index pe user_id pentru filtrare rapida
create index if not exists materials_chunks_user_id_idx
    on materials_chunks (user_id);

-- 7. Functie RPC pentru similarity search, filtrata pe materie.
--    Combina materialele oficiale (user_id IS NULL) cu cele personale
--    ale userului curent (user_id = match_user_id), daca match_user_id e furnizat.
--    Returneaza si source_type pentru atribuirea corecta a surselor in LLM.
create or replace function match_chunks(
    query_embedding vector(1536),
    match_subject text,
    match_count int default 5,
    match_user_id uuid default null
)
returns table (
    id uuid,
    content text,
    source_type text,
    similarity float
)
language sql stable
as $$
    select
        materials_chunks.id,
        materials_chunks.content,
        materials_chunks.source_type,
        1 - (materials_chunks.embedding <=> query_embedding) as similarity
    from materials_chunks
    where materials_chunks.subject = match_subject
      and (
          materials_chunks.user_id is null
          or (match_user_id is not null and materials_chunks.user_id = match_user_id)
      )
    order by materials_chunks.embedding <=> query_embedding
    limit match_count;
$$;
