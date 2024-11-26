import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.tokens import get_tokens_count
from database.users import get_user_data_by_id
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion, AssertionModes
from helpers.validate_response import validate_response_model
from models.users import DeleteUserSuccessfulResponse

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
        # Извлечение имеющихся в БД данных пользователя, а также количества токенов доступа и количества токенов
        # обновления.
        user_data_from_db_before_delete = get_user_data_by_id(db=database, user_id=create_and_authorize_user.user_id)
        access_tokens_count_before_delete = get_tokens_count(
            db=database,
            user_id=create_and_authorize_user.user_id,
            token_type='access_token'
        )
        refresh_tokens_count_before_delete = get_tokens_count(
            db=database,
            user_id=create_and_authorize_user.user_id,
            token_type='refresh_token'
        )

        # Отправка запроса на удаление пользователя.
        res = requests.delete(
            url=FrVars.APP_HOST + f"/users/{create_and_authorize_user.user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        # Попытка извлечения данных удалённого пользователя из БД, включая запрос количеств его токенов доступа и
        # токенов обновления.
        user_data_from_db_after_delete = get_user_data_by_id(db=database, user_id=create_and_authorize_user.user_id)
        access_tokens_count_after_delete = get_tokens_count(
            db=database,
            user_id=create_and_authorize_user.user_id,
            token_type='access_token'
        )
        refresh_tokens_count_after_delete = get_tokens_count(
            db=database,
            user_id=create_and_authorize_user.user_id,
            token_type='refresh_token'
        )

        validate_response_model(
            model=DeleteUserSuccessfulResponse,
            data=res.json()
        )

        make_bulk_assertion(
            group_name="Верификация состояния пользователя в БД до удаления",
            data=[
                Assertion(
                    expected_value=None,
                    actual_value=user_data_from_db_before_delete,
                    assertion_name="Данные пользователя должны существовать в БД",
                    assertion_mode=AssertionModes.VALUES_ARE_NOT_EQUAL
                ),
                Assertion(
                    expected_value=1,
                    actual_value=access_tokens_count_before_delete,
                    assertion_name="В БД должен существовать по меньшей мере один токен доступа",
                    assertion_mode=AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT
                ),
                Assertion(
                    expected_value=1,
                    actual_value=refresh_tokens_count_before_delete,
                    assertion_name="В БД должен существовать по меньшей мере один токен обновления",
                    assertion_mode=AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT
                )
            ])


        make_bulk_assertion(
            group_name="Верификация результатов удаления пользователя из БД",
            data=[
                Assertion(
                    expected_value=None,
                    actual_value=user_data_from_db_after_delete,
                    assertion_name="Данных удалённого пользователя не должно существовать в БД",
                    assertion_mode=AssertionModes.VALUES_ARE_EQUAL
                ),
                Assertion(
                    expected_value=0,
                    actual_value=access_tokens_count_after_delete,
                    assertion_name="В БД должен не должно существовать токенов доступа удалённого пользователя",
                    assertion_mode=AssertionModes.VALUES_ARE_EQUAL
                ),
                Assertion(
                    expected_value=0,
                    actual_value=refresh_tokens_count_after_delete,
                    assertion_name="В БД должен не должно существовать токенов обновления удалённого пользователя",
                    assertion_mode=AssertionModes.VALUES_ARE_EQUAL
                )
            ])
