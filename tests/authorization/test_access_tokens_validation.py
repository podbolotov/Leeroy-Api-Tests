import allure
import requests
from faker import Faker

from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from models.authorization import AccessTokenErrorTokenBadSignature, AccessTokenErrorTokenMalformed, \
    AccessTokenErrorTokenExpired, \
    AccessTokenErrorTokenNotFoundInDatabase, AccessTokenErrorTokenRevoked

fake = Faker()


@allure.parent_suite("Домен «Авторизация»")
@allure.suite("Токены доступа и обновления")
@allure.sub_suite("Тесты на валидацию токенов доступа")
class TestAccessTokenValidation:

    @allure.title("Ошибка при попытке передачи токена с некорректной подписью")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи токена доступа с некорректной подписью."
    )
    def test_invalid_access_token_signature(
            self, variable_manager, get_random_endpoint_data, make_access_token_with_incorrect_signature
    ):

        res = requests.request(
            method=get_random_endpoint_data.method,
            url=get_random_endpoint_data.url,
            headers={
                "Access-Token": make_access_token_with_incorrect_signature
            },
            json=get_random_endpoint_data.json
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AccessTokenErrorTokenBadSignature,
            data=res.json()
        )


    @allure.title("Ошибка при попытке передачи повреждённого или некорректного токена")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи повреждённого токена доступа, либо данных, "
        "не являющихся токеном доступа."
    )
    def test_malformed_or_incorrect_access_token(
            self, variable_manager, get_random_endpoint_data, make_malformed_jwt_token
    ):
        res = requests.request(
            method=get_random_endpoint_data.method,
            url=get_random_endpoint_data.url,
            headers={
                "Access-Token": make_malformed_jwt_token
            },
            json=get_random_endpoint_data.json
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=400, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AccessTokenErrorTokenMalformed,
            data=res.json()
        )

    @allure.title("Ошибка при передаче истёкшего токена")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи токена доступа, который соответствует формату и "
        "имеет корректную подпись, если его срок действия уже истёк."
    )
    def test_expired_access_token(
            self, variable_manager, get_random_endpoint_data, make_expired_access_token
    ):
        res = requests.request(
            method=get_random_endpoint_data.method,
            url=get_random_endpoint_data.url,
            headers={
                "Access-Token": make_expired_access_token
            },
            json=get_random_endpoint_data.json
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AccessTokenErrorTokenExpired,
            data=res.json()
        )

    @allure.title("Ошибка при передаче токена, данных по которому нет в базе данных")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи токена доступа, являющегося корректным и не "
        "являющегося истёкшим, при условии, что запись о нём в базе данных найти не удалось."
    )
    def test_access_token_not_found(
            self, variable_manager, get_random_endpoint_data, make_unavailable_in_db_access_token
    ):
        res = requests.request(
            method=get_random_endpoint_data.method,
            url=get_random_endpoint_data.url,
            headers={
                "Access-Token": make_unavailable_in_db_access_token
            },
            json=get_random_endpoint_data.json
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AccessTokenErrorTokenNotFoundInDatabase,
            data=res.json()
        )

    @allure.title("Ошибка при передаче отозванного токена")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в обслуживании при попытке передачи неистёкшего и соответствующего ожидаемому "
        "формату токена доступа, запись о котором удалось найти в БД, при условии, что в БД данный токен имеет "
        "признак отзыва."
    )
    def test_access_token_revoked(
            self, variable_manager, get_random_endpoint_data, make_revoked_access_token
    ):
        res = requests.request(
            method=get_random_endpoint_data.method,
            url=get_random_endpoint_data.url,
            headers={
                "Access-Token": make_revoked_access_token
            },
            json=get_random_endpoint_data.json
        )

        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=401, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AccessTokenErrorTokenRevoked,
            data=res.json()
        )
