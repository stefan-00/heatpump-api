import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings
from .session import StartupError, session_manager
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
