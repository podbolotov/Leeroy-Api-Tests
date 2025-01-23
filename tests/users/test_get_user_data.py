import uuid

import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_email, get_user_data_by_id
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion
from helpers.jwt_tools import validate_and_decode_token
from helpers.validate_response import validate_response_model
from models.users import GetUserDataSuccessfulResponse, GetUserDataForbiddenError, GetUserDataNotFoundErrorResponse

fake = Faker()


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Получение информации о пользователе")
@allure.sub_suite("Основные функциональные тесты получения информации о пользователе")
class TestGetUserData:

    @allure.title("Отказ в отображении информации по другому пользователю")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отсутствие возможности запросить информацию о другом пользователе от лица пользователя, "
        "не наделённого правами администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
    )
    def test_lack_of_permissions_for_another_user_data_get(
            self, database, variable_manager, authorize_administrator,
            create_and_authorize_user, create_second_user
    ):
        res = requests.get(
            url=FrVars.APP_HOST + "/v1/users/" + str(create_second_user.user_id),
            headers={
                "Access-Token": create_and_authorize_user.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        validate_response_model(
            model=GetUserDataForbiddenError,
            data=res.json()
        )

    @allure.title("Отказ при попытке получения информации о несуществующем пользователе")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет корректную обработку ситуации, когда в запросе передан ID пользователя, найти которого "
        "не удалось.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
    )
    def test_non_existent_user_data_get(
            self, database, variable_manager, authorize_administrator
    ):
        unavailable_in_db_user_id = str(uuid.uuid4())
        res = requests.get(
            url=f"{FrVars.APP_HOST}/v1/users/{unavailable_in_db_user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=404, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_model = validate_response_model(
            model=GetUserDataNotFoundErrorResponse,
            data=res.json()
        )

        make_simple_assertion(
            expected_value=f"User with id {unavailable_in_db_user_id} is not found.",
            actual_value=serialized_model.description,
            assertion_name="Детализация ошибки содержит ID пользователя, данных по которому найти не удалось"
        )

    @allure.title("Успешное получение информации о другом пользователе")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность получения информации одним пользователем о другом, при условии, что "
        "запрашивающий наделён правами администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Соответствие данных, полученных в ответе, данным из БД"
    )
    def test_successful_another_user_data_get(self, database, variable_manager, authorize_administrator, create_user):
        user_id = str(create_user.user_id)
        res = requests.get(
            url=FrVars.APP_HOST + "/v1/users/" + user_id,
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=GetUserDataSuccessfulResponse,
            data=res.json()
        )

        user_data_from_db = get_user_data_by_email(db=database, email=create_user.email)

        make_simple_assertion(
            expected_value=user_id,
            actual_value=str(serialized_response.id),
            assertion_name="ID пользователя в ответе соответствует ID, переданному в запросе"
        )

        make_bulk_assertion(
            group_name="Сверка данных из ответа с данными из БД",
            data=[
                Assertion(
                    expected_value=serialized_response.id,
                    actual_value=user_data_from_db.id,
                    assertion_name="ID пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.firstname,
                    actual_value=user_data_from_db.firstname,
                    assertion_name="Имя пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.middlename,
                    actual_value=user_data_from_db.middlename,
                    assertion_name="Второе имя/отчество пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.surname,
                    actual_value=user_data_from_db.surname,
                    assertion_name="Фамилия пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.is_admin,
                    actual_value=user_data_from_db.is_admin,
                    assertion_name="Признак наличия прав администратора у пользователя в ответе и в БД совпадают"
                )
            ])

    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность получения информации пользователем о себе, по собственному ID, либо по пути "
        "\"/me\".\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Соответствие данных, полученных в ответе, данным из БД"
    )
    @pytest.mark.parametrize("get_mode", ['by_id', 'by_me_path'])
    def test_successful_user_data_get(self, database, variable_manager, create_and_authorize_user, get_mode):

        user_id = validate_and_decode_token(create_and_authorize_user.access_token).user_id

        if get_mode == 'by_id':
            allure.dynamic.title("Успешное получение информации пользователем о себе по своему ID")
            request_url_part = str(user_id)
        else:  # == 'by_me_path'
            allure.dynamic.title("Успешное получение информации пользователем о себе по пути \"/me\"")
            request_url_part = 'me'

        res = requests.get(
            url=FrVars.APP_HOST + "/v1/users/" + request_url_part,
            headers={
                "Access-Token": create_and_authorize_user.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=GetUserDataSuccessfulResponse,
            data=res.json()
        )

        # Дополнительный тест, применимый только к одному из типов запроса информации.
        if get_mode == 'by_id':
            make_simple_assertion(
                expected_value=request_url_part,
                # при режиме запроса 'by_id' в качестве части URL используется ID пользователя
                actual_value=str(serialized_response.id),
                assertion_name="ID пользователя в ответе соответствует ID, переданному в запросе"
            )

        user_data_from_db = get_user_data_by_id(db=database, user_id=user_id)

        make_bulk_assertion(
            group_name="Сверка данных из ответа с данными из БД",
            data=[
                Assertion(
                    expected_value=serialized_response.id,
                    actual_value=user_data_from_db.id,
                    assertion_name="ID пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.firstname,
                    actual_value=user_data_from_db.firstname,
                    assertion_name="Имя пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.middlename,
                    actual_value=user_data_from_db.middlename,
                    assertion_name="Второе имя/отчество пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.surname,
                    actual_value=user_data_from_db.surname,
                    assertion_name="Фамилия пользователя в ответе и в БД совпадают"
                ),
                Assertion(
                    expected_value=serialized_response.is_admin,
                    actual_value=user_data_from_db.is_admin,
                    assertion_name="Признак наличия прав администратора у пользователя в ответе и в БД совпадают"
                )
            ])
