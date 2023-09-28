import time

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from modules.auth import controller as auth_controller
from modules.db_connection import controller as db_connection_controller
from modules.golden_sql import controller as golden_sql_controller
from modules.instruction import controller as instruction_controller
from modules.organization import controller as organization_controller
from modules.query import controller as query_controller
from modules.table_description import controller as table_description_controller
from modules.user import controller as user_controller

tags_metadata = [
    {"name": "Authentication", "description": "Login endpoints for authentication"},
    {
        "name": "Database Connection",
        "description": "Database connection related endpoints",
    },
    {"name": "Golden SQL", "description": "Golden SQL related endpoints"},
    {"name": "Organization", "description": "Organization related endpoints"},
    {"name": "Query", "description": "NL Query Response related endpoints"},
    {
        "name": "Table Description",
        "description": "Table description for SQL queried databases",
    },
    {"name": "User", "description": "User related endpoints"},
]

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, tags=["Authentication"])
app.include_router(db_connection_controller.router, tags=["Database Connection"])
app.include_router(golden_sql_controller.router, tags=["Golden SQL"])
app.include_router(instruction_controller.router, tags=["Instruction"])
app.include_router(organization_controller.router, tags=["Organization"])
app.include_router(query_controller.router, tags=["Query"])
app.include_router(table_description_controller.router, tags=["Table Description"])
app.include_router(user_controller.router, tags=["User"])


@app.get("/heartbeat")
async def heartbeat():
    return int(time.time_ns())


@app.get("/engine/heartbeat")
async def engine_heartbeat():
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.k2_core_url + "/heartbeat")
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return response.json()


@app.get("/")
async def root():
    return {"message": "Hello World"}
