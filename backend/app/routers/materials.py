from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.schemas import MaterialUploadResponse
from app.services.ingestion import extract_text, chunk_text
from app.services.embeddings import embed_chunks
from app.db.supabase_client import get_supabase

router = APIRouter()


@router.post("/upload", response_model=MaterialUploadResponse)
async def upload_material(
    file: UploadFile = File(...),
    subject: str = Form(...),
    user_id: Optional[str] = Form(None),
):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ("pdf", "docx", "png", "jpg", "jpeg"):
        raise HTTPException(status_code=400, detail=f"Tip de fisier nesuportat: {file_ext}")

    try:
        file_bytes = await file.read()
        text = extract_text(file_bytes, file_ext)
        chunks = chunk_text(text)

        if not chunks:
            raise HTTPException(status_code=400, detail="Nu s-a putut extrage text din fisier")

        embeddings = embed_chunks(chunks)

        supabase = get_supabase()

        material_row = {"filename": file.filename, "subject": subject, "source_type": "user_uploaded"}
        if user_id:
            material_row["user_id"] = user_id

        material = supabase.table("materials").insert(material_row).execute()
        material_id = material.data[0]["id"]

        rows = [
            {
                "material_id": material_id,
                "content": chunk,
                "embedding": embedding,
                "subject": subject,
                "source_type": "user_uploaded",
                "user_id": user_id,
            }
            for chunk, embedding in zip(chunks, embeddings)
        ]
        supabase.table("materials_chunks").insert(rows).execute()

        return MaterialUploadResponse(
            material_id=material_id,
            filename=file.filename,
            chunks_created=len(chunks),
            subject=subject,
            user_id=user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
