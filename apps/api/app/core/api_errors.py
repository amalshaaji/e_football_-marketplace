from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.errors import DomainError


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {"code": exc.code, "message": exc.message},
            "request_id": getattr(request.state, "request_id", None),
        },
        headers={"X-Request-ID": getattr(request.state, "request_id", "")},
    )
