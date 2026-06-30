from google import genai
from google.genai import types
from app.config import settings

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Genereaza embeddings pentru o lista de chunk-uri de text, folosind Gemini."""
    if not chunks:
        return []

    client = get_gemini_client()
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=chunks,
        # fortam 1536 dimensiuni ca sa ramana compatibil cu schema SQL existenta
        # (gemini-embedding-001 are implicit 3072, dar suporta trunchiere configurabila)
        config=types.EmbedContentConfig(output_dimensionality=1536),
    )
    return [embedding.values for embedding in result.embeddings]


def embed_query(query: str) -> list[float]:
    """Genereaza embedding pentru o singura interogare (intrebarea elevului)."""
    return embed_chunks([query])[0]