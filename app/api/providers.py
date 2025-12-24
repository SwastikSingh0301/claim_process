from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.rate_limiter import limiter
from app.core.config import settings
from app.db.session import get_session
from app.models.provider_aggregate import ProviderNetFeeAggregate
from app.schemas.provider import TopProviderResponse

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get(
    "/top",
    response_model=list[TopProviderResponse],
    summary="Get top 10 providers by net fees",
    description="""
    Returns the top 10 provider NPIs ranked by total net fees generated.

    ### Implementation Overview

    This endpoint uses a **pre-aggregated table** (`provider_net_fee_aggregate`) that
    maintains the running total of net fees per provider. The aggregate is updated
    incrementally during claim processing within the same database transaction.

    ### Performance Characteristics

    - **Write Path**: O(1) per claim line (indexed upsert by provider_npi)
    - **Read Path**: O(P log P), where P is the number of unique providers
    - Avoids expensive runtime aggregation over claim lines

    ### Consistency & Concurrency

    - Aggregate updates are performed atomically within database transactions
    - Safe under concurrent claim processing across multiple service instances

    ### Rate Limiting

    This endpoint is rate-limited to prevent abuse and ensure predictable performance.
    """,
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def top_providers(
    request: Request, 
    session: Session = Depends(get_session),
):
    """
    Returns the top 10 provider NPIs by total net fees.
    
    The implementation uses a pre-aggregated table that is updated
    incrementally during claim processing, allowing for O(P log P) query
    performance where P is the number of providers (typically much smaller
    than the number of claim lines).
    """
    stmt = (
        select(ProviderNetFeeAggregate)
        .order_by(ProviderNetFeeAggregate.total_net_fee_cents.desc())
        .limit(10)
    )

    results = session.exec(stmt).all()

    return [
        TopProviderResponse(
            provider_npi=row.provider_npi,
            total_net_fee_cents=row.total_net_fee_cents,
        )
        for row in results
    ]
