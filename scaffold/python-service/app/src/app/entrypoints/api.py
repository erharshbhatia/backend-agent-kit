"""HTTP API. Thin: routers parse, call a use case, and format the result."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.application.health import check_readiness
from app.persistence.ports.database import Database


def build_api(*, database: Database) -> FastAPI:
    """The FastAPI app over already-built dependencies (the composition root passes them in)."""
    api = FastAPI(title="<Project> API")

    @api.get("/livez")
    async def livez() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/readyz")
    async def readyz() -> JSONResponse:
        readiness = await check_readiness(database)
        return JSONResponse(
            status_code=200 if readiness.ready else 503,
            content={"ready": readiness.ready, "checks": readiness.checks},
        )

    return api
