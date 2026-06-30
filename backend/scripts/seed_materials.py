"""
Script de seed pentru materialele oficiale.

Parcurge backend/materials/<Subject>/ si incarca fisierele in Supabase
cu source_type="official". Idempotent: fisierele deja existente sunt sarite.

Utilizare:
    cd backend
    python scripts/seed_materials.py                     # toate materiile
    python scripts/seed_materials.py --subject Matematica  # doar o materie
"""

import argparse
import os
import sys

# Asigura ca pachetul `app` e importabil indiferent de directorul de lucru
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.supabase_client import get_supabase
from app.services.ingestion import extract_text, chunk_text
from app.services.embeddings import embed_chunks

MATERIALS_DIR = os.path.join(os.path.dirname(__file__), "..", "materials")
SUPPORTED_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg"}


def already_seeded(supabase, filename: str, subject: str) -> bool:
    result = (
        supabase.table("materials")
        .select("id")
        .eq("filename", filename)
        .eq("subject", subject)
        .eq("source_type", "official")
        .execute()
    )
    return bool(result.data)


def seed_file(supabase, filepath: str, subject: str) -> None:
    filename = os.path.basename(filepath)
    file_ext = filename.rsplit(".", 1)[-1].lower()

    if file_ext not in SUPPORTED_EXTENSIONS:
        print(f"  [SKIP] {filename} — extensie nesupotata ({file_ext})")
        return

    if already_seeded(supabase, filename, subject):
        print(f"  [SKIP] {filename} — deja incarcat")
        return

    print(f"  [PROC] {filename} ...")

    with open(filepath, "rb") as f:
        file_bytes = f.read()

    text = extract_text(file_bytes, file_ext)
    chunks = chunk_text(text)

    if not chunks:
        print(f"  [WARN] {filename} — text gol, sarit")
        return

    embeddings = embed_chunks(chunks)

    material = (
        supabase.table("materials")
        .insert({"filename": filename, "subject": subject, "source_type": "official", "user_id": None})
        .execute()
    )
    material_id = material.data[0]["id"]

    rows = [
        {
            "material_id": material_id,
            "content": chunk,
            "embedding": embedding,
            "subject": subject,
            "source_type": "official",
            "user_id": None,
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]
    supabase.table("materials_chunks").insert(rows).execute()

    print(f"  [OK]   {filename} — {len(chunks)} chunk-uri salvate")


def seed_subject(supabase, subject_dir: str, subject: str) -> None:
    print(f"\n=== {subject} ===")
    entries = sorted(os.listdir(subject_dir))
    if not entries:
        print("  (folder gol)")
        return
    for entry in entries:
        filepath = os.path.join(subject_dir, entry)
        if os.path.isfile(filepath):
            seed_file(supabase, filepath, subject)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed materiale oficiale in Supabase")
    parser.add_argument("--subject", help="Proceseaza doar materia specificata (ex: Matematica)")
    args = parser.parse_args()

    materials_path = os.path.abspath(MATERIALS_DIR)
    if not os.path.isdir(materials_path):
        print(f"[EROARE] Folderul de materiale nu exista: {materials_path}")
        sys.exit(1)

    supabase = get_supabase()

    if args.subject:
        subject_dir = os.path.join(materials_path, args.subject)
        if not os.path.isdir(subject_dir):
            print(f"[EROARE] Nu exista subfolder pentru materia '{args.subject}' in {materials_path}")
            sys.exit(1)
        seed_subject(supabase, subject_dir, args.subject)
    else:
        subjects = sorted(
            entry for entry in os.listdir(materials_path)
            if os.path.isdir(os.path.join(materials_path, entry))
        )
        if not subjects:
            print("[INFO] Nu exista subfoldere in", materials_path)
            return
        for subject in subjects:
            seed_subject(supabase, os.path.join(materials_path, subject), subject)

    print("\n[DONE] Seed complet.")


if __name__ == "__main__":
    main()
