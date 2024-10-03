import random

import allure
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
@allure.suite("Создание пользователей")
@allure.sub_suite("Основные функциональные тесты создания пользователей")
class TestCreateUsers:

    @allure.title("Отказ при использовании занятого email")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность создания ещё одного пользователя с указанием ранее занятого email.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Соответствие числа записей в таблице пользователей в БД количеству пользователей с уникальным email в этой "
        "же таблице."
    )
    def test_not_unique_email(self, database, variable_manager, authorize_administrator, create_user):
        res = requests.post(
            url=FrVars.APP_HOST + "/users",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "email": create_user.email,
                "firstname": fake.first_name(),
                "middlename": fake.first_name(),
                "surname": fake.last_name(),
                "password": fake.password()
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=400, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=CreateUserWithUsedEmailErrorResponse,
            data=res.json()
        )

        make_simple_assertion(
            expected_value=f"Email {create_user.email} is not avalaible for registration",
            actual_value=serialized_response.description,
            assertion_name="Детализация ошибки содержит email запрашивающего"
        )

        users_count_by_table_length = get_users_count(db=database, mode='table_count')
        users_count_by_email_distinct = get_users_count(db=database, mode='email_distinct')

        make_simple_assertion(
            expected_value=users_count_by_table_length,
            actual_value=users_count_by_email_distinct,
            assertion_name=f"Общее количество записей в таблице пользователей идентично количеству пользователей с "
                           f"уникальным email"
        )


    @allure.title("Отказ при отсутствии прав администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность создания пользователя при передаче запроса от имени пользователя, не "
        "имеющего прав администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Отсутствие в БД записи о пользователе, который мог бы быть создан этим запросом при его передаче от имени "
        "администратора"
    )
    def test_create_user_without_administrator_permissions(
            self, database, variable_manager, create_and_authorize_user
    ):
        new_user_mail = fake.email()
        res = requests.post(
            url=FrVars.APP_HOST + "/users",
            headers={
                "Access-Token": create_and_authorize_user.access_token
            },
            json={
                "email": new_user_mail,
                "firstname": fake.first_name(),
                "middlename": fake.first_name(),
                "surname": fake.last_name(),
                "password": fake.password()
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        validate_response_model(
            model=CreateUserForbiddenResponse,
            data=res.json()
        )

        potentialy_created_user_data = get_user_data_by_email(db=database, email=new_user_mail)

        make_simple_assertion(
            expected_value=None,
            actual_value=potentialy_created_user_data,
            assertion_name=f"Пользователь с переданным в запросе email не был создан"
        )


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
    def test_successful_user_creation(self, database, variable_manager, authorize_administrator, delete_user):
        new_user_random_email = fake.email()
        new_user_random_firstname = fake.first_name()
        new_user_random_middlename = random.choice([fake.first_name(), None])
        new_user_random_surname = fake.last_name()
        new_user_random_password = fake.password()
        res = requests.post(
            url=FrVars.APP_HOST + "/users",
            headers={
                "Access-Token": authorize_administrator.access_token
            },
            json={
                "email": new_user_random_email,
                "firstname": new_user_random_firstname,
                "middlename": new_user_random_middlename,
                "surname": new_user_random_surname,
                "password": new_user_random_password
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=CreateUserSuccessfulResponse,
            data=res.json()
        )

        user_data_from_db = get_user_data_by_email(db=database, email=new_user_random_email)

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
                        expected_value=new_user_random_firstname,
                        actual_value=user_data_from_db.firstname,
                        assertion_name="Имя пользователя соответствует переданному в запросе"
                    ),
                    Assertion(
                        expected_value=new_user_random_middlename,
                        actual_value=user_data_from_db.middlename,
                        assertion_name="Отчество / среднее имя пользователя соответствует переданному в запросе"
                    ),
                    Assertion(
                        expected_value=new_user_random_surname,
                        actual_value=user_data_from_db.surname,
                        assertion_name="Фамилия пользователя соответствует переданной в запросе"
                    ),
                    Assertion(
                        expected_value=hash_password(new_user_random_password),
                        actual_value=user_data_from_db.hashed_password,
                        assertion_name="Хэш пароля идентичен результату хэширования на стороне тестового фреймворка"
                    ),
                    Assertion(
                        expected_value=False,
                        actual_value=user_data_from_db.is_admin,
                        assertion_name="Созданный пользователь не является администратором"
                    )
                ])

        # Переменная user_id назначается для дальнейшей обработки в фикстуре delete_user.
        variable_manager.set("user_id", serialized_response.user_id)