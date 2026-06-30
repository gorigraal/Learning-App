import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Gemini 
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # RAG
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    TOP_K: int = int(os.getenv("TOP_K", "5"))

    def validate(self):
        missing = [
            name
            for name in ["GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
            if not getattr(self, name)
        ]
        if missing:
            raise RuntimeError(
                f"Lipsesc variabile de environment in .env: {', '.join(missing)}"
            )


settings = Settings()