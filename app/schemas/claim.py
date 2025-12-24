from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ClaimLineInput(BaseModel):
    service_date: datetime
    submitted_procedure: str
    quadrant: Optional[str] = None
    plan_group: str
    subscriber_id: str
    provider_npi: str
    provider_fees: str
    allowed_fees: str
    member_coinsurance: str
    member_copay: str


class ClaimCreateRequest(BaseModel):
    claim_reference: Optional[str] = None
    lines: List[ClaimLineInput] = Field(min_length=1, description="At least one claim line is required")


class ClaimCreateResponse(BaseModel):
    claim_id: UUID
    message: str = "Claim processed successfully"
