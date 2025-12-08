from contextlib import asynccontextmanager
from typing import AsyncIterator

import anyio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Starting app")
    app.state.sssss = "123"
    yield
    print("Stopping app")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root(request: Request):
    print(f"sssss: {request.app.state.sssss}")
    return {"Hello": "World"}


async def main():
    async with LifespanManager(app) as manager:
        async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}


anyio.run(main)