from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    """Get current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)

class ClaimLine(SQLModel, table=True):
    __tablename__ = "claim_lines"

    id: Optional[int] = Field(default=None, primary_key=True)
    claim_id: UUID = Field(foreign_key="claims.id", index=True)

    # Required fields from CSV/API input
    service_date: datetime
    plan_group: str
    subscriber_id: str
    provider_npi: str = Field(index=True)
    submitted_procedure: str
    quadrant: Optional[str] = None

    # Financial fields (stored as integer cents)
    provider_fees_cents: int
    allowed_fees_cents: int
    member_coinsurance_cents: int
    member_copay_cents: int

    # Computed field
    net_fee_cents: int
    created_at: datetime = Field(default_factory=utc_now)
