import pytest
from helpers.varirable_manager import VariableManager


@pytest.fixture(scope="session")
def variable_manager():
    vman = VariableManager()
    yield vman
    vman = None
