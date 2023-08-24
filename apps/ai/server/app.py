import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.auth import controller as auth_controller
from modules.database import controller as database_controller
from modules.golden_sql import controller as golden_sql_controller
from modules.k2_core import controller as k2_controller
from modules.organization import controller as organization_controller
from modules.query import controller as query_controller
from modules.user import controller as user_controller

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router)
app.include_router(k2_controller.router)
app.include_router(query_controller.router)
app.include_router(user_controller.router)
app.include_router(organization_controller.router)
app.include_router(golden_sql_controller.router)
app.include_router(database_controller.router)


@app.get("/heartbeat")
async def heartbeat():
    return int(time.time_ns())


@app.get("/")
async def root():
    return {"message": "Hello World"}
