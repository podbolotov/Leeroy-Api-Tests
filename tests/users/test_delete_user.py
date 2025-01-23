import uuid

import allure
import pytest
import requests
from faker import Faker

from data.framework_variables import FrameworkVariables as FrVars
from database.tokens import get_tokens_count
from database.users import get_user_data_by_id
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion, make_bulk_assertion, AssertionBundle as Assertion, AssertionModes
from helpers.password_tools import hash_password
from helpers.validate_response import validate_response_model
from models.users import DeleteUserSuccessfulResponse, DeleteUserLackOfPermissionsErrorResponse, \
    DeleteAdministratorForbiddenErrorResponse, GetUserDataNotFoundErrorResponse

fake = Faker()


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Удаление пользователей")
@allure.sub_suite("Основные функциональные тесты удаления пользователей")
class TestDeleteUsers:

    @allure.title("Отказ при отсутствии прав администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность удаления пользователя при передаче запроса от имени пользователя, не "
        "имеющего прав администратора.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Сохранность в БД данных пользователя, которого пытались удалить\n"
        "- Сохранность в БД токенов доступа и токенов обновления пользователя, которого пытались удалить"
    )
    def test_delete_user_without_administrator_permissions(
            self, database, variable_manager, create_and_authorize_user, create_and_authorize_second_user
    ):
        # Отправка запроса на удаление пользователя.
        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/users/{create_and_authorize_second_user.user_id}",
            headers={
                "Access-Token": create_and_authorize_user.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        # Запрос из БД данных пользователя которого пытались удалить, а также количества выпущенных на него токенов
        # доступа и токенов обновления.
        user_data_from_db_after_delete_try = get_user_data_by_id(
            db=database, user_id=create_and_authorize_second_user.user_id
        )
        access_tokens_count_after_delete_try = get_tokens_count(
            db=database,
            user_id=create_and_authorize_second_user.user_id,
            token_type='access_token'
        )
        refresh_tokens_count_after_delete_try = get_tokens_count(
            db=database,
            user_id=create_and_authorize_second_user.user_id,
            token_type='refresh_token'
        )

        validate_response_model(
            model=DeleteUserLackOfPermissionsErrorResponse,
            data=res.json()
        )

        make_bulk_assertion(
            group_name="Проверка сохранности данных пользователя",
            data=[
                Assertion(
                    expected_value=create_and_authorize_second_user.user_id,
                    actual_value=user_data_from_db_after_delete_try.id,
                    assertion_name="ID созданного пользователя соответствует установленному при его создании"
                ),
                Assertion(
                    expected_value=create_and_authorize_second_user.firstname,
                    actual_value=user_data_from_db_after_delete_try.firstname,
                    assertion_name="Имя пользователя соответствует установленному при его создании"
                ),
                Assertion(
                    expected_value=create_and_authorize_second_user.middlename,
                    actual_value=user_data_from_db_after_delete_try.middlename,
                    assertion_name="Отчество / среднее имя пользователя соответствует установленному при его создании"
                ),
                Assertion(
                    expected_value=create_and_authorize_second_user.surname,
                    actual_value=user_data_from_db_after_delete_try.surname,
                    assertion_name="Фамилия пользователя соответствует установленной при его создании"
                ),
                Assertion(
                    expected_value=hash_password(create_and_authorize_second_user.password),
                    actual_value=user_data_from_db_after_delete_try.hashed_password,
                    assertion_name="Хэш пароля идентичен результату хеширования на стороне тестового фреймворка"
                ),
                Assertion(
                    expected_value=False,
                    actual_value=user_data_from_db_after_delete_try.is_admin,
                    assertion_name="Значение уровня прав пользователя соответствует установленному при его создании"
                )
            ])

        make_bulk_assertion(
            group_name="Проверка наличия в БД токенов доступа и токенов обновления пользователя, "
                       "которого пытались удалить",
            data=[
                Assertion(
                    expected_value=1,
                    actual_value=access_tokens_count_after_delete_try,
                    assertion_name="В БД должен существовать по меньшей мере один токен доступа",
                    assertion_mode=AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT
                ),
                Assertion(
                    expected_value=1,
                    actual_value=refresh_tokens_count_after_delete_try,
                    assertion_name="В БД должен существовать по меньшей мере один токен обновления",
                    assertion_mode=AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT
                )
            ])

    @allure.title("Отказ при попытке удаления несуществующего пользователя")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет корректность обработки ситуации, в которой запрос на удаление передан с ID, по которому "
        "не удалось найти пользователя.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой"
    )
    def test_delete_non_existing_user(
            self, database, variable_manager, authorize_administrator
    ):
        unavailable_in_db_user_id = str(uuid.uuid4())
        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/users/{unavailable_in_db_user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=404, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        serialized_model = validate_response_model(
            model=GetUserDataNotFoundErrorResponse,
            data=res.json()
        )

        make_simple_assertion(
            expected_value=f"User with id {unavailable_in_db_user_id} is not found.",
            actual_value=serialized_model.description,
            assertion_name="Детализация ошибки содержит ID пользователя, данных по которому найти не удалось"
        )

    @allure.title("Отказ при попытке удаления пользователя с правами администратора")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет невозможность удаления пользователя, являющегося администратором.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Сохранность в БД данных пользователя, которого пытались удалить\n"
        "- Сохранность в БД токенов доступа и токенов обновления пользователя, которого пытались удалить"
    )
    @pytest.mark.parametrize('before_test_user_has_administrator_permissions', [True], indirect=True)
    def test_delete_administrator(
            self, database, authorize_administrator, create_user, create_and_authorize_user,
            before_test_user_has_administrator_permissions
    ):
        res = requests.delete(
            url=FrVars.APP_HOST + f"/v1/users/{create_and_authorize_user.user_id}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code,
                              assertion_name="Проверка кода ответа")

        # Запрос из БД данных пользователя которого пытались удалить, а также количества выпущенных на него токенов
        # доступа и токенов обновления.
        user_data_from_db_after_delete_try = get_user_data_by_id(
            db=database, user_id=create_and_authorize_user.user_id
        )
        access_tokens_count_after_delete_try = get_tokens_count(
            db=database,
            user_id=create_and_authorize_user.user_id,
            token_type='access_token'
        )
        refresh_tokens_count_after_delete_try = get_tokens_count(
            db=database,
            user_id=create_and_authorize_user.user_id,
            token_type='refresh_token'
        )

        validate_response_model(
            model=DeleteAdministratorForbiddenErrorResponse,
            data=res.json()
        )

        make_bulk_assertion(
            group_name="Проверка сохранности данных пользователя",
            data=[
                Assertion(
                    expected_value=create_and_authorize_user.user_id,
                    actual_value=user_data_from_db_after_delete_try.id,
                    assertion_name="ID созданного пользователя соответствует установленному при его создании"
                ),
                Assertion(
                    expected_value=create_and_authorize_user.firstname,
                    actual_value=user_data_from_db_after_delete_try.firstname,
                    assertion_name="Имя пользователя соответствует установленному при его создании"
                ),
                Assertion(
                    expected_value=create_and_authorize_user.middlename,
                    actual_value=user_data_from_db_after_delete_try.middlename,
                    assertion_name="Отчество / среднее имя пользователя соответствует установленному при его создании"
                ),
                Assertion(
                    expected_value=create_and_authorize_user.surname,
                    actual_value=user_data_from_db_after_delete_try.surname,
                    assertion_name="Фамилия пользователя соответствует установленной при его создании"
                ),
                Assertion(
                    expected_value=hash_password(create_and_authorize_user.password),
                    actual_value=user_data_from_db_after_delete_try.hashed_password,
                    assertion_name="Хэш пароля идентичен результату хеширования на стороне тестового фреймворка"
                ),
                Assertion(
                    expected_value=True,
                    actual_value=user_data_from_db_after_delete_try.is_admin,
                    assertion_name="Значение уровня прав пользователя соответствует установленному при его создании"
                )
            ])

        make_bulk_assertion(
            group_name="Проверка наличия в БД токенов доступа и токенов обновления пользователя, "
                       "которого пытались удалить",
            data=[
                Assertion(
                    expected_value=1,
                    actual_value=access_tokens_count_after_delete_try,
                    assertion_name="В БД должен существовать по меньшей мере один токен доступа",
                    assertion_mode=AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT
                ),
                Assertion(
                    expected_value=1,
                    actual_value=refresh_tokens_count_after_delete_try,
                    assertion_name="В БД должен существовать по меньшей мере один токен обновления",
                    assertion_mode=AssertionModes.ACTUAL_VALUE_GREATER_THAN_EXPECTED_OR_EQUAL_TO_IT
                )
            ])

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
            url=FrVars.APP_HOST + f"/v1/users/{create_and_authorize_user.user_id}",
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
