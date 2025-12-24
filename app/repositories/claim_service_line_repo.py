from sqlmodel import Session
from app.models.claim_line import ClaimLine

class ClaimServiceLineRepository:
    def __init__(self, session: Session):
        self.session = session

    def bulk_create(self, lines: list[ClaimLine]) -> None:
        self.session.add_all(lines)
        self.session.flush()
