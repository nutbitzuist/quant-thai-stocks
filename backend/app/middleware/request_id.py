
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import contextvars

# Context variable to store request ID for the current context
REQUEST_ID_CTX_KEY = "request_id"
_request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(REQUEST_ID_CTX_KEY, default=None)

def get_request_id() -> str:
    return _request_id_ctx_var.get()

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        _request_id_ctx_var.set(request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
