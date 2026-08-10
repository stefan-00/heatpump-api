import logging
from contextlib import asynccontextmanager
from copy import deepcopy

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings
from .session import SessionExpiredError, StartupError, session_manager
from .routers import setpoints, status

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await session_manager.login()
    except StartupError as e:
        logger.error("Startup failed: %s", e)
        raise
    yield
    await session_manager.close()


app = FastAPI(title="Heatpump API", version="0.1.0", lifespan=lifespan)

app.include_router(status.router)
app.include_router(setpoints.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(SessionExpiredError)
async def session_expired_handler(
    request: Request, exc: SessionExpiredError
) -> JSONResponse:
    # WEB-RC operations normally absorb this by restarting from navigation. If one
    # escapes, it is a device/session condition, not a bug — surface it as a 502
    # rather than letting the catch-all below report an internal error.
    logger.warning("Session expired and was not absorbed by the caller: %s", exc)
    return JSONResponse(
        status_code=502,
        content={"detail": f"Heatpump session expired mid-operation: {exc}"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def _log_config() -> dict:
    # uvicorn.run() installs its own dictConfig for the uvicorn/uvicorn.access/
    # uvicorn.error loggers, whose formatters have no timestamp. Prepend
    # %(asctime)s so access lines match app log lines.
    from uvicorn.config import LOGGING_CONFIG

    config = deepcopy(LOGGING_CONFIG)
    config["formatters"]["default"]["fmt"] = (
        "%(asctime)s " + config["formatters"]["default"]["fmt"]
    )
    config["formatters"]["access"]["fmt"] = (
        "%(asctime)s " + config["formatters"]["access"]["fmt"]
    )
    return config


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port, log_config=_log_config())
