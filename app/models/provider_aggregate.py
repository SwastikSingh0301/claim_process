from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

def utc_now() -> datetime:
    """Get current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)

class ProviderNetFeeAggregate(SQLModel, table=True):
    __tablename__ = "provider_net_fee_aggregate"

    provider_npi: str = Field(primary_key=True)
    total_net_fee_cents: int
    updated_at: datetime = Field(default_factory=utc_now)
