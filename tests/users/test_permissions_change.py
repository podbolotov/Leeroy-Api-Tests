import allure
import pytest
import requests
import random
from faker import Faker
from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_id, get_user_data_by_email, get_all_nonadmin_users_ids, \
    get_all_administrators_ids
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion
from helpers.validate_response import validate_response_model
from models.users import (UserPermissionsChangeSuccessfulResponse,
                          UserPermissionsChangeBadRequestResponse, UserPermissionsChangeBadRequestReason,
                          UserPermissionsChangeLastAdminErrorResponse,
                          UserPermissionsChangeLackOfPermissionsErrorResponse)

fake = Faker()


@allure.parent_suite("Домен «Пользователи»")
@allure.suite("Изменение уровня прав пользователя")
@allure.sub_suite("Основные функциональные тесты изменения уровня прав пользователей")
class TestUsersPermissions:

    @pytest.mark.parametrize('before_test_user_has_administrator_permissions', [True, False], indirect=True)
    def test_successful_permissions_change(
            self, database, authorize_administrator, create_user, before_test_user_has_administrator_permissions
    ):
        # Описание кейса, подготовка параметров и тестовых данных
        if before_test_user_has_administrator_permissions is True:
            permission_action = "revoke"
            case_title_part = "понижение"
            case_description_part = "отзыва у пользователя"
            expected_administrator_permission_state_after_action = False
        elif before_test_user_has_administrator_permissions is False:
            permission_action = "grant"
            case_title_part = "повышение"
            case_description_part = "присвоения пользователю"
            expected_administrator_permission_state_after_action = True
        else:
            raise AssertionError("Incorrect set_initial_permission_level state!")

        allure.dynamic.title(f"Успешное {case_title_part} уровня прав пользователя")
        allure.dynamic.severity(severity_level=allure.severity_level.CRITICAL)
        allure.dynamic.description(
            f"Данный тест проверяет возможность {case_description_part} прав администратора приложения.\n\n"
            "При проведении теста проверяется:\n"
            "- Соответствие кода ответа ожидаемому\n"
            "- Соответствие структуры (модели) ответа ожидаемой\n"
            "- Корректность обновления признака наличия прав администратора в базе данных"
        )

        user_id = create_user.user_id
        res = requests.patch(
            url=FrVars.APP_HOST + f"/users/admin-permissions/{user_id}/{permission_action}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=200, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=UserPermissionsChangeSuccessfulResponse,
            data=res.json()
        )

        user_data_from_db = get_user_data_by_id(db=database, user_id=user_id)

        # Формируем строку с полным именем пользователя
        user_fullname = create_user.firstname
        if create_user.middlename is not None: user_fullname = user_fullname + f" {create_user.middlename}"
        user_fullname = user_fullname + f" {create_user.surname}"

        make_simple_assertion(
            expected_value=f"Administrator permissions for {user_fullname} is successfully changed",
            actual_value=serialized_response.status,
            assertion_name="Статусное сообщение в ответе содержит полное имя пользователя"
        )

        make_simple_assertion(
            expected_value=expected_administrator_permission_state_after_action,
            actual_value=user_data_from_db.is_admin,
            assertion_name="Значение признака наличия прав администратора в БД соответствует ожидаемому значению"
        )

        make_simple_assertion(
            expected_value=expected_administrator_permission_state_after_action,
            actual_value=serialized_response.is_admin,
            assertion_name="Значение признака наличия прав администратора в ответе на запрос соответствует ожидаемому "
                           "значению"
        )

    @allure.severity(severity_level=allure.severity_level.NORMAL)
    @pytest.mark.parametrize('before_test_user_has_administrator_permissions', [True, False], indirect=True)
    def test_repeated_permissions_change(
            self, database, authorize_administrator, create_user, before_test_user_has_administrator_permissions
    ):
        # Описание кейса, подготовка параметров и тестовых данных
        if before_test_user_has_administrator_permissions is False:
            permission_action = "revoke"
            case_title_part = "понижении"
            case_description_part = "отзыве у пользователя"
            expected_administrator_permission_state_after_action = False
        elif before_test_user_has_administrator_permissions is True:
            permission_action = "grant"
            case_title_part = "повышении"
            case_description_part = "присвоении пользователю"
            expected_administrator_permission_state_after_action = True
        else:
            raise AssertionError("Incorrect set_initial_permission_level state!")

        allure.dynamic.title(f"Отказ в повторном {case_title_part} уровня прав пользователя")
        allure.dynamic.description(
            f"Данный тест проверяет отказ в повторном {case_description_part} прав администратора приложения.\n\n"
            "При проведении теста проверяется:\n"
            "- Соответствие кода ответа ожидаемому\n"
            "- Соответствие структуры (модели) ответа ожидаемой\n"
            "- Отсутствие обновления признака наличия прав администратора в базе данных"
        )

        user_id = create_user.user_id
        res = requests.patch(
            url=FrVars.APP_HOST + f"/users/admin-permissions/{user_id}/{permission_action}",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=400, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        serialized_response = validate_response_model(
            model=UserPermissionsChangeBadRequestResponse,
            data=res.json()
        )

        user_data_from_db = get_user_data_by_id(db=database, user_id=user_id)

        make_simple_assertion(
            expected_value=expected_administrator_permission_state_after_action,
            actual_value=user_data_from_db.is_admin,
            assertion_name="Значение признака наличия прав администратора в БД не изменилось и соответствует значению "
                           "до отправки запроса"
        )

        if before_test_user_has_administrator_permissions is True:
            deny_reason = UserPermissionsChangeBadRequestReason.user_is_already_has_admin_permissions.value
        else:
            deny_reason = UserPermissionsChangeBadRequestReason.user_is_already_has_no_admin_permissions.value

        make_simple_assertion(
            expected_value=deny_reason,
            actual_value=serialized_response.description.value,
            assertion_name="Описание ошибки содержит причину отказа"
        )

    @allure.title("Запрет отзыва прав администратора у последнего администратора приложения")
    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @allure.description(
        "Данный тест проверяет отказ в отзыве прав администратора у пользователя, являющегося последним "
        "администратором приложения.\n\n"
        "При проведении теста проверяется:\n"
        "- Соответствие кода ответа ожидаемому\n"
        "- Соответствие структуры (модели) ответа ожидаемой\n"
        "- Неизменность признака наличия прав администратора в БД"
    )
    def test_last_administrator_permissions_revoke(
            self, database, authorize_administrator, revoke_all_administrators_permissions_except_default
    ):
        default_user_data = get_user_data_by_email(db=database, email=FrVars.APP_DEFAULT_USER_EMAIL)
        user_id = default_user_data.id
        res = requests.patch(
            url=FrVars.APP_HOST + f"/users/admin-permissions/{user_id}/revoke",
            headers={
                "Access-Token": authorize_administrator.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        validate_response_model(
            model=UserPermissionsChangeLastAdminErrorResponse,
            data=res.json()
        )

        user_data_from_db = get_user_data_by_id(db=database, user_id=user_id)

        make_simple_assertion(
            expected_value=True,
            actual_value=user_data_from_db.is_admin,
            assertion_name="Признак наличия прав администратора в БД не изменился и соответствует значению True"
        )


    @allure.severity(severity_level=allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("case", ['unauthorized_grant', 'unauthorized_revoke'])
    def test_permissions_change_without_administrator_permissions(
            self, database, create_and_authorize_user, revoke_all_administrators_permissions_except_default, case
    ):
        if case == 'unauthorized_grant':
            allure.dynamic.title("Запрет повышения уровня прав пользователем, не имеющим прав администратора")
            all_nonadmin_users_ids = get_all_nonadmin_users_ids(db=database)
            random_user_id = random.choice(all_nonadmin_users_ids)
            expected_user_permission_value_in_db_after_request=False
            permissions_action = 'grant'
            case_description = ("В данном варианте теста проверяется отказ при попытке повысить уровень прав случайному"
                                " пользователю без прав администратора, при отправке запроса от имени пользователя, "
                                "не имеющего прав администратора.")
        else:  # 'unauthorized_revoke'
            allure.dynamic.title("Запрет понижения уровня прав пользователем, не имеющим прав администратора")
            all_administrators_ids = get_all_administrators_ids(db=database)
            random_user_id = random.choice(all_administrators_ids)
            expected_user_permission_value_in_db_after_request = True
            permissions_action = 'revoke'
            case_description = ("В данном варианте теста проверяется отказ при попытке отзыва прав у случайного "
                                "администратора, при отправке запроса от имени пользователя, не имеющего прав "
                                "администратора.")

        allure.dynamic.description(
            "Данный тест проверяет отказ в изменении уровня прав пользователем, не имеющим на это полномочий.\n\n"
            f"{case_description}"
            "\n\nПри проведении теста проверяется:\n"
            "- Соответствие кода ответа ожидаемому\n"
            "- Соответствие структуры (модели) ответа ожидаемой\n"
            "- Неизменность признака наличия или отсутствия прав администратора в БД\n\n"
        )

        res = requests.patch(
            url=FrVars.APP_HOST + f"/users/admin-permissions/{random_user_id}/{permissions_action}",
            headers={
                "Access-Token": create_and_authorize_user.access_token
            }
        )
        attach_request_data_to_report(res)

        make_simple_assertion(expected_value=403, actual_value=res.status_code, assertion_name="Проверка кода ответа")

        validate_response_model(
            model=UserPermissionsChangeLackOfPermissionsErrorResponse,
            data=res.json()
        )

        user_data_from_db_after_request = get_user_data_by_id(db=database, user_id=random_user_id)

        make_simple_assertion(
            expected_value=expected_user_permission_value_in_db_after_request,
            actual_value=user_data_from_db_after_request.is_admin,
            assertion_name=f"Признак наличия прав администратора в БД не изменился и соответствует значению "
                           f"{expected_user_permission_value_in_db_after_request}"
        )
