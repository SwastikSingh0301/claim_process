from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session
from datetime import datetime, timezone

from app.models.provider_aggregate import ProviderNetFeeAggregate


def utc_now() -> datetime:
    """Get current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


class ProviderAggregateRepository:
    def __init__(self, session: Session):
        self.session = session
        # Detect database type from engine URL
        self.is_postgres = "postgresql" in str(session.bind.url)

    def increment_net_fee(
        self,
        provider_npi: str,
        delta_cents: int,
    ) -> None:
        if self.is_postgres:
            # PostgreSQL: Use INSERT ... ON CONFLICT DO UPDATE
            stmt = pg_insert(ProviderNetFeeAggregate).values(
                provider_npi=provider_npi,
                total_net_fee_cents=delta_cents,
                updated_at=utc_now(),
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=["provider_npi"],
                set_={
                    "total_net_fee_cents":
                        ProviderNetFeeAggregate.total_net_fee_cents
                        + stmt.excluded.total_net_fee_cents,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            self.session.execute(stmt)
        else:
            # SQLite: Use INSERT OR REPLACE or manual upsert
            existing = self.session.get(ProviderNetFeeAggregate, provider_npi)
            if existing:
                existing.total_net_fee_cents += delta_cents
                existing.updated_at = utc_now()
                self.session.add(existing)
            else:
                new_aggregate = ProviderNetFeeAggregate(
                    provider_npi=provider_npi,
                    total_net_fee_cents=delta_cents,
                    updated_at=utc_now(),
                )
                self.session.add(new_aggregate)
