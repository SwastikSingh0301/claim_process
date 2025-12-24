import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schemas.claim import (
    ClaimCreateRequest,
    ClaimCreateResponse,
)
from app.db.session import get_session
from app.services.claim_service import ClaimService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("/", response_model=ClaimCreateResponse)
def create_claim(
    request: ClaimCreateRequest,
    session: Session = Depends(get_session),
):
    try:
        with session.begin():
            service = ClaimService(session)
            claim = service.process_claim(request.model_dump())
        logger.info(f"Successfully processed claim {claim.id}")
        return ClaimCreateResponse(claim_id=claim.id)
    except ValueError as e:
        # validation errors
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to process claim: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process claim",
        )
