from sqlmodel import Session
from app.models.claim import Claim
from uuid import UUID
from typing import Optional

class ClaimRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, claim: Claim) -> Claim:
        self.session.add(claim)
        self.session.flush()  # ensures ID is generated
        return claim

    def get_by_id(self, claim_id: UUID) -> Optional[Claim]:
        return self.session.get(Claim, claim_id)
