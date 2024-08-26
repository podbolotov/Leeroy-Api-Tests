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
from models.users import CreateUserSuccessfulResponse

fake = Faker()


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Создание пользователей")
@allure.sub_suite("Основные функциональные тесты создания пользователей")
class TestCreateUsers:
    NEW_USER_RANDOM_EMAIL = fake.email()
    NEW_USER_RANDOM_FIRSTNAME = fake.first_name()
    NEW_USER_RANDOM_MIDDLENAME = random.choice([fake.first_name(), None])
    NEW_USER_RANDOM_SURNAME = fake.last_name()
    NEW_USER_RANDOM_PASSWORD = fake.password()

    @allure.title("Успешное создание пользователя")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность создания нового пользователя стандартным администратором приложения.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Корректность записи данных зарегистрированного пользователя в БД, совпадение записанных в БД данных с "
        "данными полученными в ответе (в случае id) и данными переданными в запросе (в случае со всеми остальными "
        "данными)"
    )
    def test_successful_user_creation(self, database, authorize_administrator):
        res = requests.post(
            url=FrVars.APP_HOST + "/users",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "email": self.NEW_USER_RANDOM_EMAIL,
                "firstname": self.NEW_USER_RANDOM_FIRSTNAME,
                "middlename": self.NEW_USER_RANDOM_MIDDLENAME,
                "surname": self.NEW_USER_RANDOM_SURNAME,
                "password": self.NEW_USER_RANDOM_PASSWORD
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=CreateUserSuccessfulResponse,
            data=res.json()
        )

        user_data_from_db = get_user_data_by_email(db=database, email=self.NEW_USER_RANDOM_EMAIL)

        with allure.step("Верификация сохранённых в БД данных пользователя"):
            allure.attach(
                format_json(user_data_from_db.model_dump_json()),
                'Данные созданного пользователя из БД'
            )

            make_bulk_assertion(
                group_name="Верификация данных пользователя",
                data=[
                    Assertion(
                        expected_value=serialized_response.user_id,
                        actual_value=user_data_from_db.id,
                        assertion_name="ID созданного пользователя соответствует полученному в ответе"
                    ),
                    Assertion(
                        expected_value=self.NEW_USER_RANDOM_FIRSTNAME,
                        actual_value=user_data_from_db.firstname,
                        assertion_name="Имя пользователя соответствует переданному в запросе"
                    ),
                    Assertion(
                        expected_value=self.NEW_USER_RANDOM_MIDDLENAME,
                        actual_value=user_data_from_db.middlename,
                        assertion_name="Отчество / среднее имя пользователя соответствует переданному в запросе"
                    ),
                    Assertion(
                        expected_value=self.NEW_USER_RANDOM_SURNAME,
                        actual_value=user_data_from_db.surname,
                        assertion_name="Фамилия пользователя соответствует переданной в запросе"
                    ),
                    Assertion(
                        expected_value=hash_password(self.NEW_USER_RANDOM_PASSWORD),
                        actual_value=user_data_from_db.hashed_password,
                        assertion_name="Хэш пароля идентичен результату хэширования на стороне тестового фреймворка"
                    ),
                    Assertion(
                        expected_value=False,
                        actual_value=user_data_from_db.is_admin,
                        assertion_name="Созданный пользователь не является администратором"
                    )
                ])
