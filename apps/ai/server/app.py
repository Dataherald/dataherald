import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.k2_core import controller as k2_controller
from modules.query import controller as query_controller

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(k2_controller.router)
app.include_router(query_controller.router)


@app.get("/heartbeat")
async def heartbeat():
    return int(time.time_ns())


@app.get("/")
async def root():
    return {"message": "Hello World"}
