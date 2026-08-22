import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.advisor import (
    AdvisorConfigError,
    AdvisorNotFoundError,
    AdvisorProviderError,
    build_context_text,
    run_advisor_chat,
)
from app.database import get_db
from app.schemas.advisor import AdvisorChatRequest, AdvisorChatResponse
from app.routes.auth import get_authenticated_session

logger = logging.getLogger("omerpath.advisor")

router = APIRouter(
    prefix="/api/advisor",
    tags=["Advisor"],
)


@router.post("/chat", response_model=AdvisorChatResponse)
def advisor_chat(
    payload: AdvisorChatRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AdvisorChatResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message is required.")

    try:
        context_text, scholarship_map, application_map = build_context_text(
            db, user_id, payload.scholarship_id, payload.application_id,
        )
    except AdvisorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    history = [{"role": h.role, "content": h.content} for h in payload.history]

    try:
        result = run_advisor_chat(message, history, context_text, scholarship_map, application_map)
    except AdvisorConfigError as exc:
        logger.error("Advisor unavailable due to configuration | type=%s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI Advisor is not available right now.",
        )
    except AdvisorProviderError as exc:
        logger.error("Advisor provider failure | type=%s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI Advisor is temporarily unavailable. Please try again.",
        )

    return AdvisorChatResponse(
        answer=result.answer,
        warnings=result.warnings,
        unknowns=result.unknowns,
        referenced_scholarships=result.referenced_scholarships,
        referenced_applications=result.referenced_applications,
    )
