import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.tokens import get_access_token_by_id, get_refresh_token_by_id
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion
from helpers.json_tools import format_json
from helpers.jwt_tools import validate_and_decode_token
from helpers.validate_response import validate_response_model
from models.authorization import AuthSuccessfulResponse

fake = Faker()


@allure.parent_suite("Домен «Авторизация»")
@allure.suite("Обновление связанной пары авторизационных токенов")
@allure.sub_suite("Основные функциональные тесты обновления токенов")
class TestSuccessfulTokensRenew:

    @allure.title("Успешное обновление пары токенов")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет возможность успешного обновления токена доступа и токена обновления.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Соответствие структуры (модели) обоих выпущенных токенов\n"
        "- Факт присвоения статуса \"отозван\" связанной паре токенов, токен обновления которой был передан.\n"
        "- Корректность записи данных о выпущенных токенах в БД, совпадение записанных в БД данных о токенах с данными "
        "из декодированных токенов\n"
    )
    # Ввиду выпуска новой пары токенов необходимо пропустить стандартный выход из учётной записи,
    # выполняемый фикстурой "create_and_authorize_user":
    @pytest.mark.parametrize("create_and_authorize_user", ["fixture logout should be skipped"], indirect=True)
    def test_successful_tokens_renew(
            self, variable_manager, create_and_authorize_user, logout
    , database):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/refresh",
            json={
                "refresh_token": create_and_authorize_user.refresh_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=AuthSuccessfulResponse,
            data=res.json()
        )

        with allure.step("Декодирование и верификация полученного Access-Token'а"):

            decoded_access_token = validate_and_decode_token(serialized_response.access_token)
            allure.attach(
                format_json(decoded_access_token.model_dump_json()),
                'Декодированный Access-Token'
            )

            make_simple_assertion(
                expected_value=create_and_authorize_user.user_id,
                actual_value=decoded_access_token.user_id,
                assertion_name="ID пользователя, полученный при создании пользователя, сходится с ID пользователя, "
                               "который закодирован в токене"
            )

        with allure.step("Декодирование и верификация полученного Refresh-Token'а"):
            decoded_refresh_token = validate_and_decode_token(serialized_response.refresh_token)
            allure.attach(
                format_json(decoded_refresh_token.model_dump_json()),
                'Декодированный Refresh-Token'
            )

            make_simple_assertion(
                expected_value=create_and_authorize_user.user_id,
                actual_value=decoded_refresh_token.user_id,
                assertion_name="ID пользователя, полученный при создании пользователя, сходится с ID пользователя, "
                               "который закодирован в токене"
            )

        with allure.step("Верификация сохранённых в БД данных токенов"):
            database_access_token_data = get_access_token_by_id(db=database, token_id=decoded_access_token.id)
            database_refresh_token_data = get_refresh_token_by_id(db=database, token_id=decoded_refresh_token.id)
            allure.attach(format_json(database_access_token_data.model_dump_json()), 'Данные Access-Token\'а из БД')
            allure.attach(format_json(database_refresh_token_data.model_dump_json()), 'Данные Refresh-Token\'а из БД')
            make_bulk_assertion(
                group_name="Верификация данных Access-Token'а",
                data=[
                    Assertion(
                        expected_value=decoded_access_token.user_id,
                        actual_value=database_access_token_data.user_id,
                        assertion_name="ID пользователя токена совпадает между БД и декодированным токеном"
                    ),
                    Assertion(
                        expected_value=decoded_access_token.issued_at,
                        actual_value=database_access_token_data.issued_at,
                        assertion_name="Значение времени выпуска совпадает между БД и декодированным токеном"
                    ),
                    Assertion(
                        expected_value=decoded_access_token.expired_at,
                        actual_value=database_access_token_data.expired_at,
                        assertion_name="Значение времени истечения совпадает между БД и декодированным токеном"
                    ),
                    Assertion(
                        expected_value=decoded_refresh_token.id,
                        actual_value=database_access_token_data.refresh_token_id,
                        assertion_name="Значение парного Refresh-Token'а в БД совпадает с ID выданного Refresh-Token'а "
                                       "из декодированного экземпляра."
                    ),
                    Assertion(
                        expected_value=False,
                        actual_value=database_access_token_data.revoked,
                        assertion_name="Токен не отозван (значение поля revoked токена в БД является False)"
                    )
                ])

            make_bulk_assertion(
                group_name="Верификация данных Refresh-Token'а",
                data=[
                    Assertion(
                        expected_value=decoded_refresh_token.user_id,
                        actual_value=database_refresh_token_data.user_id,
                        assertion_name="ID пользователя токена совпадает между БД и декодированным токеном"
                    ),
                    Assertion(
                        expected_value=decoded_refresh_token.issued_at,
                        actual_value=database_refresh_token_data.issued_at,
                        assertion_name="Значение времени выпуска совпадает между БД и декодированным токеном"
                    ),
                    Assertion(
                        expected_value=decoded_refresh_token.expired_at,
                        actual_value=database_refresh_token_data.expired_at,
                        assertion_name="Значение времени истечения совпадает между БД и декодированным токеном"
                    ),
                    Assertion(
                        expected_value=decoded_access_token.id,
                        actual_value=database_refresh_token_data.access_token_id,
                        assertion_name="Значение парного Access-Token'а в БД совпадает с ID выданного Access-Token'а "
                                       "из декодированного экземпляра."
                    ),
                    Assertion(
                        expected_value=False,
                        actual_value=database_refresh_token_data.revoked,
                        assertion_name="Токен не отозван (значение поля revoked токена в БД является False)"
                    )
                ])

        # Переменная access_token назначается для дальнейшей обработки в фикстуре logout.
        variable_manager.set("access_token", res.json()['access_token'])
