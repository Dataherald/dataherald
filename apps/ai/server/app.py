import time

from fastapi import FastAPI

from modules.k2_core import controller as k2_controller
from modules.query import controller as query_controller

app = FastAPI()

app.include_router(k2_controller.router)
app.include_router(query_controller.router)


@app.get("/heartbeat")
async def heartbeat():
    return int(time.time_ns())


@app.get("/")
async def root():
    return {"message": "Hello World"}
