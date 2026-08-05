"""LangGraph workflow nodes - each node has a single responsibility."""

import json
from datetime import datetime, timezone
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from backend.domain.services import (
    get_client,
    is_known_client,
    is_known_product,
    get_product,
    check_stock,
    calculate_quote_total,
    validate_discount,
    requires_approval,
)
from backend.workflow.state import QuoteState
from backend.services.quote_service import update_quote, add_history_event


# --- Node: Extract structured data from natural language ---

EXTRACTION_PROMPT_TEMPLATE = """Eres un asistente de cotización B2B para AndesPro Industrial.
Extrae información estructurada de la solicitud del cliente.

Debes responder ÚNICAMENTE con JSON válido, sin texto adicional.

Extrae:
- items: array de objetos con campos: sku, product_name, quantity, requested_discount_pct
- delivery_location: string (ciudad/ubicación de entrega)
- delivery_date: string (fecha de entrega solicitada si se menciona)
- requested_discount_pct: number (porcentaje de descuento general si se menciona)
- special_instructions: string (requisitos especiales)
- missing_fields: array de strings (información esencial que falta)

Productos disponibles (usa estos SKUs):
{products_catalog}

Si un producto mencionado no coincide con ninguno conocido, inclúyelo con sku="UNKNOWN".
Si no se especifica cantidad, márcalo en missing_fields.
Si no se menciona descuento, usa 0.
IMPORTANTE: Los valores de missing_fields deben estar en español (ej: "cantidad", "ubicación de entrega", "fecha de entrega", "producto específico").

Formato JSON:
{{
  "items": [{{"sku": "HX-200", "product_name": "Casco de Seguridad Industrial", "quantity": 20, "requested_discount_pct": 8}}],
  "delivery_location": "Arequipa",
  "delivery_date": "próxima semana",
  "requested_discount_pct": 8,
  "special_instructions": "",
  "missing_fields": []
}}"""


def _build_extraction_prompt() -> str:
    """Build extraction prompt dynamically from product catalog."""
    from backend.domain.data import PRODUCTS
    catalog_lines = [f"- {sku}: {p['name']}" for sku, p in PRODUCTS.items()]
    catalog_str = "\n".join(catalog_lines)
    return EXTRACTION_PROMPT_TEMPLATE.format(products_catalog=catalog_str)


async def extraction_node(state: QuoteState, llm) -> dict:
    """Extract structured data from natural language request using LLM."""
    messages = [
        SystemMessage(content=_build_extraction_prompt()),
        HumanMessage(content=f"Client ID: {state['client_id']}\nRequest: {state['raw_text']}"),
    ]

    response = await llm.ainvoke(messages)
    content = response.content.strip()

    # Parse JSON from response (handle markdown code blocks)
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        extracted = json.loads(content)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Error al parsear la respuesta de extracción",
            "current_node": "extraction",
        }

    # Add client info
    extracted["client_id"] = state["client_id"]
    client = get_client(state["client_id"])
    if client:
        extracted["client_name"] = client["name"]

    # Persist
    if state.get("quote_id"):
        update_quote(state["quote_id"], {"extracted_data": extracted, "status": "processing"})
        add_history_event(state["quote_id"], "extraction_completed", {"items_count": len(extracted.get("items", []))})

    return {
        "extracted_data": extracted,
        "current_node": "extraction",
    }


# --- Node: Validate business rules ---

