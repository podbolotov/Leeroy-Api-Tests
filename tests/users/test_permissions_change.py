import random

import allure
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_email
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion
from helpers.json_tools import format_json
from helpers.password_tools import hash_password
from helpers.validate_response import validate_response_model
from models.users import CreateUserSuccessfulResponse, UserPermissionsChangeSuccessfulResponse

fake = Faker()


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Изменение уровня прав пользователя")
@allure.sub_suite("Основные функциональные тесты изменения уровня прав пользователей")
class TestUsersPermissions:

    @allure.title("Повышение уровня прав пользователя до администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность присвоения пользователю прав администратора приложения.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Корректность обновления признака наличия прав администратора в базе данных"
    )
    def test_successful_permissions_increase(self, database, authorize_administrator, create_user):
        user_id = str(create_user.user_id)
        res = requests.patch(
            url=FrVars.APP_HOST + f"/users/admin-permissions/{user_id}/grant",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=UserPermissionsChangeSuccessfulResponse,
            data=res.json()
        )
