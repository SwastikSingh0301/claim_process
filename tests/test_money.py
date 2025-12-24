"""
Tests for money conversion utilities.
"""
import pytest
from app.services.money import dollars_to_cents


def test_dollars_to_cents_basic():
    """Test basic dollar to cents conversion."""
    assert dollars_to_cents("100.00") == 10000
    assert dollars_to_cents("50.50") == 5050
    assert dollars_to_cents("0.01") == 1
    assert dollars_to_cents("0.00") == 0


def test_dollars_to_cents_with_dollar_sign():
    """Test conversion with dollar sign prefix."""
    assert dollars_to_cents("$100.00") == 10000
    assert dollars_to_cents("$50.50") == 5050
    assert dollars_to_cents("$0.00") == 0


def test_dollars_to_cents_with_whitespace():
    """Test conversion with whitespace."""
    assert dollars_to_cents(" 100.00 ") == 10000
    assert dollars_to_cents("$ 50.50 ") == 5050


def test_dollars_to_cents_large_amounts():
    """Test conversion with large amounts."""
    assert dollars_to_cents("1000.00") == 100000
    assert dollars_to_cents("999999.99") == 99999999


def test_dollars_to_cents_no_decimal():
    """Test conversion without decimal places."""
    assert dollars_to_cents("100") == 10000
    assert dollars_to_cents("50") == 5000


def test_dollars_to_cents_single_decimal():
    """Test conversion with single decimal place."""
    assert dollars_to_cents("100.5") == 10050
    assert dollars_to_cents("50.1") == 5010

