from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    """Get current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)

class Claim(SQLModel, table=True):
    __tablename__ = "claims"
    
    # Primary key - UUID is auto-generated
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    claim_reference: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=utc_now)
