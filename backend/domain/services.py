"""Deterministic domain services.

All business logic lives here. The LLM NEVER calculates prices,
validates stock, or applies discounts. These are pure functions.
"""

from typing import Optional
from backend.domain.data import (
    CLIENTS,
    PRODUCTS,
    INVENTORY,
    DISCOUNT_POLICIES,
    APPROVAL_THRESHOLD_USD,
    RUSH_SURCHARGE_PCT,
)


# --- CLIENT SERVICES ---

def get_client(client_id: str) -> Optional[dict]:
    """Retrieve client information by ID."""
    return CLIENTS.get(client_id)


def is_known_client(client_id: str) -> bool:
    """Check if client exists in the system."""
    return client_id in CLIENTS


# --- PRODUCT SERVICES ---

def get_product(sku: str) -> Optional[dict]:
    """Retrieve product information by SKU."""
    return PRODUCTS.get(sku)


def is_known_product(sku: str) -> bool:
    """Check if product exists in the catalog."""
    return sku in PRODUCTS


def find_product_by_name(name: str) -> Optional[dict]:
    """Fuzzy search product by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for product in PRODUCTS.values():
        if name_lower in product["name"].lower() or name_lower in product["sku"].lower():
            return product
    return None


# --- INVENTORY SERVICES ---

def check_stock(sku: str, location: str, quantity: int) -> dict:
    """Check stock availability for a product at a location.

    Returns:
        dict with keys: available (bool), stock (int), shortage (int)
    """
    product_inventory = INVENTORY.get(sku, {})
    # Try exact location first, then check all locations
    stock = product_inventory.get(location, 0)

    if stock >= quantity:
        return {"available": True, "stock": stock, "shortage": 0, "location": location}

    # Check if any location has enough
    total_stock = sum(product_inventory.values())
    return {
        "available": stock >= quantity,
        "stock": stock,
        "shortage": max(0, quantity - stock),
        "location": location,
        "total_stock_all_locations": total_stock,
    }


# --- PRICING SERVICES ---

def calculate_line_total(sku: str, quantity: int, discount_pct: float = 0.0) -> dict:
    """Calculate the total for a single line item.

    Args:
        sku: Product SKU
        quantity: Number of units
        discount_pct: Discount percentage to apply

    Returns:
        dict with unit_price, subtotal, discount_amount, line_total
    """
    product = get_product(sku)
    if not product:
        return {"error": f"Product {sku} not found"}

    unit_price = product["unit_price"]
    subtotal = unit_price * quantity
    discount_amount = subtotal * (discount_pct / 100.0)
    line_total = subtotal - discount_amount

    return {
        "sku": sku,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": round(subtotal, 2),
        "discount_pct": discount_pct,
        "discount_amount": round(discount_amount, 2),
        "line_total": round(line_total, 2),
        "currency": product["currency"],
    }


def calculate_quote_total(line_items: list[dict]) -> dict:
    """Calculate the total for a complete quote.

    Args:
        line_items: List of dicts with keys: sku, quantity, discount_pct

    Returns:
        dict with lines, subtotal, total_discount, grand_total
    """
    lines = []
    subtotal = 0.0
    total_discount = 0.0

    for item in line_items:
        line = calculate_line_total(
            sku=item["sku"],
            quantity=item["quantity"],
            discount_pct=item.get("discount_pct", 0.0),
        )
        if "error" in line:
            return {"error": line["error"]}
        lines.append(line)
        subtotal += line["subtotal"]
        total_discount += line["discount_amount"]

    grand_total = subtotal - total_discount

    return {
        "lines": lines,
        "subtotal": round(subtotal, 2),
        "total_discount": round(total_discount, 2),
        "grand_total": round(grand_total, 2),
        "currency": "USD",
    }


# --- POLICY SERVICES ---

def get_max_discount(client_tier: str) -> float:
    """Get maximum allowed discount for a client tier."""
    policy = DISCOUNT_POLICIES.get(client_tier, DISCOUNT_POLICIES["standard"])
    return policy["max_discount_pct"]


def get_auto_approve_discount(client_tier: str) -> float:
    """Get auto-approvable discount limit for a client tier."""
    policy = DISCOUNT_POLICIES.get(client_tier, DISCOUNT_POLICIES["standard"])
    return policy["auto_approve_up_to"]


def validate_discount(client_tier: str, requested_discount: float) -> dict:
    """Validate if a requested discount is within policy.

    Returns:
        dict with: allowed (bool), requires_approval (bool), max_allowed, reason
    """
    max_discount = get_max_discount(client_tier)
    auto_approve = get_auto_approve_discount(client_tier)

    if requested_discount <= 0:
        return {"allowed": True, "requires_approval": False, "applied_discount": 0.0}

    if requested_discount > max_discount:
        return {
            "allowed": False,
            "requires_approval": True,
            "max_allowed": max_discount,
            "reason": f"Requested {requested_discount}% exceeds maximum {max_discount}% for {client_tier} tier",
        }

    if requested_discount > auto_approve:
        return {
            "allowed": True,
            "requires_approval": True,
            "applied_discount": requested_discount,
            "reason": f"Discount {requested_discount}% exceeds auto-approve limit of {auto_approve}% for {client_tier} tier",
        }

    return {
        "allowed": True,
        "requires_approval": False,
        "applied_discount": requested_discount,
    }


def requires_approval(grand_total: float, discount_validation: dict) -> dict:
    """Determine if the quote requires human approval.

    Returns:
        dict with: required (bool), reasons (list of strings)
    """
    reasons = []

    if grand_total > APPROVAL_THRESHOLD_USD:
        reasons.append(f"Total USD {grand_total:,.2f} exceeds threshold of USD {APPROVAL_THRESHOLD_USD:,.2f}")

    if discount_validation.get("requires_approval"):
        reasons.append(discount_validation.get("reason", "Discount exception"))

    return {
        "required": len(reasons) > 0,
        "reasons": reasons,
    }
