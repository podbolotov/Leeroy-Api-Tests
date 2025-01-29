import pytest
import requests

from data.framework_variables import FrameworkVariables as FrVars
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from models.authorization import AuthSuccessfulResponse


@pytest.fixture(scope="class")
def authorize_administrator(variable_manager) -> AuthSuccessfulResponse:
    """
    Данная фикстура авторизует стандартного администратора приложения.

    :param variable_manager: Ссылка на фикстуру "variable_manager".
    :return AuthSuccessfulResponse: (yield) Сериализованный ответ на запрос авторизации.
    """
    res = requests.post(
        url=FrVars.APP_HOST + "/v1/authorize",
        json={
            "email": FrVars.APP_DEFAULT_USER_EMAIL,
            "password": FrVars.APP_DEFAULT_USER_PASSWORD
        }
    )
    attach_request_data_to_report(res)

    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )

    serialized_response = validate_response_model(
        model=AuthSuccessfulResponse,
        data=res.json()
    )

    yield serialized_response

    res = requests.delete(
        url=FrVars.APP_HOST + "/v1/logout",
        headers={
            "Access-Token": serialized_response.access_token
        }
    )
    attach_request_data_to_report(res)
    make_simple_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Код ответа на запрос фикстуры"
    )

@pytest.fixture(scope="function")
def logout(variable_manager) -> None:
    """
    Данная фикстура обеспечивает вызов эндпоинта /logout для тестовых функций, которые завершились корректной
    авторизацией и требуют погашения выданных токенов.

    Обратите внимание, что данная фикстура читает другую фикстуру, variable_manager, и для успешной работы фикстуры
    logout требуется, чтобы перед её вызовом в variable_manager была записана переменная 'access_token' с токеном,
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
        url=FrVars.APP_HOST + "/v1/logout",
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
    # Очистка переменной access_token из менеджера переменных
    variable_manager.unset('access_token')
