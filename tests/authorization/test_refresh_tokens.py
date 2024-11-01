import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
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
    @pytest.mark.skip("Отключено до добавления в фикстуру create_and_authorize_user возможности пропуска этапа выхода "
                      "из учётной записи")
    def test_successful_tokens_renew(
            self, variable_manager, create_and_authorize_user
    ):
        res = requests.post(
            url=FrVars.APP_HOST + "/refresh",
            json={
                "refresh_token": create_and_authorize_user.refresh_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        validate_response_model(
            model=AuthSuccessfulResponse,
            data=res.json()
        )
