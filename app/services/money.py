from decimal import Decimal

def dollars_to_cents(value: str) -> int:
    """
    Converts '$130.00 ' -> 13000
    """
    cleaned = value.replace("$", "").strip()
    return int(Decimal(cleaned) * 100)
