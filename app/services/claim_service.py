from sqlmodel import Session
from uuid import uuid4

from app.models.claim import Claim
from app.models.claim_line import ClaimLine
from app.repositories.claim_repo import ClaimRepository
from app.repositories.claim_service_line_repo import ClaimServiceLineRepository
from app.repositories.provider_aggregate_repo import ProviderAggregateRepository
from app.services.money import dollars_to_cents
from app.services.validation import (
    SUBMITTED_PROCEDURE_RULE,
    PROVIDER_NPI_RULE,
)

class ClaimService:
    def __init__(self, session: Session):
        self.session = session
        self.claim_repo = ClaimRepository(session)
        self.line_repo = ClaimServiceLineRepository(session)
        self.provider_agg_repo = ProviderAggregateRepository(session)

    def process_claim(self, payload: dict) -> Claim:
        """
        Orchestrates full claim processing in a single transaction.
        """

        claim = Claim(
            id=uuid4(),
            claim_reference=payload.get("claim_reference"),
        )

        self.claim_repo.create(claim)

        service_lines: list[ClaimLine] = []

        for line in payload["lines"]:
            # ---- Validation ----
            SUBMITTED_PROCEDURE_RULE.validate(line["submitted_procedure"])
            PROVIDER_NPI_RULE.validate(line["provider_npi"])

            # ---- Money parsing ----
            provider_fees = dollars_to_cents(line["provider_fees"])
            allowed_fees = dollars_to_cents(line["allowed_fees"])
            coinsurance = dollars_to_cents(line["member_coinsurance"])
            copay = dollars_to_cents(line["member_copay"])

            # ---- Net fee computation ----
            net_fee = provider_fees + coinsurance + copay - allowed_fees

            service_line = ClaimLine(
                claim_id=claim.id,
                service_date=line["service_date"],
                plan_group=line["plan_group"],
                subscriber_id=line["subscriber_id"],
                provider_npi=line["provider_npi"],
                submitted_procedure=line["submitted_procedure"],
                quadrant=line.get("quadrant"),
                provider_fees_cents=provider_fees,
                allowed_fees_cents=allowed_fees,
                member_coinsurance_cents=coinsurance,
                member_copay_cents=copay,
                net_fee_cents=net_fee,
            )

            service_lines.append(service_line)

            # ---- Aggregate update ----
            self.provider_agg_repo.increment_net_fee(
                provider_npi=line["provider_npi"],
                delta_cents=net_fee,
            )

        self.line_repo.bulk_create(service_lines)

        # After successful claim processing, a downstream payments service
        # should be notified about computed net fees.
        #
        # Proposed approach: Outbox pattern with asynchronous message publishing
        # to ensure reliability, idempotency, and safe retries.

        return claim
