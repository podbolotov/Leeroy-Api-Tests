import allure
import requests

from data.framework_variables import FrameworkVariables as FrVars
from helpers.allure_report import attach_request_data_to_report
from helpers.validate_response import validate_response
from helpers.assertions import make_assertion
from models.authorization import AuthSuccessfulResponse


@allure.parent_suite("Тесты")
@allure.suite("Авторизация")
@allure.sub_suite("Основные функциональные тесты авторизации")
@allure.title("Успешная авторизация стандартного администратора")
@allure.severity(severity_level=allure.severity_level.CRITICAL)
@allure.description(
    ''' Данный тест проверяет возможность авторизации стандартного администратора приложения '''
)
def test_authorize_default_administrator():
    res = requests.post(
        url=FrVars.APP_HOST + "/authorize",
        json={
            "email": FrVars.APP_DEFAULT_USER_EMAIL,
            "password": FrVars.APP_DEFAULT_USER_PASSWORD
        }
    )
    attach_request_data_to_report(res)

    make_assertion(
        expected_value=200,
        actual_value=res.status_code,
        assertion_name="Проверка кода ответа"
    )

    validate_response(
        model=AuthSuccessfulResponse,
        data=res.json()
    )
