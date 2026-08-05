"""Tests for idempotency - same decision must not produce duplicate effects."""

import pytest
from backend.domain.services import (
    calculate_line_total,
    calculate_quote_total,
    validate_discount,
    requires_approval,
)


class TestIdempotency:
    """Verify that domain functions are pure and idempotent."""

    def test_calculate_line_total_idempotent(self):
        """Same inputs always produce same outputs."""
        result1 = calculate_line_total("HX-200", 20, 8.0)
        result2 = calculate_line_total("HX-200", 20, 8.0)
        assert result1 == result2

    def test_calculate_quote_total_idempotent(self):
        """Quote calculation is deterministic."""
        items = [
            {"sku": "HX-200", "quantity": 10, "discount_pct": 5.0},
            {"sku": "BT-500", "quantity": 5, "discount_pct": 3.0},
        ]
        result1 = calculate_quote_total(items)
        result2 = calculate_quote_total(items)
        assert result1 == result2

    def test_validate_discount_idempotent(self):
        """Discount validation is deterministic."""
        result1 = validate_discount("gold", 9.0)
        result2 = validate_discount("gold", 9.0)
        assert result1 == result2

    def test_requires_approval_idempotent(self):
        """Approval check is deterministic."""
        discount_val = {"requires_approval": True, "reason": "test"}
        result1 = requires_approval(15000, discount_val)
        result2 = requires_approval(15000, discount_val)
        assert result1 == result2
