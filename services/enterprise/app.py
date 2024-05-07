import time

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from exceptions.exception_handlers import exception_handler
from exceptions.exceptions import BaseError
from middleware.error import UnknownErrorMiddleware
from modules.auth import controller as auth_controller
from modules.db_connection import controller as db_connection_controller
from modules.finetuning import controller as finetuning_controller
from modules.generation import (
    aggr_controller as aggr_generation_controller,
)
from modules.generation import (
    controller as generation_controller,
)
from modules.golden_sql import controller as golden_sql_controller
from modules.instruction import controller as instruction_controller
from modules.key import controller as key_controller
from modules.organization import controller as organization_controller
from modules.organization.invoice import controller as invoice_controller
from modules.table_description import controller as table_description_controller
from modules.user import controller as user_controller

tags_metadata = [
    {"name": "Authentication", "description": "Login endpoints for authentication"},
    {
        "name": "Database Connection",
        "description": "Database connection related endpoints",
    },
    {"name": "Finetuning", "description": "Finetuning LLM related endpoints"},
    {"name": "Generation", "description": "SQL and NL Generation related endpoints"},
    {"name": "Golden SQL", "description": "Golden SQL related endpoints"},
    {"name": "Organization", "description": "Organization related endpoints"},
    {
        "name": "Aggregated Generation",
        "description": "Aggregated Generation related endpoints",
    },
    {
        "name": "Table Description",
        "description": "Table description for SQL queried databases",
    },
    {"name": "User", "description": "User related endpoints"},
]

app = FastAPI()

app.add_middleware(UnknownErrorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(BaseError, exception_handler)

app.include_router(db_connection_controller.router, tags=["Database Connection"])
app.include_router(finetuning_controller.router, tags=["Finetuning"])
app.include_router(golden_sql_controller.router, tags=["Golden SQL"])
app.include_router(instruction_controller.router, tags=["Instruction"])
app.include_router(aggr_generation_controller.router, tags=["Aggregated Generation"])
app.include_router(generation_controller.router, tags=["Generation"])
app.include_router(table_description_controller.router, tags=["Table Description"])

app.include_router(db_connection_controller.ac_router, tags=["Database Connection"])
app.include_router(finetuning_controller.ac_router, tags=["Finetuning"])
app.include_router(golden_sql_controller.ac_router, tags=["Golden SQL"])
app.include_router(instruction_controller.ac_router, tags=["Instruction"])
app.include_router(aggr_generation_controller.ac_router, tags=["Aggregated Generation"])
app.include_router(table_description_controller.ac_router, tags=["Table Description"])

app.include_router(auth_controller.router, tags=["Authentication"])
app.include_router(invoice_controller.router, tags=["Invoice"])
app.include_router(organization_controller.router, tags=["Organization"])
app.include_router(key_controller.router, tags=["Keys"])
app.include_router(user_controller.router, tags=["User"])


@app.get("/heartbeat")
async def heartbeat():
    return int(time.time_ns())


@app.get("/engine/heartbeat")
async def engine_heartbeat():
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.engine_url + "/heartbeat")
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return response.json()
