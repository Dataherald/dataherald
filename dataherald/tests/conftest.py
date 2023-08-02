import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    engine = create_engine("sqlite:///mydb2.db")
    try:
        engine.execute(
            """CREATE TABLE numbers
                                     (number text, existing boolean)"""
        )
    except Exception:
        pass
