import random

import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_email, get_users_count
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion
from helpers.json_tools import format_json
from helpers.password_tools import hash_password
from helpers.validate_response import validate_response_model
from models.users import CreateUserSuccessfulResponse, CreateUserWithUsedEmailErrorResponse, CreateUserForbiddenResponse

fake = Faker()


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Удаление пользователей")
@allure.sub_suite("Основные функциональные тесты удаления пользователей")
class TestDeleteUsers:

    @allure.title("Успешное удаление пользователя")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность удаления ранее созданного пользователя стандартным администратором "
        "приложения.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Корректность удаления данных удаляемого пользователя из БД"
    )
    @pytest.mark.parametrize("create_and_authorize_user", ["fixture logout should be skipped"], indirect=True)
    @pytest.mark.parametrize("create_user", ["fixture user deletion should be skipped"], indirect=True)
    def test_successful_user_deletion(
            self, database, variable_manager, authorize_administrator, create_user, create_and_authorize_user
    ):
        res = requests.delete(
            url=FrVars.APP_HOST + f"/users/{create_and_authorize_user.user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        # serialized_response = validate_response_model(
        #     model=CreateUserSuccessfulResponse,
        #     data=res.json()
        # )

        # user_data_from_db = get_user_data_by_email(db=database, email=new_user_random_email)
        #
        # with allure.step("Верификация сохранённых в БД данных пользователя"):
        #     allure.attach(
        #         format_json(user_data_from_db.model_dump_json()),
        #         'Данные созданного пользователя из БД'
        #     )
        #
        #     make_bulk_assertion(
        #         group_name="Верификация данных пользователя",
        #         data=[
        #             Assertion(
        #                 expected_value=serialized_response.user_id,
        #                 actual_value=user_data_from_db.id,
        #                 assertion_name="ID созданного пользователя соответствует полученному в ответе"
        #             ),
        #             Assertion(
        #                 expected_value=new_user_random_firstname,
        #                 actual_value=user_data_from_db.firstname,
        #                 assertion_name="Имя пользователя соответствует переданному в запросе"
        #             ),
        #             Assertion(
        #                 expected_value=new_user_random_middlename,
        #                 actual_value=user_data_from_db.middlename,
        #                 assertion_name="Отчество / среднее имя пользователя соответствует переданному в запросе"
        #             ),
        #             Assertion(
        #                 expected_value=new_user_random_surname,
        #                 actual_value=user_data_from_db.surname,
        #                 assertion_name="Фамилия пользователя соответствует переданной в запросе"
        #             ),
        #             Assertion(
        #                 expected_value=hash_password(new_user_random_password),
        #                 actual_value=user_data_from_db.hashed_password,
        #                 assertion_name="Хэш пароля идентичен результату хэширования на стороне тестового фреймворка"
        #             ),
        #             Assertion(
        #                 expected_value=False,
        #                 actual_value=user_data_from_db.is_admin,
        #                 assertion_name="Созданный пользователь не является администратором"
        #             )
        #         ])
        #
        # # Переменная user_id назначается для дальнейшей обработки в фикстуре delete_user.
        # variable_manager.set("user_id", serialized_response.user_id)