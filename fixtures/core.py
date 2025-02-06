from platform import python_version

import allure
import pytest
import platform

from database.db_baseclass import Database
from helpers.varirable_manager import VariableManager
from data.framework_variables import FrameworkVariables as FrVars


@pytest.fixture(scope="session", autouse=True)
@allure.title("Запись информации об окружении в отчёт")
def report_environment_properties_generation():
    f = open("allure-results/environment.properties", "a", encoding='utf-8')
    current_platform = platform.system()

    f.write(f"""
    Platform={current_platform}
    Python\\ version={python_version()}
    Application\\ URL={FrVars.APP_HOST}
    DBMS\\ URL={FrVars.DB_HOST}:{FrVars.DB_PORT}
    """)
    f.close()


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
