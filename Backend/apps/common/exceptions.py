import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler so every error response has the
    consistent shape: {"error": {"detail": ..., "status_code": ...}}.
    Unhandled exceptions are logged server-side, never leaked to the client.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail") if isinstance(response.data, dict) else response.data
        response.data = {
            "error": {
                "detail": detail,
                "status_code": response.status_code,
            }
        }
        return response

    # Unhandled exception - log it, never leak internals to the client.
    logger.exception("Unhandled exception in %s", context.get("view"), exc_info=exc)
    return None
