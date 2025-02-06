import allure
import pytest

from database.db_baseclass import Database
from helpers.varirable_manager import VariableManager


@pytest.fixture(scope="session", autouse=True)
@allure.title("Подключение к базе данных")
def database() -> Database:
    """
    Данная фикстура предоставляет единое подключение к базе данных.

    :return: Экземпляр класса Database.
    """
    db = Database()
    db.connect_to_database()
    yield db


@pytest.fixture(scope="session")
@allure.title("Менеджер переменных сессии")
def variable_manager(database) -> VariableManager:
    """
    Данная фикстура предоставляет менеджер переменных.
    :return: Экземпляр класса VariableManager.
    """
    vman = VariableManager()
    yield vman
