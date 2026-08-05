"""Typed state definition for the QuoteFlow LangGraph workflow."""

from typing import Annotated, Any, Literal, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class QuoteItem(TypedDict):
    """A single product line item extracted from the request."""
    sku: str
    product_name: str
    quantity: int
    requested_discount_pct: float


class ExtractedData(TypedDict, total=False):
    """Data extracted from the natural language request."""
    client_id: str
    client_name: str
    items: list[QuoteItem]
    delivery_location: str
    delivery_date: str
    requested_discount_pct: float
    special_instructions: str
    missing_fields: list[str]


class ValidationResult(TypedDict, total=False):
    """Result of business rule validation."""
    is_valid: bool
    client_known: bool
    all_products_known: bool
    stock_available: bool
    discount_allowed: bool
    requires_approval: bool
    issues: list[str]
    approval_reasons: list[str]


class Quotation(TypedDict, total=False):
    """Calculated quotation details."""
    lines: list[dict]
    subtotal: float
    total_discount: float
    grand_total: float
    currency: str


class ApprovalDecision(TypedDict, total=False):
    """Human approval decision."""
    action: str  # "approve" | "reject"
    approved_by: str
    notes: str
    timestamp: str


# --- Main Workflow State ---

class QuoteState(TypedDict, total=False):
    """Complete state for the quotation workflow graph.

    This state is persisted via LangGraph's checkpointer and survives
    application restarts.
    """
    # Identity
    quote_id: str
    thread_id: str

    # Input
    client_id: str
    raw_text: str

    # Processing stages
    extracted_data: Optional[ExtractedData]
    validation_result: Optional[ValidationResult]
    quotation: Optional[Quotation]
    approval: Optional[ApprovalDecision]

    # Output
    draft_response: Optional[str]
    status: str  # processing | needs_clarification | needs_approval | approved | rejected | completed | error
    clarification_message: Optional[str]

    # Routing
    route: Optional[str]

    # Audit
    current_node: str
    error: Optional[str]
    messages: Annotated[list, add_messages]
