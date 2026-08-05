"""Unit tests for deterministic domain services.

These tests verify business logic WITHOUT any LLM dependency.
They are fully reproducible and fast.
"""

import pytest
from backend.domain.services import (
    get_client,
    is_known_client,
    get_product,
    is_known_product,
    find_product_by_name,
    check_stock,
    calculate_line_total,
    calculate_quote_total,
    get_max_discount,
    get_auto_approve_discount,
    validate_discount,
    requires_approval,
)


# --- Client Tests ---

class TestClientServices:
    def test_get_known_client(self):
        client = get_client("CLI-001")
        assert client is not None
        assert client["name"] == "Minera del Sur SAC"
        assert client["tier"] == "gold"

    def test_get_unknown_client(self):
        client = get_client("CLI-999")
        assert client is None

    def test_is_known_client(self):
        assert is_known_client("CLI-001") is True
        assert is_known_client("UNKNOWN") is False


# --- Product Tests ---

class TestProductServices:
    def test_get_known_product(self):
        product = get_product("HX-200")
        assert product is not None
        assert product["name"] == "Industrial Safety Helmet HX-200"
        assert product["unit_price"] == 45.00

    def test_get_unknown_product(self):
        assert get_product("XYZ-000") is None

    def test_is_known_product(self):
        assert is_known_product("HX-200") is True
        assert is_known_product("FAKE") is False

    def test_find_product_by_name(self):
        product = find_product_by_name("helmet")
        assert product is not None
        assert product["sku"] == "HX-200"

    def test_find_product_by_partial_name(self):
        product = find_product_by_name("welding")
        assert product is not None
        assert product["sku"] == "WL-100"

    def test_find_unknown_product(self):
        assert find_product_by_name("spaceship") is None


# --- Inventory Tests ---

class TestInventoryServices:
    def test_stock_available(self):
        result = check_stock("HX-200", "Lima", 50)
        assert result["available"] is True
        assert result["stock"] >= 50

    def test_stock_insufficient(self):
        result = check_stock("WL-100", "Arequipa", 100)
        assert result["available"] is False
        assert result["shortage"] > 0

    def test_stock_unknown_product(self):
        result = check_stock("FAKE-001", "Lima", 1)
        assert result["available"] is False


# --- Pricing Tests ---

class TestPricingServices:
    def test_calculate_line_total_no_discount(self):
        result = calculate_line_total("HX-200", 20, 0)
        assert result["unit_price"] == 45.00
        assert result["subtotal"] == 900.00
        assert result["discount_amount"] == 0.00
        assert result["line_total"] == 900.00

    def test_calculate_line_total_with_discount(self):
        result = calculate_line_total("HX-200", 20, 8.0)
        assert result["subtotal"] == 900.00
        assert result["discount_pct"] == 8.0
        assert result["discount_amount"] == 72.00
        assert result["line_total"] == 828.00

    def test_calculate_line_total_unknown_product(self):
        result = calculate_line_total("FAKE", 10, 0)
        assert "error" in result

    def test_calculate_quote_total(self):
        items = [
            {"sku": "HX-200", "quantity": 20, "discount_pct": 5.0},
            {"sku": "BT-500", "quantity": 10, "discount_pct": 5.0},
        ]
        result = calculate_quote_total(items)
        assert "error" not in result
        assert len(result["lines"]) == 2
        assert result["currency"] == "USD"
        # HX-200: 20 * 45 = 900, discount 45 -> 855
        # BT-500: 10 * 89 = 890, discount 44.5 -> 845.5
        assert result["grand_total"] == 1700.50

    def test_calculate_quote_total_unknown_product(self):
        items = [{"sku": "FAKE", "quantity": 1, "discount_pct": 0}]
        result = calculate_quote_total(items)
        assert "error" in result


# --- Policy Tests ---

class TestPolicyServices:
    def test_max_discount_by_tier(self):
        assert get_max_discount("platinum") == 15.0
        assert get_max_discount("gold") == 10.0
        assert get_max_discount("silver") == 7.0
        assert get_max_discount("standard") == 5.0

    def test_auto_approve_discount(self):
        assert get_auto_approve_discount("gold") == 8.0
        assert get_auto_approve_discount("silver") == 5.0

    def test_validate_discount_within_auto_approve(self):
        result = validate_discount("gold", 5.0)
        assert result["allowed"] is True
        assert result["requires_approval"] is False

    def test_validate_discount_needs_approval(self):
        # Gold auto-approve is 8%, requesting 9% (within max 10% but above auto)
        result = validate_discount("gold", 9.0)
        assert result["allowed"] is True
        assert result["requires_approval"] is True

    def test_validate_discount_exceeds_max(self):
        # Gold max is 10%, requesting 12%
        result = validate_discount("gold", 12.0)
        assert result["allowed"] is False
        assert result["requires_approval"] is True

    def test_validate_no_discount(self):
        result = validate_discount("standard", 0)
        assert result["allowed"] is True
        assert result["requires_approval"] is False


# --- Approval Threshold Tests ---

class TestApprovalThreshold:
    def test_below_threshold(self):
        discount_val = {"requires_approval": False}
        result = requires_approval(5000.00, discount_val)
        assert result["required"] is False

    def test_above_threshold(self):
        discount_val = {"requires_approval": False}
        result = requires_approval(15000.00, discount_val)
        assert result["required"] is True
        assert any("10,000" in r for r in result["reasons"])

    def test_discount_exception(self):
        discount_val = {
            "requires_approval": True,
            "reason": "Discount 9% exceeds auto-approve limit",
        }
        result = requires_approval(5000.00, discount_val)
        assert result["required"] is True

    def test_both_conditions(self):
        discount_val = {
            "requires_approval": True,
            "reason": "Discount exception",
        }
        result = requires_approval(15000.00, discount_val)
        assert result["required"] is True
        assert len(result["reasons"]) == 2
