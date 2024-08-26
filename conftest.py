import pytest
import requests

from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.varirable_manager import VariableManager
from database.db_baseclass import Database
from data.framework_variables import FrameworkVariables as FrVars


@pytest.fixture(scope="session", autouse=True)
def database():
    """ Фикстура, предоставляющая подключение к базе данных """
    db = Database()
    db.connect_to_database()
    yield db


@pytest.fixture(scope="session")
def variable_manager(database):
    """
    Данная фикстура предоставляет менеджер переменных.
    :return:
    """
    vman = VariableManager()
    yield vman


@pytest.fixture(scope="function")
def logout(variable_manager):
    """
    Данная фикстура обеспечивает вызов эндпоинта /logout для тестовых функций, которые завершились корректной
    авторизацией и требуют погашения выданных токенов.

    Обратите внимание, что данная фиксура читает другую фикстуру, variable_manager, и для успешной работы фикстуры
    logout требуется, чтобы перед её вызовом в variable_manager была записана переменная 'access_token' c токеном,
    который необходимо погасить.

    :param variable_manager: Ссылка на фикстуру "variable_manager"
    :return: Данная фикстура ничего не возвращает.
    """
    yield
    try:
        access_token = variable_manager.get('access_token')
    except AttributeError:
        raise RuntimeError("access_token variable in variable_manager is not setted")
    res = requests.delete(
        url=FrVars.APP_HOST + "/logout",
        headers={
            "Access-Token": access_token
        }
    )
    attach_request_data_to_report(res)
    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )
