import allure
import pytest
import requests

from data.framework_variables import FrameworkVariables as FrVars
from database.users import get_user_data_by_email
from helpers.allure_report import attach_request_data_to_report
from helpers.assertions import make_simple_assertion


@pytest.fixture
def before_test_user_has_administrator_permissions(
        database, authorize_administrator, create_user, request
) -> bool:
    """
    Данная фикстура обеспечивает подготовку тестовых данных путём приведения наличия прав администратора у пользователя
    к значению, определённому в параметре тестовой функции (с применением indirect-параметризации).

    :param database: Ссылка на фикстуру "database".
        Необходима для запроса уровня прав пользователя перед отправкой запроса на его изменение.
    :param authorize_administrator: Ссылка на фикстуру "variable_manager".
        Используется данной фикстурой, так как изменение уровня прав пользователя требует авторизации администратора.
    :param create_user: Ссылка на фикстуру "create_user".
        Используется данной фикстурой для получения данных созданного пользователя,
        уровень прав которого требуется изменить.
    :param request: Ссылка на объект вызова фикстуры, содержащий параметр, который определяет действие над уровнем
        прав пользователя. Ожидается, что в параметре будет передано значение с типом bool.
    :return: Ожидаемое значение признака наличия прав администратора у пользователя.
    """
    user_should_be_administrator = request.param
    user_already_has_correct_permissions_state = get_user_data_by_email(
        db=database,
        email=create_user.email
    ).is_admin

    if user_should_be_administrator != user_already_has_correct_permissions_state:
        with allure.step("Изменение уровня прав пользователя"):
            if user_should_be_administrator is True:
                action = "grant"
            elif user_should_be_administrator is False:
                action = "revoke"
            else:
                raise RuntimeError("Incorrect expected user permissions state!")

            res = requests.patch(
                url=FrVars.APP_HOST + f"/users/admin-permissions/{create_user.user_id}/{action}",
                headers={
                    "Access-Token": authorize_administrator.access_token
                }
            )
            attach_request_data_to_report(res)

            make_simple_assertion(
                expected_value=200,
                actual_value=res.status_code,
                assertion_name="Код ответа на запрос отзыва прав администратора у пользователя в фикстуре"
            )

    return user_should_be_administrator
