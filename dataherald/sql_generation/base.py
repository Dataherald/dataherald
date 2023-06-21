"""Base class that all sql generation classes inherit from."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from dataherald.sql_database.base import SQLDatabase


class SQLGenerator(ABC):
    database: SQLDatabase
    metadata: Any
    
    

