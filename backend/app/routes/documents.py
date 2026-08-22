import logging
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.notifications import create_notification
from app.schemas.document import DocumentDownloadResponse, DocumentResponse
from app.routes.auth import get_authenticated_session
from app.supabase_client import supabase

logger = logging.getLogger("omerpath.documents")

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)

BUCKET_NAME = "documents"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
SIGNED_URL_EXPIRY_SECONDS = 60

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
}


def _sanitize_filename(filename: str) -> str:
    safe = "".join(c for c in filename if c.isalnum() or c in "._- ")
    return safe.strip() or "file"


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    documents = db.scalars(
        select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
    ).all()
    return [DocumentResponse.model_validate(d) for d in documents]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    document_type: str = Form("Other"),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: PDF, DOCX, JPG, PNG.",
        )

    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds the 10 MB size limit.",
            )
        chunks.append(chunk)
    contents = b"".join(chunks)

    document_id = uuid.uuid4()
    safe_name = _sanitize_filename(file.filename or "file")
    storage_path = f"{user_id}/{document_id}/{safe_name}"

    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            contents,
            file_options={"content-type": file.content_type},
        )
    except Exception as exc:
        logger.error("Document upload to storage failed | type=%s", type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to store file.")

    document = Document(
        id=document_id,
        user_id=user_id,
        document_type=document_type or "Other",
        original_filename=file.filename or safe_name,
        storage_path=storage_path,
        mime_type=file.content_type,
        file_size=total_size,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    create_notification(
        db, user_id, "document_uploaded",
        "Document uploaded",
        f"{document.original_filename} was added to your Passport.",
    )

    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/download", response_model=DocumentDownloadResponse)
def get_download_url(
    document_id: UUID,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> DocumentDownloadResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    document = db.get(Document, document_id)
    if document is None or document.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    try:
        signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            document.storage_path, SIGNED_URL_EXPIRY_SECONDS
        )
    except Exception as exc:
        logger.error("Signed URL generation failed | type=%s", type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to generate download link.")

    url = signed.get("signedUrl") or signed.get("signedURL")
    if not url:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to generate download link.")
    return DocumentDownloadResponse(url=url)


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: UUID,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    document = db.get(Document, document_id)
    if document is None or document.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    storage_path = document.storage_path
    original_filename = document.original_filename
    db.delete(document)
    db.commit()

    create_notification(
        db, user_id, "document_deleted",
        "Document removed",
        f"{original_filename} was removed from your Passport.",
    )

    try:
        supabase.storage.from_(BUCKET_NAME).remove([storage_path])
    except Exception as exc:
        # Metadata is already gone - the user's document list is correct.
        # A leftover storage object with no DB reference is inert (unreachable
        # via the app) and can be cleaned up later; failing the request here
        # would incorrectly suggest the delete didn't work.
        logger.warning("Storage object cleanup failed after metadata delete | type=%s", type(exc).__name__)

    return {"message": "Document deleted."}
