"""LangGraph workflow definition with conditional routing and interrupt."""

from functools import partial

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # from langgraph-checkpoint-sqlite

from backend.workflow.state import QuoteState
from backend.workflow.nodes import (
    extraction_node,
    validation_node,
    calculation_node,
    draft_node,
    clarification_node,
    blocked_node,
    approval_node,
    post_approval_node,
)


# --- Routing Functions ---

def route_after_validation(state: QuoteState) -> str:
    """Determine next step after validation based on business rules."""
    validation = state.get("validation_result", {})

    # Missing essential info -> clarification
    if not validation.get("client_known", True):
        return "clarification"

    # Missing fields
    extracted = state.get("extracted_data", {})
    if extracted.get("missing_fields"):
        return "clarification"

    # Unknown products or no stock -> blocked
    if not validation.get("all_products_known", True):
        return "blocked"

    if not validation.get("stock_available", True):
        return "blocked"

    # Valid -> proceed to calculation
    return "calculation"


def route_after_calculation(state: QuoteState) -> str:
    """Determine if approval is needed after calculation."""
    quotation = state.get("quotation", {})
    validation = state.get("validation_result", {})

    # Check if approval is required
    if quotation.get("requires_approval") or validation.get("requires_approval"):
        return "approval"

    # No approval needed -> generate draft
    return "draft"


def route_after_approval(state: QuoteState) -> str:
    """Route based on approval decision."""
    approval = state.get("approval", {})
    status = state.get("status", "")

    if status == "rejected":
        return END

    # Approved -> generate draft
    return "draft"


# --- Graph Builder ---

def build_graph(llm, checkpointer=None):
    """Build the QuoteFlow LangGraph workflow.

    Args:
        llm: LangChain LLM instance for extraction and drafting
        checkpointer: LangGraph checkpointer for persistence

    Returns:
        Compiled StateGraph
    """
    # Create graph with typed state
    graph = StateGraph(QuoteState)

    # Add nodes (bind LLM to nodes that need it)
    graph.add_node("extraction", partial(extraction_node, llm=llm))
    graph.add_node("validation", validation_node)
    graph.add_node("calculation", calculation_node)
    graph.add_node("draft", partial(draft_node, llm=llm))
    graph.add_node("clarification", clarification_node)
    graph.add_node("blocked", blocked_node)
    graph.add_node("approval", approval_node)
    graph.add_node("post_approval", post_approval_node)

    # Define edges
    graph.add_edge(START, "extraction")
    graph.add_edge("extraction", "validation")

    # Conditional routing after validation
    graph.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "clarification": "clarification",
            "blocked": "blocked",
            "calculation": "calculation",
        },
    )

    # Conditional routing after calculation
    graph.add_conditional_edges(
        "calculation",
        route_after_calculation,
        {
            "approval": "approval",
            "draft": "draft",
        },
    )

    # Approval -> post_approval (interrupt happens at approval node)
    graph.add_edge("approval", "post_approval")

    # Conditional routing after post_approval
    graph.add_conditional_edges(
        "post_approval",
        route_after_approval,
        {
            "draft": "draft",
            END: END,
        },
    )

    # Terminal nodes
    graph.add_edge("draft", END)
    graph.add_edge("clarification", END)
    graph.add_edge("blocked", END)

    # Compile with checkpointer and interrupt
    compile_kwargs = {}
    if checkpointer:
        compile_kwargs["checkpointer"] = checkpointer
    compile_kwargs["interrupt_before"] = ["post_approval"]

    return graph.compile(**compile_kwargs)


async def get_checkpointer(db_path: str):
    """Create an async SQLite checkpointer for durable persistence."""
    return AsyncSqliteSaver.from_conn_string(db_path)
