"""Shared response envelope.

Every endpoint answers with {"code", "message", "data"} so the frontend can
read the same three keys on both the success and the failure path.
"""

from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data: Any = None) -> JSONResponse:
    """Wrap a successful result.

    `data` may be a Pydantic model, an ORM object or a plain value —
    jsonable_encoder converts it, honouring serialization aliases so fields
    keep coming out in camelCase.
    """
    content = {"code": 200, "message": message, "data": data}
    return JSONResponse(content=jsonable_encoder(content))


def error_response(code: int, message: str, data: Optional[Any] = None) -> JSONResponse:
    """Wrap a failure, keeping the HTTP status in sync with the payload code."""
    content = {"code": code, "message": message, "data": data}
    return JSONResponse(status_code=code, content=jsonable_encoder(content))
