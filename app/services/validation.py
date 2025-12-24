import re
from typing import Protocol, Any, Optional


class ValidationRule(Protocol):
    """Protocol for validation rules - allows extensible validation framework."""
    def validate(self, value: Any) -> None: ...


class RegexRule:
    """Validates a string value against a regex pattern."""
    
    def __init__(self, pattern: str, message: str):
        self.pattern = re.compile(pattern)
        self.message = message

    def validate(self, value: str) -> None:
        if not self.pattern.match(value):
            raise ValueError(self.message)


class RequiredFieldRule:
    """Validates that a required field is present and not empty."""
    
    def __init__(self, field_name: str):
        self.field_name = field_name
    
    def validate(self, value: Any) -> None:
        if value is None:
            raise ValueError(f"{self.field_name} is required")
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{self.field_name} cannot be empty")


class FieldValidator:
    """Composite validator that applies multiple rules to a field."""
    
    def __init__(self, field_name: str, rules: list[ValidationRule]):
        self.field_name = field_name
        self.rules = rules
    
    def validate(self, value: Any) -> None:
        """Apply all validation rules to the value."""
        for rule in self.rules:
            rule.validate(value)


# Predefined validation rules
SUBMITTED_PROCEDURE_RULE = RegexRule(
    r"^D.*",
    "submitted_procedure must start with 'D'",
)

PROVIDER_NPI_RULE = RegexRule(
    r"^\d{10}$",
    "provider_npi must be a 10 digit number",
)

