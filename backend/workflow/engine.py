"""Workflow engine - orchestrates graph execution and resume."""

import uuid
from datetime import datetime, timezone

from langchain_groq import ChatGroq

from backend.config import GROQ_API_KEY, LLM_MODEL, CHECKPOINTER_DB_PATH
from backend.workflow.graph import build_graph, get_checkpointer
from backend.workflow.state import QuoteState
from backend.services.quote_service import (
    create_quote_record,
    update_quote,
    add_history_event,
)


# Global graph instance (initialized on first use)
_graph = None
_checkpointer = None


async def _get_graph():
    """Lazy initialization of the graph with checkpointer."""
    global _graph, _checkpointer

    if _graph is None:
        # Ensure data directory exists
        from pathlib import Path
        Path(CHECKPOINTER_DB_PATH).parent.mkdir(parents=True, exist_ok=True)

        llm = ChatGroq(
            model=LLM_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0,
        )
        # Use MemorySaver for immediate functionality
        from langgraph.checkpoint.memory import MemorySaver
        _checkpointer = MemorySaver()
        _graph = build_graph(llm, checkpointer=_checkpointer)

    return _graph


async def run_quote_workflow(client_id: str, raw_text: str) -> dict:
    """Start a new quotation workflow.

    Creates a quote record, initializes state, and runs the graph
    until it reaches a terminal state or an interrupt point.
    """
    graph = await _get_graph()

    # Create persisted quote record
    quote = create_quote_record(client_id, raw_text)
    quote_id = quote["id"]
    thread_id = str(uuid.uuid4())

    # Initial state
    initial_state: QuoteState = {
        "quote_id": quote_id,
        "thread_id": thread_id,
        "client_id": client_id,
        "raw_text": raw_text,
        "status": "processing",
        "current_node": "start",
        "messages": [],
    }

    # Store thread_id in quote for resume
    update_quote(quote_id, {"thread_id": thread_id})

    add_history_event(quote_id, "workflow_started", {
        "client_id": client_id,
        "thread_id": thread_id,
    })

    # Run graph with thread config (for checkpointer)
    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_state = await graph.ainvoke(initial_state, config=config)
    except Exception as e:
        update_quote(quote_id, {"status": "error"})
        add_history_event(quote_id, "workflow_error", {"error": str(e)})
        return {
            "quote_id": quote_id,
            "status": "error",
            "error": str(e),
        }

    # Update final status
    status = final_state.get("status", "completed")
    update_quote(quote_id, {"status": status})

    return {
        "quote_id": quote_id,
        "thread_id": thread_id,
        "status": status,
        "extracted_data": final_state.get("extracted_data"),
        "validation_result": final_state.get("validation_result"),
        "quotation": final_state.get("quotation"),
        "draft": final_state.get("draft_response"),
        "clarification_message": final_state.get("clarification_message"),
        "error": final_state.get("error"),
    }


async def resume_quote_workflow(quote_id: str, action: str, notes: str = None) -> dict:
    """Resume a paused workflow after human approval/rejection.

    This uses LangGraph's checkpoint to resume from the interrupt point.
    """
    from backend.services.quote_service import get_quote_by_id
    from backend.workflow.nodes import draft_node

    graph = await _get_graph()

    # Get the quote to find thread_id
    quote = await get_quote_by_id(quote_id)
    if not quote:
        return {"error": "Cotización no encontrada"}

    thread_id = quote.get("thread_id")
    if not thread_id:
        return {"error": "No se encontró thread_id para esta cotización"}

    config = {"configurable": {"thread_id": thread_id}}

    # Prepare approval decision
    approval_decision = {
        "action": action,
        "notes": notes or "",
        "approved_by": "reviewer",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    add_history_event(quote_id, f"approval_{action}", {
        "notes": notes or "",
    })

    if action == "reject":
        update_quote(quote_id, {
            "status": "rejected",
            "approval": approval_decision,
        })
        return {
            "quote_id": quote_id,
            "status": "rejected",
            "approval": approval_decision,
        }

    # Approved - try to resume graph, fallback to direct draft generation
    try:
        # Try LangGraph resume with Command
        from langgraph.types import Command
        final_state = await graph.ainvoke(
            Command(resume={"approval": approval_decision}),
            config=config,
        )
        status = final_state.get("status", "completed")
        draft = final_state.get("draft_response")
    except Exception:
        # Fallback: generate draft directly using LLM
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0)
            
            # Build state from stored quote data
            state = {
                "quote_id": quote_id,
                "client_id": quote.get("client_id", ""),
                "extracted_data": quote.get("extracted_data", {}),
                "quotation": quote.get("quotation", {}),
            }
            result = await draft_node(state, llm)
            status = "completed"
            draft = result.get("draft_response", "")
        except Exception as e:
            update_quote(quote_id, {"status": "error"})
            add_history_event(quote_id, "resume_error", {"error": str(e)})
            return {
                "quote_id": quote_id,
                "status": "error",
                "error": str(e),
            }

    update_quote(quote_id, {
        "status": status,
        "approval": approval_decision,
        "draft": draft,
    })

    return {
        "quote_id": quote_id,
        "status": status,
        "approval": approval_decision,
        "draft": draft,
    }
