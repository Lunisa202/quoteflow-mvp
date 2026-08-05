"""Integration tests for workflow routing logic.

These tests verify the graph routing decisions WITHOUT an LLM.
They test the deterministic routing functions directly.
"""

import pytest
from backend.workflow.graph import route_after_validation, route_after_calculation


class TestRouteAfterValidation:
    """Test conditional routing after the validation node."""

    def test_route_to_clarification_unknown_client(self):
        state = {
            "validation_result": {
                "client_known": False,
                "all_products_known": True,
                "stock_available": True,
            },
            "extracted_data": {"missing_fields": []},
        }
        assert route_after_validation(state) == "clarification"

    def test_route_to_clarification_missing_fields(self):
        state = {
            "validation_result": {
                "client_known": True,
                "all_products_known": True,
                "stock_available": True,
            },
            "extracted_data": {"missing_fields": ["quantity", "delivery_location"]},
        }
        assert route_after_validation(state) == "clarification"

    def test_route_to_blocked_unknown_product(self):
        state = {
            "validation_result": {
                "client_known": True,
                "all_products_known": False,
                "stock_available": True,
            },
            "extracted_data": {"missing_fields": []},
        }
        assert route_after_validation(state) == "blocked"

    def test_route_to_blocked_no_stock(self):
        state = {
            "validation_result": {
                "client_known": True,
                "all_products_known": True,
                "stock_available": False,
            },
            "extracted_data": {"missing_fields": []},
        }
        assert route_after_validation(state) == "blocked"

    def test_route_to_calculation_valid(self):
        state = {
            "validation_result": {
                "client_known": True,
                "all_products_known": True,
                "stock_available": True,
            },
            "extracted_data": {"missing_fields": []},
        }
        assert route_after_validation(state) == "calculation"


class TestRouteAfterCalculation:
    """Test conditional routing after the calculation node."""

    def test_route_to_approval_high_total(self):
        state = {
            "quotation": {"requires_approval": True, "grand_total": 15000},
            "validation_result": {"requires_approval": False},
        }
        assert route_after_calculation(state) == "approval"

    def test_route_to_approval_discount_exception(self):
        state = {
            "quotation": {"requires_approval": False, "grand_total": 5000},
            "validation_result": {"requires_approval": True},
        }
        assert route_after_calculation(state) == "approval"

    def test_route_to_draft_no_approval_needed(self):
        state = {
            "quotation": {"requires_approval": False, "grand_total": 5000},
            "validation_result": {"requires_approval": False},
        }
        assert route_after_calculation(state) == "draft"
