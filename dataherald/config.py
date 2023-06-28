import importlib
import inspect
import os
from abc import ABC
from typing import Any, TypeVar, cast

from dotenv import load_dotenv
from overrides import EnforceOverrides
from pydantic import BaseSettings

_abstract_type_keys: dict[str, str] = {
    "dataherald.api.API": "api_impl",
    "dataherald.smart_cache.SmartCache": "cache_impl",
    "dataherald.sql_generator.SQLGenerator": "sql_generator_impl",
    "dataherald.eval.Evaluator": "eval_impl",
    "dataherald.db.DB": "db_impl",
}


class Settings(BaseSettings):
    load_dotenv()

    api_impl: str = os.environ.get("API_SERVER", "dataherald.api.fastapi.FastAPI")
    cache_impl: str = os.environ.get(
        "CACHE", "dataherald.smart_cache.in_memory.InMemoryCache"
    )
    sql_generator_impl: str = os.environ.get(
        "SQL_GENERATOR", "dataherald.sql_generator.langchain_sql.LangChainSQLGenerator"
    )
    eval_impl: str = os.environ.get(
        "EVALUATOR", "dataherald.eval.simple_evaluator.SimpleEvaluator"
    )
    db_impl: str = os.environ.get("DB", "dataherald.db.mongo.MongoDB")

    server_host: str | None = os.environ.get("SERVER_HOST")
    server_http_port: str | None = os.environ.get("SERVER_HTTP_PORT")
    server_ssl_enabled: bool | None = os.environ.get("SERVER_SSL_ENABLED")

    dataherald_api_impl: str = os.environ.get(
        "DH_API_SERVER", "dataherald.api.fastapi.FastAPI"
    )
    dataherald_cache_impl: str = os.environ.get(
        "DH_CACHE", "dataherald.smart_cache.in_memory.InMemoryCache"
    )
    dataherald_sql_generator_impl: str = os.environ.get(
        "DH_SQL_GENERATOR",
        "dataherald.sql_generator.langchain_sql.LangChainSQLGenerator",
    )
    dataherald_eval_impl: str = os.environ.get(
        "DH_EVALUATOR", "dataherald.eval.simple_evaluator.SimpleEvaluator"
    )

    db_host: str | None = os.environ.get("DB_HOST")
    db_port: str | None = os.environ.get("DB_PORT")
    db_name: str | None = os.environ.get("DB_NAME")
    db_username: str | None = os.environ.get("DB_USERNAME")
    db_password: str | None = os.environ.get("DB_PASSWORD")

    def require(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


T = TypeVar("T", bound="Component")


class Component(ABC, EnforceOverrides):
    _running: bool

    def __init__(self, system: "System"):  # noqa: ARG002
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
    _instances: dict[type[Component], Component]

    def __init__(self, settings: Settings):
        self.settings = settings
        self._instances = {}
        super().__init__(self)

    def instance(self, _type: type[T]) -> T:
        """Return an instance of the component type specified. If the system is running,
        the component will be started as well."""

        if inspect.isabstract(_type):
            type_fqn = get_fqn(_type)
            if type_fqn not in _abstract_type_keys:
                raise ValueError(f"Cannot instantiate abstract type: {_type}")
            key = _abstract_type_keys[type_fqn]
            fqn = self.settings.require(key)
            _type = get_class(fqn)

        if type not in self._instances:
            impl = type(self)
            self._instances[type] = impl
            if self._running:
                impl.start()

        inst = self._instances[type]
        return cast(T, inst)


C = TypeVar("C")


def get_class(fqn: str) -> type[C]:
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(type[C], cls)


def get_fqn(cls: type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"
