import allure
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from models.authorization import RefreshTokenErrorTokenBadSignature, \
    RefreshTokenErrorTokenMalformed, RefreshTokenErrorTokenExpired, RefreshTokenErrorTokenNotFoundInDatabase, \
    RefreshTokenErrorTokenRevoked

fake = Faker()


@allure.parent_suite("Домен «Авторизация»")
@allure.suite("Токены доступа и обновления")
@allure.sub_suite("Тесты на валидацию токенов обновления")
class TestRefreshTokenValidation:

    @allure.title("Ошибка при попытке передачи токена с некорректной подписью")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи токена обновления с некорректной подписью."
    )
    def test_invalid_refresh_token_signature(
            self, variable_manager, make_refresh_token_with_incorrect_signature
    ):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/refresh",
            json={
                "refresh_token": make_refresh_token_with_incorrect_signature
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=RefreshTokenErrorTokenBadSignature,
            data=res.json()
        )


    @allure.title("Ошибка при попытке передачи повреждённого или некорректного токена")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи повреждённого токена обновления, либо данных, "
        "не являющихся токеном обновления."
    )
    def test_malformed_or_incorrect_refresh_token(
            self, variable_manager, make_malformed_jwt_token
    ):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/refresh",
            json={
                "refresh_token": make_malformed_jwt_token
            }
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=400, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=RefreshTokenErrorTokenMalformed,
            data=res.json()
        )

    @allure.title("Ошибка при передаче истёкшего токена")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи токена обновления, который соответствует "
        "формату и имеет корректную подпись, если его срок действия уже истёк."
    )
    def test_expired_refresh_token(
            self, variable_manager, make_expired_refresh_token
    ):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/refresh",
            json={
                "refresh_token": make_expired_refresh_token
            }
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=RefreshTokenErrorTokenExpired,
            data=res.json()
        )

    @allure.title("Ошибка при передаче токена, данных по которому нет в базе данных")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи токена обновления, являющегося корректным и "
        "не являющегося истёкшим, при условии, что запись о нём в базе данных найти не удалось."
    )
    def test_refresh_token_not_found(
            self, variable_manager, make_unavailable_in_db_refresh_token
    ):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/refresh",
            json={
                "refresh_token": make_unavailable_in_db_refresh_token
            }
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=RefreshTokenErrorTokenNotFoundInDatabase,
            data=res.json()
        )

    @allure.title("Ошибка при передаче отозванного токена")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи неистёкшего и соответствующего ожидаемому "
        "формату токена обновления, запись о котором удалось найти в БД, при условии, что в БД данный токен имеет "
        "признак отзыва."
    )
    def test_refresh_token_revoked(
            self, variable_manager, make_revoked_refresh_token
    ):
        res = requests.post(
            url=FrVars.APP_HOST + "/v1/refresh",
            json={
                "refresh_token": make_revoked_refresh_token
            }
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=RefreshTokenErrorTokenRevoked,
            data=res.json()
        )
