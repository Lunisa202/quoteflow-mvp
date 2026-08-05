"""Fictional business data for AndesPro Industrial.

This module contains all reference data: clients, products, inventory,
and commercial policies. In production this would come from a database/ERP.
"""

# --- CLIENTS ---
CLIENTS: dict[str, dict] = {
    "CLI-001": {
        "id": "CLI-001",
        "name": "Minera del Sur SAC",
        "tier": "gold",
        "credit_limit": 50000.00,
        "location": "Arequipa",
        "contact_email": "compras@mineradelsur.pe",
    },
    "CLI-002": {
        "id": "CLI-002",
        "name": "Constructora Andes",
        "tier": "silver",
        "credit_limit": 25000.00,
        "location": "Lima",
        "contact_email": "logistica@constructoraandes.pe",
    },
    "CLI-003": {
        "id": "CLI-003",
        "name": "Petroleos del Norte",
        "tier": "platinum",
        "credit_limit": 100000.00,
        "location": "Piura",
        "contact_email": "adquisiciones@petronorte.pe",
    },
    "CLI-004": {
        "id": "CLI-004",
        "name": "Transportes Huancayo",
        "tier": "standard",
        "credit_limit": 10000.00,
        "location": "Huancayo",
        "contact_email": "compras@transhuancayo.pe",
    },
}

# --- PRODUCTS ---
PRODUCTS: dict[str, dict] = {
    "HX-200": {
        "sku": "HX-200",
        "name": "Industrial Safety Helmet HX-200",
        "category": "safety",
        "unit_price": 45.00,
        "currency": "USD",
        "min_order_qty": 5,
    },
    "BT-500": {
        "sku": "BT-500",
        "name": "Steel-Toe Safety Boots BT-500",
        "category": "safety",
        "unit_price": 89.00,
        "currency": "USD",
        "min_order_qty": 3,
    },
    "GL-300": {
        "sku": "GL-300",
        "name": "Chemical Resistant Gloves GL-300",
        "category": "safety",
        "unit_price": 32.00,
        "currency": "USD",
        "min_order_qty": 10,
    },
    "WL-100": {
        "sku": "WL-100",
        "name": "Industrial Welding Machine WL-100",
        "category": "equipment",
        "unit_price": 2500.00,
        "currency": "USD",
        "min_order_qty": 1,
    },
    "CP-750": {
        "sku": "CP-750",
        "name": "Air Compressor CP-750",
        "category": "equipment",
        "unit_price": 1800.00,
        "currency": "USD",
        "min_order_qty": 1,
    },
    "VL-400": {
        "sku": "VL-400",
        "name": "Safety Valve VL-400",
        "category": "parts",
        "unit_price": 120.00,
        "currency": "USD",
        "min_order_qty": 2,
    },
}

# --- INVENTORY (by location) ---
INVENTORY: dict[str, dict[str, int]] = {
    "HX-200": {"Lima": 500, "Arequipa": 150, "Piura": 80},
    "BT-500": {"Lima": 200, "Arequipa": 60, "Piura": 40},
    "GL-300": {"Lima": 1000, "Arequipa": 300, "Piura": 200},
    "WL-100": {"Lima": 15, "Arequipa": 5, "Piura": 3},
    "CP-750": {"Lima": 10, "Arequipa": 4, "Piura": 2},
    "VL-400": {"Lima": 250, "Arequipa": 100, "Piura": 50},
}

# --- COMMERCIAL POLICIES ---
DISCOUNT_POLICIES: dict[str, dict] = {
    "platinum": {"max_discount_pct": 15.0, "auto_approve_up_to": 12.0},
    "gold": {"max_discount_pct": 10.0, "auto_approve_up_to": 8.0},
    "silver": {"max_discount_pct": 7.0, "auto_approve_up_to": 5.0},
    "standard": {"max_discount_pct": 5.0, "auto_approve_up_to": 3.0},
}

# --- BUSINESS RULES ---
APPROVAL_THRESHOLD_USD = 10000.00  # Quotes above this require human approval
DELIVERY_LEAD_DAYS = {
    "same_city": 2,
    "different_city": 5,
    "rush": 1,  # Rush delivery surcharge applies
}
RUSH_SURCHARGE_PCT = 10.0  # Additional % for rush delivery