async def validation_node(state: QuoteState) -> dict:
    """Validate extracted data against business rules. Pure deterministic logic."""
    extracted = state.get("extracted_data", {})
    issues = []
    approval_reasons = []

    # 1. Check if client is known
    client_id = state.get("client_id", "")
    client_known = is_known_client(client_id)
    if not client_known:
        issues.append(f"Cliente desconocido: {client_id}")

    # 2. Check missing fields
    missing = extracted.get("missing_fields", [])
    if missing:
        issues.append(f"Información esencial faltante: {', '.join(missing)}")

    # 3. Check all products are known
    items = extracted.get("items", [])
    all_products_known = True
    for item in items:
        if item.get("sku") == "UNKNOWN" or not is_known_product(item.get("sku", "")):
            all_products_known = False
            issues.append(f"Producto desconocido: {item.get('product_name', 'N/A')}")

    # 4. Check stock
    stock_available = True
    location = extracted.get("delivery_location", "Lima")
    for item in items:
        if is_known_product(item.get("sku", "")):
            stock_result = check_stock(item["sku"], location, item.get("quantity", 0))
            if not stock_result["available"]:
                stock_available = False
                issues.append(
                    f"Stock insuficiente para {item['sku']} en {location}: "
                    f"se necesitan {item.get('quantity', 0)}, disponibles {stock_result['stock']}"
                )

    # 5. Check discount policy
    discount_allowed = True
    client = get_client(client_id) if client_known else None
    client_tier = client["tier"] if client else "standard"
    requested_discount = extracted.get("requested_discount_pct", 0)

    if requested_discount > 0:
        discount_result = validate_discount(client_tier, requested_discount)
        if not discount_result.get("allowed"):
            discount_allowed = False
            issues.append(discount_result.get("reason", "Descuento excede la política"))
        if discount_result.get("requires_approval"):
            approval_reasons.append(discount_result.get("reason", "Descuento requiere aprobación"))

    # 6. Check if total would exceed approval threshold (estimate)
    estimated_total = sum(
        get_product(item["sku"])["unit_price"] * item.get("quantity", 0)
        for item in items
        if is_known_product(item.get("sku", ""))
    )
    if estimated_total > 10000:
        approval_reasons.append(
            f"Total estimado USD {estimated_total:,.2f} excede el umbral de USD 10,000"
        )

    # Build validation result
    needs_approval = len(approval_reasons) > 0
    validation_result = {
        "is_valid": len(issues) == 0 or (client_known and all_products_known and stock_available),
        "client_known": client_known,
        "all_products_known": all_products_known,
        "stock_available": stock_available,
        "discount_allowed": discount_allowed,
        "requires_approval": needs_approval,
        "issues": issues,
        "approval_reasons": approval_reasons,
    }

    # Persist
    if state.get("quote_id"):
        update_quote(state["quote_id"], {"validation_result": validation_result})
        add_history_event(state["quote_id"], "validation_completed", {
            "is_valid": validation_result["is_valid"],
            "issues_count": len(issues),
        })

    return {
        "validation_result": validation_result,
        "current_node": "validation",
    }


# --- Node: Calculate quotation ---

async def calculation_node(state: QuoteState) -> dict:
    """Calculate pricing using deterministic domain functions. No LLM involved."""
    extracted = state.get("extracted_data", {})
    validation = state.get("validation_result", {})

    items = extracted.get("items", [])
    client = get_client(state.get("client_id", ""))
    client_tier = client["tier"] if client else "standard"

    # Build line items for calculation
    line_items = []
    for item in items:
        if not is_known_product(item.get("sku", "")):
            continue

        # Determine applicable discount
        requested = item.get("requested_discount_pct", 0) or extracted.get("requested_discount_pct", 0)
        discount_check = validate_discount(client_tier, requested)

        # Use the applicable discount (may be capped)
        if discount_check.get("allowed"):
            applied_discount = discount_check.get("applied_discount", 0)
        else:
            # Cap at max allowed
            from backend.domain.services import get_max_discount
            applied_discount = get_max_discount(client_tier)

        line_items.append({
            "sku": item["sku"],
            "quantity": item.get("quantity", 1),
            "discount_pct": applied_discount,
        })

    quotation = calculate_quote_total(line_items)

    if "error" in quotation:
        return {
            "status": "error",
            "error": quotation["error"],
            "current_node": "calculation",
        }

    # Check if approval is needed based on final total
    discount_validation = validation if validation else {}
    approval_check = requires_approval(quotation["grand_total"], discount_validation)

    if approval_check["required"]:
        # Merge reasons
        existing_reasons = state.get("validation_result", {}).get("approval_reasons", [])
        all_reasons = list(set(existing_reasons + approval_check["reasons"]))
        quotation["requires_approval"] = True
        quotation["approval_reasons"] = all_reasons

    # Persist
    if state.get("quote_id"):
        update_quote(state["quote_id"], {"quotation": quotation})
        add_history_event(state["quote_id"], "calculation_completed", {
            "grand_total": quotation["grand_total"],
            "requires_approval": approval_check["required"],
        })

    return {
        "quotation": quotation,
        "current_node": "calculation",
    }


# --- Node: Generate draft response ---

