"""Quote request endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from backend.api.errors import success_response, NotFoundError

router = APIRouter()


# --- Request/Response Schemas ---

class CreateQuoteRequest(BaseModel):
    """Input for creating a new quote request."""
    client_id: str = Field(..., description="Client identifier")
    raw_text: str = Field(..., description="Natural language quote request")


class ApprovalAction(BaseModel):
    """Input for approval/rejection."""
    action: str = Field(..., pattern="^(approve|reject)$", description="Action: approve or reject")
    notes: Optional[str] = Field(None, description="Optional reviewer notes")


# --- Endpoints ---

@router.post("")
async def create_quote(payload: CreateQuoteRequest):
    """Create a new quotation request and start the workflow."""
    # TODO: Implement workflow execution
    from backend.workflow.engine import run_quote_workflow

    result = await run_quote_workflow(payload.client_id, payload.raw_text)
    return success_response(data=result)


@router.get("")
async def list_quotes():
    """List all quote requests with their current status."""
    # TODO: Implement listing from DB
    from backend.services.quote_service import get_all_quotes

    quotes = await get_all_quotes()
    return success_response(data=quotes)


@router.get("/{quote_id}")
async def get_quote(quote_id: str):
    """Get detailed information about a specific quote."""
    from backend.services.quote_service import get_quote_by_id

    quote = await get_quote_by_id(quote_id)
    if not quote:
        raise NotFoundError("Quote", quote_id)
    return success_response(data=quote)


@router.post("/{quote_id}/approve")
async def approve_quote(quote_id: str, payload: ApprovalAction):
    """Approve or reject a quote that requires human decision."""
    from backend.workflow.engine import resume_quote_workflow

    result = await resume_quote_workflow(quote_id, payload.action, payload.notes)
    return success_response(data=result)


@router.get("/{quote_id}/history")
async def get_quote_history(quote_id: str):
    """Get the audit trail for a quote request."""
    from backend.services.quote_service import get_quote_history

    history = await get_quote_history(quote_id)
    return success_response(data=history)
