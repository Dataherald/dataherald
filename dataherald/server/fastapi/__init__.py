from typing import Any, Callable, Dict, List, Sequence
import fastapi
from fastapi import FastAPI as _FastAPI, Response
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi import HTTPException, status
from uuid import UUID
import dataherald
from dataherald.config import Settings


import logging

def use_route_names_as_operation_ids(app: _FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.
    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name



class FastAPI(dataherald.server.Server):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._app = fastapi.FastAPI(debug=True)
        self._api: dataherald.api.API = dataherald.Client(settings)

        self.router = fastapi.APIRouter()

        self.router.add_api_route(
            "/api/v1/question", self.answer_question, methods=["POST"]
        )

        self.router.add_api_route(
            "/api/v1/heartbeat", self.heartbeat, methods=["GET"]
        )

        
        self.router.add_api_route(
            "/api/v1/database", self.connect_database, methods=["POST"]
        )

        self.router.add_api_route(
            "/api/v1/context", self.add_context, methods=["POST"]
        )


        self._app.include_router(self.router)
        use_route_names_as_operation_ids(self._app)


    def app(self) -> fastapi.FastAPI:
        return self._app
    
    def answer_question(self, question: str) -> str:
        return self._api.answer_question(question)
    
    def root(self) -> Dict[str, int]:
        return {"nanosecond heartbeat": self._api.heartbeat()}

    def heartbeat(self) -> Dict[str, int]:
        return self.root()
    
    def connect_database(self, Database:Any) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        return self._api.connect_database(Database)
    
    def add_context(self, ContextDocumentHandler:Any) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        return self._api.connect_database(ContextDocumentHandler)