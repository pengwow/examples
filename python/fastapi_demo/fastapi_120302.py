from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from httpx import AsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncClient(app=app) as client:
        app.state.client = client
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root(request: Request):
    client = request.app.state.client
    response = await client.get("/")
    return response.json()