import time

from fastapi import FastAPI

from modules.k2_core import controller as k2_controller
from modules.queries import controller as queries_controller
from modules.user import controller as user_controller

app = FastAPI()

app.include_router(k2_controller.router)
app.include_router(queries_controller.router)
app.include_router(user_controller.router)


@app.get("/heartbeat")
async def heartbeat():
    return int(time.time_ns())


@app.get("/")
async def root():
    return {"message": "Hello World"}
