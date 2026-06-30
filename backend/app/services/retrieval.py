from typing import TypedDict

from app.db.supabase_client import get_supabase
from app.services.embeddings import embed_query
from app.config import settings


class ChunkResult(TypedDict):
    content: str
    source_type: str  # "official" | "user_uploaded"


def retrieve_relevant_chunks(
    query: str,
    subject: str,
    top_k: int = settings.TOP_K,
    user_id: str | None = None,
) -> list[ChunkResult]:
    """Gaseste cele mai relevante chunk-uri filtrate pe subject.
    Combina materialele oficiale cu cele personale ale userului daca user_id e furnizat.
    Returneaza dictionare cu 'content' si 'source_type' pentru fiecare chunk."""
    query_embedding = embed_query(query)
    supabase = get_supabase()

    params: dict = {
        "query_embedding": query_embedding,
        "match_subject": subject,
        "match_count": top_k,
    }
    if user_id is not None:
        params["match_user_id"] = user_id

    result = supabase.rpc("match_chunks", params).execute()

    if not result.data:
        return []

    return [
        ChunkResult(content=row["content"], source_type=row.get("source_type", "official"))
        for row in result.data
    ]
