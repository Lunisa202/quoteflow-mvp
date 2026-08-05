"""Global error handling and exception classes."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional


# --- Standard API Response Schema ---

class APIResponse(BaseModel):
    """Uniform API response format."""
    success: bool
    data: Optional[Any] = None
    error: Optional[dict] = None
    meta: Optional[dict] = None


def success_response(data: Any = None, meta: Optional[dict] = None) -> dict:
    """Create a standardized success response."""
    return APIResponse(success=True, data=data, meta=meta).model_dump(exclude_none=True)


def error_response(
    code: str,
    message: str,
    details: Optional[Any] = None,
    status_code: int = 400,
) -> JSONResponse:
    """Create a standardized error response."""
    body = APIResponse(
        success=False,
        error={"code": code, "message": message, "details": details},
    ).model_dump(exclude_none=True)
    return JSONResponse(status_code=status_code, content=body)


# --- Custom Exceptions ---

class QuoteFlowError(Exception):
    """Base exception for QuoteFlow application."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(QuoteFlowError):
    """Resource not found."""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(QuoteFlowError):
    """Business validation failed."""
    def __init__(self, message: str, details: Any = None):
        self.details = details
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422)


class WorkflowError(QuoteFlowError):
    """Workflow execution error."""
    def __init__(self, message: str, details: Any = None):
        self.details = details
        super().__init__(message=message, code="WORKFLOW_ERROR", status_code=500)


# --- Exception Handlers ---

def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(QuoteFlowError)
    async def quoteflow_error_handler(request: Request, exc: QuoteFlowError):
        details = getattr(exc, "details", None)
        return error_response(
            code=exc.code,
            message=exc.message,
            details=details,
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details=str(exc) if True else None,  # Show details in dev
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
