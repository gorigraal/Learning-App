from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, materials

app = FastAPI(
    title="Learning-App API",
    description="Backend pentru aplicatia de invatare ghidata prin RAG + LLM",
    version="0.1.0",
)

# CORS - 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(materials.router, prefix="/api/materials", tags=["materials"])


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Learning-App API"}