DRAFT_PROMPT = """Eres un asistente profesional de cotización B2B para AndesPro Industrial.
Genera un borrador de cotización claro y profesional EN ESPAÑOL basado en los datos proporcionados.

El borrador DEBE estar completamente en español e incluir:
- Saludo con el nombre del cliente
- Resumen de los productos solicitados con precios
- Descuento aplicado (si corresponde)
- Condiciones de entrega
- Monto total
- Período de validez (30 días)
- Términos estándar

IMPORTANTE: Todo el texto debe estar en español. No uses inglés.
Redacta de forma profesional y concisa.
Este es un BORRADOR para revisión interna antes de enviar al cliente.
"""


async def draft_node(state: QuoteState, llm) -> dict:
    """Generate the final quotation draft using LLM for natural language."""
    extracted = state.get("extracted_data", {})
    quotation = state.get("quotation", {})
    client = get_client(state.get("client_id", ""))

    context = json.dumps({
        "client": client,
        "extracted_request": extracted,
        "quotation": quotation,
    }, indent=2, default=str)

    messages = [
        SystemMessage(content=DRAFT_PROMPT),
        HumanMessage(content=f"Genera un borrador de cotización basado en:\n{context}"),
    ]

    response = await llm.ainvoke(messages)
    draft = response.content.strip()

    # Persist
    if state.get("quote_id"):
        update_quote(state["quote_id"], {"draft": draft, "status": "completed"})
        add_history_event(state["quote_id"], "draft_generated")

    return {
        "draft_response": draft,
        "status": "completed",
        "current_node": "draft",
    }


# --- Node: Handle clarification needed ---

async def clarification_node(state: QuoteState) -> dict:
    """Handle cases where essential information is missing."""
    extracted = state.get("extracted_data", {})
    validation = state.get("validation_result", {})

    issues = validation.get("issues", [])
    missing = extracted.get("missing_fields", [])

    message = "Se necesita la siguiente información para procesar esta cotización:\n"
    for issue in issues:
        message += f"- {issue}\n"
    if missing:
        message += f"\nCampos faltantes: {', '.join(missing)}"

    # Persist
    if state.get("quote_id"):
        update_quote(state["quote_id"], {
            "status": "needs_clarification",
            "clarification_message": message,
        })
        add_history_event(state["quote_id"], "clarification_needed", {"issues": issues})

    return {
        "status": "needs_clarification",
        "clarification_message": message,
        "current_node": "clarification",
    }


# --- Node: Handle stock/product issues ---

async def blocked_node(state: QuoteState) -> dict:
    """Handle cases blocked by stock or unknown products."""
    validation = state.get("validation_result", {})
    issues = validation.get("issues", [])

    reason = "Cotización bloqueada por:\n" + "\n".join(f"- {i}" for i in issues)

    if state.get("quote_id"):
        update_quote(state["quote_id"], {"status": "blocked", "error": reason})
        add_history_event(state["quote_id"], "quote_blocked", {"reason": reason})

    return {
        "status": "blocked",
        "error": reason,
        "current_node": "blocked",
    }


# --- Node: Approval checkpoint (uses interrupt) ---

async def approval_node(state: QuoteState) -> dict:
    """Pause workflow for human approval. Uses LangGraph interrupt."""
    if state.get("quote_id"):
        update_quote(state["quote_id"], {"status": "needs_approval"})
        reasons = state.get("validation_result", {}).get("approval_reasons", [])
        if not reasons and state.get("quotation", {}).get("approval_reasons"):
            reasons = state["quotation"]["approval_reasons"]
        add_history_event(state["quote_id"], "approval_required", {"reasons": reasons})

    return {
        "status": "needs_approval",
        "current_node": "approval",
    }


# --- Node: Process approval decision ---

async def post_approval_node(state: QuoteState) -> dict:
    """Process the human approval/rejection decision."""
    approval = state.get("approval")

    if not approval:
        return {"status": "needs_approval", "current_node": "approval"}

    action = approval.get("action", "reject")

    if state.get("quote_id"):
        add_history_event(state["quote_id"], f"approval_{action}", {
            "notes": approval.get("notes", ""),
        })

    if action == "reject":
        if state.get("quote_id"):
            update_quote(state["quote_id"], {"status": "rejected"})
        return {
            "status": "rejected",
            "current_node": "post_approval",
        }

    # Approved - continue to draft
    return {
        "status": "approved",
        "current_node": "post_approval",
    }
