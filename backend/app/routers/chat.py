from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.retrieval import retrieve_relevant_chunks
from app.services.llm import generate_response

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        chunks = retrieve_relevant_chunks(request.query, request.subject, user_id=request.user_id)
        response_text = generate_response(request.query, chunks, request.history)
        return ChatResponse(response=response_text, sources_used=len(chunks))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
