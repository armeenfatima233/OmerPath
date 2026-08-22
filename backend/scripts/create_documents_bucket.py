"""One-time setup: create the private Supabase Storage bucket for documents.

Run manually, once, from backend/: PYTHONPATH=. ../.venv/Scripts/python.exe scripts/create_documents_bucket.py
Safe to re-run - checks for existing bucket first.
"""
from app.supabase_client import supabase

BUCKET_NAME = "documents"


def run() -> None:
    existing = supabase.storage.list_buckets()
    if any(b.name == BUCKET_NAME for b in existing):
        print(f"Bucket '{BUCKET_NAME}' already exists, skipping.")
        return
    supabase.storage.create_bucket(
        BUCKET_NAME,
        options={"public": False},
    )
    print(f"Created private bucket '{BUCKET_NAME}'.")


if __name__ == "__main__":
    run()
