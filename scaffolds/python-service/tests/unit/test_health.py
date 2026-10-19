"""Liveness and readiness endpoints, over the memory database twin."""

import httpx

from app.entrypoints.api import build_api
from app.persistence.memory.uow import MemoryDatabase


def client_for(database: MemoryDatabase) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=build_api(database=database))
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_livez_is_ok_without_touching_dependencies() -> None:
    async with client_for(MemoryDatabase(reachable=False)) as client:
        response = await client.get("/livez")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readyz_is_ok_when_database_answers() -> None:
    async with client_for(MemoryDatabase()) as client:
        response = await client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"ready": True, "checks": {"database": "ok"}}


async def test_readyz_is_503_when_database_is_unreachable() -> None:
    async with client_for(MemoryDatabase(reachable=False)) as client:
        response = await client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["checks"]["database"].startswith("failed")
