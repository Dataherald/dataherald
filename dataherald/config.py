import os
from dotenv import load_dotenv
from pydantic import BaseSettings
from typing import Optional, cast, Type, TypeVar, Dict, Any
from abc import ABC
import inspect
import importlib
from overrides import EnforceOverrides
import logging


_abstract_type_keys: Dict[str, str] = {
    "dataherald.api.API": "api_impl",
    "dataherald.smart_cache.SmartCache": "cache_impl",
    "dataherald.sql_generator.SQLGenerator": "sql_generator_impl",
    "dataherald.eval.Evaluator": "eval_impl",
    "dataherald.db.DB": "db_impl"
}

class Settings(BaseSettings):

    load_dotenv()
    
    api_impl: str = os.environ.get("API_SERVER", "dataherald.api.fastapi.FastAPI")
    cache_impl: str = os.environ.get("CACHE" , "dataherald.smart_cache.in_memory.InMemoryCache")
    sql_generator_impl: str = os.environ.get("SQL_GENERATOR", "dataherald.sql_generator.langchain_sql.LangChainSQLGenerator")
    eval_impl:str = os.environ.get("EVALUATOR", "dataherald.eval.simple_evaluator.SimpleEvaluator")
    db_impl: str = os.environ.get("DB", "dataherald.db.mongo.MongoDB")

    server_host: Optional[str] = os.environ.get("SERVER_HOST")
    server_http_port: Optional[str] = os.environ.get("SERVER_HTTP_PORT")
    server_ssl_enabled: Optional[bool] = os.environ.get("SERVER_SSL_ENABLED")


    db_host: Optional[str] = os.environ.get("DB_HOST")
    db_port: Optional[str] = os.environ.get("DB_PORT")
    db_name: Optional[str] = os.environ.get("DB_NAME")
    db_username: Optional[str] = os.environ.get("DB_USERNAME")
    db_password: Optional[str] = os.environ.get("DB_PASSWORD")

    def require(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val
    
    def __getitem__(self, key: str) -> Any:
        val = getattr(self, key)
        return val

T = TypeVar("T", bound="Component")


class Component(ABC, EnforceOverrides):
    _running: bool

    def __init__(self, system: "System"):
        self._running = False

    def stop(self) -> None:
        """Idempotently stop this component's execution and free all associated
        resources."""
        self._running = False

    def start(self) -> None:
        """Idempotently start this component's execution"""
        self._running = True



class System(Component):
    settings: Settings
    _instances: Dict[Type[Component], Component]

    def __init__(self, settings: Settings):
        self.settings = settings
        self._instances = {}
        super().__init__(self)

    def instance(self, type: Type[T]) -> T:
        """Return an instance of the component type specified. If the system is running,
        the component will be started as well."""

        if inspect.isabstract(type):
            type_fqn = get_fqn(type)
            if type_fqn not in _abstract_type_keys:
                raise ValueError(f"Cannot instantiate abstract type: {type}")
            key = _abstract_type_keys[type_fqn]
            fqn = self.settings.require(key)
            type = get_class(fqn, type)

        if type not in self._instances:
            impl = type(self)
            self._instances[type] = impl
            if self._running:
                impl.start()

        inst = self._instances[type]
        return cast(T, inst)
    

C = TypeVar("C")

def get_class(fqn: str, type: Type[C]) -> Type[C]:
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(Type[C], cls)


def get_fqn(cls: Type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"