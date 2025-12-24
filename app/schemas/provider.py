from pydantic import BaseModel

class TopProviderResponse(BaseModel):
    provider_npi: str
    total_net_fee_cents: int
