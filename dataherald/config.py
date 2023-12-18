import importlib
import inspect
import os
from abc import ABC
from typing import Any, Dict, Type, TypeVar, cast

from dotenv import load_dotenv
from overrides import EnforceOverrides
from pydantic import BaseSettings

_abstract_type_keys: Dict[str, str] = {
    "dataherald.api.API": "api_impl",
    "dataherald.db_scanner.Scanner": "db_scanner_impl",
    "dataherald.eval.Evaluator": "eval_impl",
    "dataherald.db.DB": "db_impl",
    "dataherald.context_store.ContextStore": "context_store_impl",
    "dataherald.vector_store.VectorStore": "vector_store_impl",
}


class Settings(BaseSettings):
    load_dotenv()

    api_impl: str = os.environ.get("API_SERVER", "dataherald.api.fastapi.FastAPI")

    db_scanner_impl: str = os.environ.get(
        "DB_SCANNER", "dataherald.db_scanner.sqlalchemy.SqlAlchemyScanner"
    )

    eval_impl: str = os.environ.get(
        "EVALUATOR", "dataherald.eval.simple_evaluator.SimpleEvaluator"
    )
    db_impl: str = os.environ.get("DB", "dataherald.db.mongo.MongoDB")

    context_store_impl: str = os.environ.get(
        "CONTEXT_STORE", "dataherald.context_store.default.DefaultContextStore"
    )
    vector_store_impl: str = os.environ.get(
        "VECTOR_STORE", "dataherald.vector_store.chroma.Chroma"
    )

    db_name: str | None = os.environ.get("MONGODB_DB_NAME")
    db_uri: str | None = os.environ.get("MONGODB_URI")
    openai_api_key: str | None = os.environ.get("OPENAI_API_KEY")
    encrypt_key: str = os.environ.get("ENCRYPT_KEY")
    s3_aws_access_key_id: str | None = os.environ.get("S3_AWS_ACCESS_KEY_ID")
    s3_aws_secret_access_key: str | None = os.environ.get("S3_AWS_SECRET_ACCESS_KEY")
    only_store_csv_files_locally: bool | None = os.environ.get(
        "ONLY_STORE_CSV_FILES_LOCALLY", False
    )

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


def get_class(fqn: str, type: Type[C]) -> Type[C]:  # noqa: ARG001
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(Type[C], cls)


def get_fqn(cls: Type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"
