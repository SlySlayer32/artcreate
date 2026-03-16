from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, logger
from shared.observability import configure_sentry, configure_tracing
from shared.schemas.common import ErrorResponse


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    configure_sentry(settings)
    configure_tracing(settings)

    app = FastAPI(title=settings.service_name, version="0.1.0")
    app.include_router(api_router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        response = ErrorResponse(
            error="internal_error",
            detail="Unexpected error",
            request_id=request.headers.get("x-request-id"),
        )
        return JSONResponse(status_code=500, content=response.model_dump())

    return app


app = create_app()
