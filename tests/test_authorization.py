import allure
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle
from helpers.validate_response import validate_response_model
from models.authorization import AuthUnauthorizedError, AuthSuccessfulResponse, StringResources as AuthStrings

fake = Faker()


@allure.parent_suite("Тесты")
@allure.suite("Авторизация")
@allure.sub_suite("Основные функциональные тесты авторизации")
class TestBasicAuthorization:
    CORRECT_ADMIN_EMAIL = FrVars.APP_DEFAULT_USER_EMAIL
    CORRECT_ADMIN_PASSWORD = FrVars.APP_DEFAULT_USER_PASSWORD
    INCORRECT_RANDOM_EMAIL = fake.email()
    INCORRECT_RANDOM_PASSWORD = fake.password()

    @allure.title("Отказ в авторизации при передаче некорректного email")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        ''' Данный тест проверяет отказ в авторизации при передаче некорректного адреса электронной почты и 
        некорректного пароля '''
    )
    def test_authorization_with_incorrect_email(self, variable_manager):
        res = requests.post(
            url=FrVars.APP_HOST + "/authorize",
            json={
                "email": self.INCORRECT_RANDOM_EMAIL,
                "password": self.INCORRECT_RANDOM_PASSWORD
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_model = validate_response_model(
            model=AuthUnauthorizedError,
            data=res.json()
        )

        make_simple_assertion(
            expected_value=f"User with email {self.INCORRECT_RANDOM_EMAIL} is not found or password is incorrect",
            actual_value=serialized_model.description, assertion_name="Проверка детализации ошибки")

        make_bulk_assertion(
            group_name="Проверка полученных данных",
            data=[
                AssertionBundle(
                    expected_value=AuthStrings.USER_NOT_FOUND % self.INCORRECT_RANDOM_EMAIL,
                    actual_value=serialized_model.description,
                    assertion_name="Детализация ошибки содержит email запрашивающего",
                )
            ])

    @allure.title("Успешная авторизация стандартного администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        ''' Данный тест проверяет возможность авторизации стандартного администратора приложения '''
    )
    def test_successful_authorize_default_administrator(self):
        res = requests.post(
            url=FrVars.APP_HOST + "/authorize",
            json={
                "email": self.CORRECT_ADMIN_EMAIL,
                "password": self.CORRECT_ADMIN_PASSWORD
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AuthSuccessfulResponse,
            data=res.json()
        )
